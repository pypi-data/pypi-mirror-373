# -*- coding: utf-8 -*-
"""
Created on Sat Jun 28 20:45:13 2025

@author: balazs
"""
import math
import sys
import types
import tempfile


n = 4

def make_float_t(n, verbose = False):
    source = f'''
import taichi as ti
from mpmath import mp, mpf
from taichi_big_float.mantissa_n32 import make_mantissa_n32

m = make_mantissa_n32({n})

mp.prec = {32*n}


# error flags:
    # 1 << 1: impossible outcome
    # 1 << 2: zero division
    # 1 << 3: unhandled case of f32 underflow in division
    

float_t = ti.types.vector({n+2}, ti.u32)

@ti.real_func
def neg(a: ti.types.vector({n+2}, ti.u32)) -> float_t:
    ret = a
    if a[{n}] == 0:
        ret[{n}] = ti.u32(1) | a[{n}]
    else:
        ret[{n}] = ti.u32(0) | (a[{n}] & ti.u32(0xfffffffe))
    return ret

@ti.real_func
def equalize_exp(v10: ti.types.vector({n+2}, ti.u32), 
                 v20: ti.types.vector({n+2}, ti.u32)) -> [float_t, float_t]:
    ret1 = ti.Vector([0]*{n+2}, ti.u32)
    ret2 = ti.Vector([0]*{n+2}, ti.u32)
    
    v1, v2 = v10, v20
    
    cond1 = m.eq(v10, ret1)
    cond2 = m.eq(v20, ret1)
    
    if cond1 and cond2:
        v1[{n+1}] = ti.u32(0x80000000)
        v2[{n+1}] = ti.u32(0x80000000)
    elif cond1:
        v1[{n+1}] = 0
    elif cond2:
        v2[{n+1}] = 0
    
    if v1[{n+1}] == v2[{n+1}]:
        ret1, ret2 = v1, v2
    elif v1[{n+1}] > v2[{n+1}]:
        exp = v1[{n+1}]
        shift = exp - v2[{n+1}]
        mant = m.bit_shift_down(v2, shift)
        
        ret1 = v1
        ret2 = mant
        ret2[{n}] = v2[{n}]
        ret2[{n+1}] = exp
    else:
        exp = v2[{n+1}]
        shift = exp - v1[{n+1}]
        mant = m.bit_shift_down(v1, shift)
        
        ret2 = v2
        ret1 = mant
        ret1[{n}] = v1[{n}]
        ret1[{n+1}] = exp
    return [ret1, ret2]

@ti.real_func 
def normalize(a: ti.types.vector({n+2}, ti.u32)) -> float_t:
    shift_limb = m.leading_zero_limbs(a)
    ret = a
    
    if shift_limb < {n}:
        shift_bit = 31-m.log2_u32(a[{n-1}-shift_limb])
        # print(a[3-shift_limb], log2_u32(a[{n-1}-shift_limb]))
        
        if shift_bit != 0:
            ret = m.bit_shift_up_simple(ret, shift_bit)
        
        if shift_limb != 0:
            ret = m.limb_shift_up(ret, shift_limb)
        ret[{n+1}] = a[{n+1}] - shift_limb*32 - shift_bit 
    
    ret[{n}] = a[{n}]
    
    return ret

@ti.real_func
def add(self0: float_t, other0: float_t) -> float_t:
    self, other = equalize_exp(self0, other0)
    ret = ti.Vector([0]*{n+2}, ti.u32)
    
    if self[{n}]%2 == other[{n}]%2:
        ret, of = m.add_hi(self, other)
        ret[{n}] = self[{n}] | other[{n}]
        ret[{n+1}] = self[{n+1}]
        if of:
            ret[{n+1}] += 32

    elif self[{n}]%2 == 1 and other[{n}]%2 == 0:
        ret = m.sub(other, self)
        
        ret[{n+1}] = self[{n+1}]
        
        if m.gt(self, other):
            ret[{n}] = ti.u32(1) | self[{n}] | other[{n}]
        else:
            ret[{n}] = ti.u32(0) | (self[{n}] & ti.u32(0xfffffffe)) | (other[{n}] & ti.u32(0xfffffffe))
    
    elif other[{n}]%2 == 1 and self[{n}]%2 == 0:
        ret = m.sub(self, other)
        
        ret[{n+1}] = self[{n+1}]
        
        if m.gt(other, self):
            ret[{n}] = ti.u32(1) | self[{n}] | other[{n}]
        else:
            ret[{n}] = ti.u32(0) | (self[{n}] & ti.u32(0xfffffffe)) | (other[{n}] & ti.u32(0xfffffffe))
    else:
        ret[{n}] = ti.u32(1 << 1)
    
    
    # print(ret)
    ret = normalize(ret)
    return ret

@ti.real_func 
def sub(self0: float_t, other0: float_t) -> float_t:
    self, other = equalize_exp(self0, other0)
    # print(self, other)
    ret = ti.Vector([0]*{n+2}, ti.u32)
    
    if self[{n}]%2 != other[{n}]%2:
        ret, of = m.add_hi(self, other)
        ret[{n}] = self[{n}] | (other[{n}] & ti.u32(0xfffffffe))
        ret[{n+1}] = self[{n+1}]
        if of:
            ret[{n+1}] += 32 
    else:
        ret = m.sub(self, other)
        
        if m.gt(other, self):
            ret[{n}] = ti.u32(1)
        else:
            ret[{n}] = ti.u32(0)
        
        ret[{n}] ^= self[{n}]%2
        ret[{n}] |= (self[{n}] & ti.u32(0xfffffffe)) | (other[{n}] & ti.u32(0xfffffffe))
        ret[{n+1}] = self[{n+1}]
        
        # print(ret)
        # print(normalize(ret))
    
    ret = normalize(ret)
    return ret

@ti.real_func 
def mul(self: float_t, other: float_t) -> float_t:
    ret, of = m.mul_hi(self, other)
    # print(ret, of)
    ret[{n+1}] = (self[{n+1}] & ti.u32(0x7fffffff)) + (other[{n+1}] & ti.u32(0x7fffffff))
    if (self[{n+1}] & ti.u32(0x80000000)) == (other[{n+1}] & ti.u32(0x80000000)):
        ret[{n+1}] ^= ti.u32(0x80000000)
    ret[{n+1}] += of
    ret[{n}] = ti.u32(self[{n}] != other[{n}]) | ((self[{n}] | other[{n}]) & ti.u32(0xfffffffe))
    
    return ret

@ti.real_func
def f32_to_float(f: ti.f32) -> float_t:
    exp = ti.u32(0)
    exp0 = -ti.i32(ti.math.log2((2**24-1)/abs(f)))
    mant = ti.u32(abs(f) / ti.pow(ti.f32(2.0), exp0))
    sgn = ti.u32(f != abs(f))
    
    ret = m.un32()
    ret[0] = mant
    ret[{n}] = sgn
    if exp0 >= 0:
        exp = ti.u32(exp0)
        ret[{n+1}] = ti.u32(0x80000000) | ti.u32(exp)
    else:
        exp = ti.u32(-exp0)
        ret[{n+1}] = ti.u32(0x80000000) - exp 
    return normalize(ret)

@ti.real_func
def float_to_f32(a: ti.types.vector({n+2}, ti.u32)) -> ti.f32:
    mant = a[{n-1}] >> 8
    exp = ti.i32(0)
    if a[{n+1}] > ti.u32(0x80000000):
        exp = ti.i32(a[{n+1}] - ti.u32(0x80000000)) + {n*32} - 24
    else:
        exp = -ti.i32(ti.u32(0x80000000) - a[{n+1}]) + {n*32} - 24
    sgn = a[{n}]%2
    
    ret = ti.f32(mant * ti.pow(ti.f32(2.0), exp))
    if sgn:
        ret *= -1
    
    return ret

@ti.real_func 
def div(self:float_t, other:float_t) -> float_t:
    zero = ti.Vector([0]*{n+2}, ti.u32)
    ret = ti.Vector([0]*{n+2}, ti.u32)
    # tmp1 = ti.Vector([0]*{n+2}, ti.u32)
    # tmp2 = ti.Vector([0]*{n+2}, ti.u32)
    # tmp3 = ti.Vector([0]*{n+2}, ti.u32)
    
    if not m.eq(other, zero):
        o_f32 = float_to_f32(other)
        o_inv = i32_to_float(0)#normalize(ti.Vector([0,0,0,0,0,ti.u32(0x80000000)], ti.u32))
        if o_f32 != 0:
            o_inv = f32_to_float(1/float_to_f32(other))
        else:
            o_inv[{n}] |= 1 << 3
        two = i32_to_float(2)#normalize(ti.Vector([2,0,0,0,0,ti.u32(0x80000000)], ti.u32))
        # print(float_to_f32(two))
        # print(two)
        
        ti.loop_config(serialize=True)
        for i in range({math.ceil(math.log2(n*32))}):
            # print(float_to_f32(o_inv), float_to_f32(mul(other, o_inv)), float_to_f32(sub(two, mul(other, o_inv))), float_to_f32(mul(o_inv, sub(two, mul(other, o_inv)))))
            o_inv = mul(o_inv, sub(two, mul(other, o_inv)))
        
        ret = mul(self, o_inv)
    else:
        ret = ti.Vector([ti.u32(0xffffffff)]*{n+2}, ti.u32)
        ret[{n}] = ti.u32(1) if self[{n}]%2 != other[{n}]%2 else ti.u32(0)
        ret[{n}] |= (self[{n}] & ti.u32(0xfffffffe)) | (other[{n}] & ti.u32(0xfffffffe))
        ret[{n}] |= 1 << 2
        ret[{n+1}] = ti.u32(0xfffeffff)
    
    return ret

@ti.real_func 
def cmp(self: float_t, other: float_t) -> ti.i32:
    v1, v2 = equalize_exp(self, other)
    return m.cmp(v1, v2)

@ti.real_func 
def gt(self: float_t, other: float_t) -> ti.i32:
    return cmp(self, other) == 1
@ti.real_func 
def eq(self: float_t, other: float_t) -> ti.i32:
    return cmp(self, other) == 0
@ti.real_func 
def lt(self: float_t, other: float_t) -> ti.i32:
    return cmp(self, other) == -1
@ti.real_func 
def ge(self: float_t, other: float_t) -> ti.i32:
    v = cmp(self, other) 
    return v == 1 or v == 0
@ti.real_func 
def le(self: float_t, other: float_t) -> ti.i32:
    v = cmp(self, other) 
    return v == -1 or v == 0

@ti.real_func 
def i32_to_float(val: ti.i32) -> float_t:
    ret = ti.Vector([0]*{n+2}, ti.u32)
    ret[0] = ti.u32(abs(val))
    if val < 0:
        ret[{n}] = ti.u32(1)
    else:
        ret[{n}] = ti.u32(0)
    ret[{n+1}] = ti.u32(0x80000000)
    return normalize(ret)

def str_to_float(val: str):
    x = mpf(val)
    sign = 0 if x >= 0 else 1
    x = abs(x)
    
    m, e = mp.frexp(x)
    
    mantissa = int(m * (1 << {n*32}))
    mantissa_u32 = [(mantissa >> (32 * i)) & 0xFFFFFFFF for i in range({n})]
    mantissa_u32.append(sign)
    mantissa_u32.append(0x80000000 + e - {n*32})
    

    return ti.Vector(mantissa_u32, ti.u32)
    
'''

    if verbose:
        print(source)
    
    # with open('float320.py', 'w') as f:
    #     f.write(source)
    #     temp_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(source)
        temp_path = f.name
    
    code = compile(source, temp_path, 'exec')
    
    mod = types.ModuleType(f'float_t_{n}')
    sys.modules[f'float_t_{n}'] = mod

    exec(code, mod.__dict__)
    return mod