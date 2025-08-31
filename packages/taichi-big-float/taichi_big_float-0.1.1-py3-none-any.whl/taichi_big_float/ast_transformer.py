# -*- coding: utf-8 -*-
"""
Created on Sat Jul 19 21:41:49 2025

@author: balazs
"""

import ast
import inspect
import textwrap
import tempfile
import importlib.util
from typing import get_type_hints
import pickle
import taichi_big_float.float_n32_p2 as bigfloat
import taichi as ti

def resolve_annotation(anotation_node, globals_dict):
    try:
        if isinstance(anotation_node, ast.Name): #example: f192_t
            return eval(anotation_node.id, globals_dict)
        elif isinstance(anotation_node, ast.Call): #example: ti.types.ndarray(dtype=f192_t, ndim = 3)
            src = ast.unparse(anotation_node)
            return eval(src, globals_dict).dtype
        elif isinstance(anotation_node, ast.Attribute): #example: float192.f192_t
            src = ast.unparse(anotation_node)
            return eval(src, globals_dict)
        # elif isinstance(anotation_node, ast.List): #example: [f192_t, f192_t]
        #     lst = [resolve_annotation(node, globals_dict) for node in anotation_node.elts]
        #     return lst
    except:
        pass
    return None

def replace_type_annotation(node, replacements):
    """Recursively replace known type annotations (AST) using replacements dict."""
    if isinstance(node, ast.Name) and node.id in replacements:
        return replacements[node.id]
    
    if isinstance(node, ast.Attribute) and node.attr in replacements:
        return replacements[node.attr]

    if isinstance(node, ast.Call):
        new_func = replace_type_annotation(node.func, replacements)
        new_args = [replace_type_annotation(arg, replacements) for arg in node.args]
        return ast.Call(func=new_func, args=new_args, keywords=node.keywords)

    return node


class TypeAnnotator(ast.NodeVisitor):
    def __init__(self, globals_dict=None):
        self.env = {}  # variable name -> type descriptor
        self.globals_dict = globals_dict if globals_dict is not None else globals()
        self.known_return_types = {
            # 'f192': ty.f192_t,
            # 'f32_to_f192': ty.f32_to_f192,
            # 'i32_to_f192': ty.i32_to_f192
        }

    def visit_FunctionDef(self, node):
        for arg in node.args.args:
            if arg.annotation:
                t = resolve_annotation(arg.annotation, self.globals_dict)
                self.env[arg.arg] = t
        
        if node.returns:
            node.inferred_type = resolve_annotation(node.returns, self.globals_dict)
        self.generic_visit(node)

    # def visit_AnnAssign(self, node):
    #     if isinstance(node.target, ast.Name):
    #         var_name = node.target.id
    #         t = resolve_annotation(node.annotation, self.globals_dict)
    #         self.env[var_name] = t
    #         node.inferred_type = t
    #     self.generic_visit(node)

    def visit_Assign(self, node):
        self.visit(node.value)
        inferred = getattr(node.value, 'inferred_type', None)
        for target in node.targets:
            if isinstance(target, ast.Name) and inferred:
                self.env[target.id] = inferred
                target.inferred_type = inferred
            elif isinstance(target, ast.Tuple) and inferred:
                assert isinstance(inferred, list), 'Tuple unpack assign must be annotated with a list of types e.g. [f192_t, f192_t]'
                for elt, it in zip(target.elts, inferred):
                    if isinstance(elt, ast.Name):
                        self.env[elt.id] = it
                        elt.inferred_type = it
                    elif isinstance(elt, ast.Attribute):
                        elt_id = ast.unparse(elt)
                        self.env[elt_id] = it
                        elt.inferred_type = it
            elif isinstance(target, ast.Attribute) and inferred:
                target_id = ast.unparse(target)
                self.env[target_id] = inferred
                target.inferred_type = inferred

    def visit_Name(self, node):
        t = self.env.get(node.id)
        if t:
            node.inferred_type = t
    
    def visit_Attribute(self, node):
        node_id = ast.unparse(node)
        t = self.env.get(node_id)
        if t:
            node.inferred_type = t

    def visit_Call(self, node):
        self.generic_visit(node)

        func_id = None
        if isinstance(node.func, ast.Name):
            func_id = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_id = ast.unparse(node.func)

        # Case 1: Known hardcoded return types
        if func_id in self.known_return_types:
            node.inferred_type = self.known_return_types[func_id]
            return node

        # Case 2: Use get_type_hints
        func_obj = eval(ast.unparse(node.func), self.globals_dict)
        if func_obj is not None:
            try:
                hints = get_type_hints(func_obj, globalns=self.globals_dict)
                ret_type = hints.get('return')
                if ret_type:
                    node.inferred_type = ret_type
            except Exception:
                pass

        return node

    def visit_Subscript(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name):
            base = node.value.id
            node.inferred_type = self.env.get(base)
        elif isinstance(node.value, ast.Attribute):
            base = ast.unparse(node.value)
            node.inferred_type = self.env.get(base)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        ltype = getattr(node.left, 'inferred_type', None)
        rtype = getattr(node.right, 'inferred_type', None)
        if ltype == rtype and ltype is not None:
            node.inferred_type = ltype

def cmp_types(tp, target_tp):
    if isinstance(tp, ti.lang.matrix.VectorType) and isinstance(target_tp, ti.lang.matrix.VectorType):
        return tp.dtype == target_tp.dtype and tp.n == target_tp.n
    else:
        return tp == target_tp

class Transformer(ast.NodeTransformer):
    def __init__(self, target_type, op_map, cmp_map):
        self.target_type = target_type
        self.op_map = op_map
        self.cmp_map = cmp_map

    def visit_BinOp(self, node):
        self.generic_visit(node)

        ltype = getattr(node.left, 'inferred_type', None)
        rtype = getattr(node.right, 'inferred_type', None)
        op_type = type(node.op)

        if cmp_types(ltype, self.target_type) and cmp_types(rtype, self.target_type) and op_type in self.op_map:
            func_name = self.op_map[op_type].__name__

            new_node = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='ty', ctx=ast.Load()),
                    attr=func_name,
                    ctx=ast.Load()),
                args=[node.left, node.right],
                keywords=[]
            )
            new_node.inferred_type = self.target_type
            return new_node

        return node
    
    def visit_Compare(self, node):
        assert len(node.ops) == 1, "Chained comparisons not supported for f192"
        
        op = node.ops[0]
        left = self.visit(node.left)
        right = self.visit(node.comparators[0])
        
        ltype = getattr(left, 'inferred_type', None)
        rtype = getattr(right, 'inferred_type', None)
        op_type = type(op)
        
        if cmp_types(ltype, self.target_type) and cmp_types(rtype, self.target_type) and op_type in self.cmp_map:
            func_name = self.cmp_map[op_type].__name__

            new_node = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='ty', ctx=ast.Load()),
                    attr=func_name,
                    ctx=ast.Load()),
                args=[left, right],
                keywords=[]
            )
            new_node.inferred_type = bool
            return new_node

        return node

def supports_bigfloat(globals_dict, n=4, verbose=False):
    ty = bigfloat.make_float_t(n)
    globals_dict |= {'ty': ty}
    def supports_bigfloat_base(fn):
        transformer = Transformer(ty.float_t, 
                                  {ast.Add: ty.add,
                                   ast.Sub: ty.sub,
                                   ast.Mult: ty.mul,
                                   ast.Div: ty.div},
                                  {ast.Gt: ty.gt,
                                   ast.Lt: ty.lt,
                                   ast.Eq: ty.eq,
                                   ast.GtE: ty.ge,
                                   ast.LtE: ty.le})
        annotator = TypeAnnotator(globals_dict)
        
        source = textwrap.dedent(inspect.getsource(fn))
        tree = ast.parse(source)
        annotator.visit(tree)
        
        tree.body[0].decorator_list = []

        # Transform function (annotations, ops, etc.)
        tree = transformer.visit(tree)
        ast.fix_missing_locations(tree)

        # Get unparsed Python code
        transformed_source = ast.unparse(tree)
        
        imports = f'''
import taichi_big_float.float_n32_p2 as bigfloat
ty = bigfloat.make_float_t({n})

'''

        # Write to a temporary .py file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(imports + transformed_source)
            temp_path = f.name
            
            if verbose:
                print(imports + transformed_source)
        
        global_ns = fn.__globals__.copy()
        local_ns = {}
        
        code = compile(imports + transformed_source, temp_path, 'exec')
        exec(code, globals()|global_ns, local_ns)
        ret_fnc = local_ns[fn.__name__]

        # Load as Python module
        # spec = importlib.util.spec_from_file_location("temp_module", temp_path)
        # module = importlib.util.module_from_spec(spec)
        # spec.loader.exec_module(module)
        
        # ret_fnc = getattr(module, fn.__name__)
        
        return ret_fnc
    return supports_bigfloat_base