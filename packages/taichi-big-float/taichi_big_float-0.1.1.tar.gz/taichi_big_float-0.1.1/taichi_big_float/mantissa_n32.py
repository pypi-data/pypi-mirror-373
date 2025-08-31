# -*- coding: utf-8 -*-
"""
Created on Sat Jun 28 20:27:53 2025

@author: balazs
"""

import types
import sys
import tempfile

def make_mantissa_n32(n, verbose = False):
    source = f'''

import taichi as ti


vec_{n+2} = ti.types.vector({n+2}, ti.u32)
vec{n*2} = ti.types.vector({n*2}, ti.u16)

@ti.real_func 
def add_with_carry(a: ti.u32,
                   b: ti.u32,
                   carry_in: ti.u32) -> [ti.u32, ti.u32]:
    temp = ti.u32(a+b)
    result = temp + carry_in
    carry_out = ti.u32((temp < a) or (result < temp))
    
    return [result, carry_out]

@ti.real_func 
def add_full(a: ti.types.vector({n+2}, ti.u32),
                  b: ti.types.vector({n+2}, ti.u32)) -> [vec_{n+2}, ti.u32]:
    
    result = ti.Vector([0]*{n+2}, ti.u32)
    
    carry = ti.u32(0)
    ti.loop_config(serialize=True)
    for i in range({n}):
        x = a[i]
        y = b[i]
        tmp = add_with_carry(x, y, carry)
        sum_ = tmp[0]
        new_carry = tmp[1]
        result[i] = sum_
        carry = new_carry
    
    return [result, carry]

@ti.real_func 
def add_hi(a: ti.types.vector({n+2}, ti.u32),
                b: ti.types.vector({n+2}, ti.u32)) -> [vec_{n+2}, ti.i32]:
    result = ti.Vector([0]*{n+2}, ti.u32)
    overflow = False
    
    tmp = add_full(a, b)
    res = tmp[0]
    carry = tmp[1]
    
    if carry:
        overflow = True
        for i in range({n-1}):
            result[i] = res[i+1]
        result[{n-1}] = carry 
    else:
        for i in range({n}):
            result[i] = res[i]
    
    return [result, overflow]


@ti.real_func 
def neg(a: ti.types.vector({n+2}, ti.u32)) -> vec_{n+2}:
    result = ti.Vector([0]*{n+2}, ti.u32)
    
    for i in range({n}):
        result[i] = ti.u32(0xffffffff)-a[i]
    # print(result)
    k = 0
    carry = ti.u32(1)
    while carry:
        temp = result[k]
        # print(temp, carry)
        temp, carry = add_with_carry(temp, carry, 0)
        # print(temp, carry)
        result[k] = temp
        k += 1
    return result

@ti.real_func 
def sub(a: ti.types.vector({n+2}, ti.u32),
             b: ti.types.vector({n+2}, ti.u32)) -> vec_{n+2}:
    
    res, carry  = add_full(a, neg(b))
    ret = res
    
    if not carry:
        ret = neg(res)
    return ret

@ti.real_func 
def from_u32_to_u16(a: ti.types.vector({n+2}, ti.u32)) -> vec{n*2}:
    ret = ti.Vector([0]*{n*2}, ti.u16)
    
    for i in range({n}):
        hi = ti.u16(a[i] >> 16)
        lo = ti.u16(a[i] & 0xffff)
        
        ret[2*i] = lo
        ret[2*i + 1] = hi
    
    return ret

@ti.real_func 
def from_u16_to_u32(a: ti.types.vector({n*2}, ti.u16)) -> vec_{n+2}:
    ret = ti.Vector([0]*{n+2}, ti.u32)
    
    for i in range({n}):
        hi = ti.u32(a[2*i+1])
        lo = ti.u32(a[2*i])
        
        ret[i] = (hi << 16) | lo
    
    return ret

@ti.real_func 
def mul_u16impl(a: ti.types.vector({n*2}, ti.u16),
                     b: ti.types.vector({n*2}, ti.u16)) -> (vec{n*2}, vec{n*2}):
    result = ti.Vector([0]*{4*n}, ti.u16)
    hi = ti.Vector([0]*{n*2}, ti.u16)
    lo = ti.Vector([0]*{n*2}, ti.u16)
    
    ti.loop_config(serialize=True)
    for i in range({n*2}):
        # ti.loop_config(serialize=True)
        for j in range({n*2}):
            tmp = ti.u32(ti.u32(a[i])*ti.u32(b[j]))
            high = tmp >> 16
            low = tmp & 0xffff
            
            temp = ti.u32(result[i+j]) + low
            carry = temp >> 16
            temp &= 0xffff
            result[i+j] = ti.u16(temp)
            
            temp = ti.u32(result[i+j+1]) + high + carry
            carry = temp >> 16
            temp &= 0xffff
            result[i+j+1] = ti.u16(temp)
            
            k = 2
            while carry:
                temp = ti.u32(result[i+j+k]) + carry
                carry = temp >> 16
                temp &= 0xffff
                result[i+j+k] = ti.u16(temp)
                k += 1
    
    for i in range({n*2}):
        hi[i] = result[i+{n*2}]
        lo[i] = result[i]
    
    return hi, lo

@ti.real_func 
def mul_full(a: ti.types.vector({n+2}, ti.u32),
                  b: ti.types.vector({n+2}, ti.u32)) -> (vec_{n+2}, vec_{n+2}):
    
    a16 = from_u32_to_u16(a)
    b16 = from_u32_to_u16(b)
    
    hi16, lo16 = mul_u16impl(a16, b16)
    
    hi = from_u16_to_u32(hi16)
    lo = from_u16_to_u32(lo16)
    
    return hi, lo

@ti.real_func 
def mul_un32_lo(a: ti.types.vector({n+2}, ti.u32),
                b: ti.types.vector({n+2}, ti.u32)) -> vec_{n+2}:
    
    return mul_full(a, b)[1]

@ti.real_func 
def leading_zero_limbs(a: ti.types.vector({n+2}, ti.u32)) -> ti.i32:
    ret = 0
    flag = True 
    
    ti.loop_config(serialize=True)
    for j in range({n}):
        i = {n-1}-j
        if a[i] == 0 and flag:
            ret += 1
        else:
            flag = False
    return ret

@ti.real_func
def log2_u32(x: ti.u32) -> ti.i32:
    low = 0
    high = 31
    
    while low <= high:
        mid = (low + high) // 2
        if x >> mid == 0:
            high = mid - 1
        else:
            low = mid + 1
    return high

@ti.real_func 
def mul_hi(a: ti.types.vector({n+2}, ti.u32),
                b: ti.types.vector({n+2}, ti.u32)) -> [vec_{n+2}, ti.i32]:
    hi, lo = mul_full(a, b)
    # print(hi, lo)
    shift_limb = leading_zero_limbs(hi)
    shift_bit = 0
    
    if shift_limb < {n}:
        shift_bit = 31-log2_u32(hi[{n-1}-shift_limb])
        # print(shift_limb, shift_bit)
        
        # print(hi)
        hi = bit_shift_up_simple(hi, shift_bit)
        # print(hi)
        hi[0] |= lo[{n-1}] >> (32-shift_bit)
        # lo = bit_shift_up_simple(lo, shift_bit)
        
        hi = limb_shift_up(hi, shift_limb)
        # print(hi)
        for i in range(shift_limb):
            hi[i] = lo[{n}-shift_limb+i]
    else:
        shift_limb -= {n}
        shift_bit = 31-log2_u32(hi[{n-1}-shift_limb])
        
        hi = bit_shift_up_simple(lo, shift_bit)
        hi = limb_shift_up(hi, shift_limb)
    
    return [hi, {n*32}-shift_limb*32-shift_bit]

@ti.real_func 
def bit_shift_up_simple(a: ti.types.vector({n+2}, ti.u32), shift: ti.u32) -> vec_{n+2}:
    result = ti.Vector([0]*{n+2}, ti.u32)
    if shift > 0:
        result = ti.Vector([0]*{n+2}, ti.u32)
        high, low = ti.u32(0), ti.u32(0)
        
        ti.loop_config(serialize=True)
        for i in range({n}):
            low = (a[i] << shift) | high
            high = a[i] >> (32-shift)
            result[i] = low
    else:
        result = ti.Vector([a[i] for i in range({n+2})], ti.u32)
    return result

@ti.real_func 
def limb_shift_up(a: ti.types.vector({n+2}, ti.u32), n: ti.int32) -> vec_{n+2}:
    result = ti.Vector([0]*{n+2}, ti.u32)
    for i in range({n}-n):
        result[i+n] = a[i]
    return result

@ti.real_func
def bit_shift_up(a: ti.types.vector({n+2}, ti.u32), shift: ti.int32) -> vec_{n+2}:
    n = shift//32 
    shift %= 32 
    result = ti.Vector([a[i] for i in range({n})])
    if shift:
        result = bit_shift_up_simple(a, shift)
    
    if n:
        result = limb_shift_up(result, n)
    
    return  result


@ti.real_func 
def bit_shift_down_simple(a: ti.types.vector({n+2}, ti.u32), shift: ti.int32) -> vec_{n+2}:
    result = ti.Vector([0]*{n+2}, ti.u32)
    high, low = ti.u32(0), ti.u32(0)
    
    ti.loop_config(serialize=True)
    for j in range({n}):
        i = {n-1}-j
        
        low = (a[i] >> shift) | high
        high = a[i] << (32-shift)
        
        result[i] = low
    return result

@ti.real_func 
def limb_shift_down(a: ti.types.vector({n+2}, ti.u32), n: ti.int32) -> vec_{n+2}:
    result = ti.Vector([0]*{n+2}, ti.u32)
    for j in range({n}-n):
        i = {n-1}-j
        
        result[i-n] = a[i]
    return result

@ti.real_func
def bit_shift_down(a: ti.types.vector({n+2}, ti.u32), shift0: ti.i32) -> vec_{n+2}:
    n = shift0//32 
    shift = shift0%32 
    
    result = ti.Vector([a[i] for i in range({n+2})])
    if shift:
        result = bit_shift_down_simple(a, shift)
    
    if n:
        result = limb_shift_down(result, n)
    
    return  result

@ti.real_func
def cmp(a: ti.types.vector({n+2}, ti.u32), b: ti.types.vector({n+2}, ti.u32)) -> ti.i32:
    ret = 0
    
    ti.loop_config(serialize=True)
    for j in range({n}):
        i = {n-1}-j
        if not ret:
            if a[i] < b[i]:
                ret = -1
            elif a[i] > b[i]:
                ret = 1
    return ret

@ti.real_func
def lt(a: ti.types.vector({n+2}, ti.u32), b: ti.types.vector({n+2}, ti.u32)) -> ti.i32:
    return cmp(a, b) == -1
@ti.real_func
def gt(a: ti.types.vector({n+2}, ti.u32), b: ti.types.vector({n+2}, ti.u32)) -> ti.i32:
    return cmp(a, b) == 1
@ti.real_func
def eq(a: ti.types.vector({n+2}, ti.u32), b: ti.types.vector({n+2}, ti.u32)) -> ti.i32:
    return cmp(a, b) == 0

@ti.real_func 
def un32() -> vec_{n+2}:
    return ti.Vector([0]*{n+2}, ti.u32)

@ti.real_func 
def leading_zero_limbs_u16impl(a: ti.types.vector({2*n+2}, ti.u16)) -> ti.i32:
    ret = 0
    flag = True 
    ti.loop_config(serialize=True)
    for j in range({2*n+2}):
        i = {n*2+1}-j
        if a[i] == 0 and flag:
            ret += 1
        else:
            flag = False
    return ret

@ti.real_func 
def bit_shift_up_simple_u16impl(a: ti.types.vector({2*n+2}, ti.u16), shift: ti.i32) -> ti.types.vector({2*n+2}, ti.u16):
    result = ti.Vector([0]*{2*n+2}, ti.u16)
    high, low = ti.u16(0), ti.u16(0)
    
    ti.loop_config(serialize=True)
    for i in range({2*n+2}):
        low = (a[i] << shift) | high
        high = a[i] >> (16-shift)
        result[i] = low
    return result

@ti.real_func 
def bit_shift_down_simple_u16impl(a: ti.types.vector({2*n+2}, ti.u16), shift: ti.i32) -> ti.types.vector({2*n+2}, ti.u16):
    result = ti.Vector([0]*{2*n+2}, ti.u16)
    high, low = ti.u16(0), ti.u16(0)
    
    ti.loop_config(serialize=True)
    for j in range({2*n+2}):
        i = {n*2+1}-j
        
        low = (a[i] >> shift) | high
        high = a[i] << (16-shift)
        
        result[i] = low
    return result

@ti.real_func
def cmp_u16impl(a: ti.types.vector({2*n+2}, ti.u16), b: ti.types.vector({2*n+2}, ti.u16)) -> ti.i32:
    ret = 0
    
    ti.loop_config(serialize=True)
    for j in range({2*n+2}):
        i = {n*2+1}-j
        if not ret:
            if a[i] < b[i]:
                ret = -1
            elif a[i] > b[i]:
                ret = 1
    return ret

@ti.real_func 
def mul_u16impl_82(a: ti.types.vector({2*n+2}, ti.u16),
                        b: ti.types.vector({2*n+2}, ti.u16)) -> ti.types.vector({2*n+2}, ti.u16):
    result = ti.Vector([0]*{2*n+2}, ti.u16)
    
    ti.loop_config(serialize=True)
    for i in range({n*2}):
        # ti.loop_config(serialize=True)
        for j in range(2):
            tmp = ti.u32(ti.u32(a[i])*ti.u32(b[j]))
            high = tmp >> 16
            low = tmp & 0xffff
            
            temp = ti.u32(result[i+j]) + low
            carry = temp >> 16
            temp &= 0xffff
            result[i+j] = ti.u16(temp)
            
            temp = ti.u32(result[i+j+1]) + high + carry
            carry = temp >> 16
            temp &= 0xffff
            result[i+j+1] = ti.u16(temp)
    
    return result

@ti.real_func 
def extend_by_digit(q: ti.types.vector({2*n+2}, ti.u16),
                    q_hat: ti.types.vector({2*n+2}, ti.u16)) -> ti.types.vector({2*n+2}, ti.u16):
    ret = ti.Vector([0]*{2*n+2}, ti.u16)
    ret[0] = q_hat[0]
    
    carry = ti.u32(q_hat[1])
    ti.loop_config(serialize=True)
    for i in range({n*2+1}):
        tmp = ti.u32(q[i]) + carry
        tmp_hi = tmp >> 16
        tmp_lo = tmp & 0xffff
        
        ret[i+1] = ti.u16(tmp_lo)
        carry = tmp_hi
    
    return ret

@ti.real_func 
def sub_u16impl(a: ti.types.vector({2*n+2}, ti.u16), b: ti.types.vector({2*n+2}, ti.u16)) -> ti.types.vector({2*n+2}, ti.u16):
    ret = ti.Vector([0]*{2*n+2}, ti.u16)
    
    carry = 0
    ti.loop_config(serialize=True)
    for i in range({2*n+2}):
        tmp = ti.i32(a[i]) - carry - ti.i32(b[i])
        
        if tmp < 0:
            carry = 1
            ret[i] = ti.u16(2**16+tmp)
        else:
            carry = 0 
            ret[i] = ti.u16(tmp)
    
    return ret

@ti.real_func
def divmod(a: ti.types.vector({n+2}, ti.u32), 
                b: ti.types.vector({n+2}, ti.u32)) -> (vec_{n+2}, vec_{n+2}, ti.i32):
    zero_devision = True
    for i in range({n}):
        if b[i]:
            zero_devision = False
    
    q_retu32 = un32()
    r_retu32 = un32()
    
    if not zero_devision:
        a_norm = ti.Vector([0]*{2*n+2}, ti.u16)
        b_norm = ti.Vector([0]*{2*n+2}, ti.u16)
        
        a_tmp = from_u32_to_u16(a)
        b_tmp = from_u32_to_u16(b)
        
        for i in range({n*2}):
            a_norm[i] = a_tmp[i]
            b_norm[i] = b_tmp[i]
        
        one = ti.Vector([0]*{n*2}, ti.u16)
        one[0] = ti.u16(1)
        shift = leading_zero_limbs_u16impl(b_norm)
        back_shift = False
        
        b_hat = ti.u32(b_norm[{n*2+1}-shift])
        
        norm = 0
        if b_hat < 2**15:
            norm = 15 - log2_u32(b_hat)
            a_norm = bit_shift_up_simple_u16impl(a_norm, norm)
            b_norm = bit_shift_up_simple_u16impl(b_norm, norm)
            back_shift = True
        shift = leading_zero_limbs_u16impl(b_norm)
        shift_a = min(leading_zero_limbs_u16impl(a_norm), shift-1)
        b_hat = ti.u32(b_norm[{n*2+1}-shift])
        
        q = ti.Vector([0]*{2*n+2}, ti.u16)
        q_hat_vec = ti.Vector([0]*{2*n+2}, ti.u16)
        r = ti.Vector([0]*{2*n+2}, ti.u16)
        dig_rem = ti.Vector([0]*{2*n+2}, ti.u16)
        
        for i in range({2*n+2}-shift+shift_a+1):
            r[i] = a_norm[i+shift-shift_a-1]
        for i in range(shift-shift_a-1):
            dig_rem[i] = a_norm[i]
        
        i = 0
        while True:            
            a_hat = ti.u32(r[{2*n+2}-shift])*2**16 + ti.u32(r[{n*2+1}-shift])
            
            q_hat = a_hat//b_hat
            q_hat_hi = q_hat >> 16
            q_hat_lo = q_hat & 0xffff
            q_hat_vec[0] = ti.u16(q_hat_lo)
            q_hat_vec[1] = ti.u16(q_hat_hi)
            
            count = 0
            tmp = mul_u16impl_82(b_norm, q_hat_vec)
            while cmp_u16impl(tmp, r) == 1:
                q_hat -= 1
                q_hat_hi = q_hat >> 16
                q_hat_lo = q_hat & 0xffff
                q_hat_vec[0] = ti.u16(q_hat_lo)
                q_hat_vec[1] = ti.u16(q_hat_hi)
                count += 1
                tmp = mul_u16impl_82(b_norm, q_hat_vec)
            
            q = extend_by_digit(q, q_hat_vec)
            
            r = sub_u16impl(r, tmp)
            if shift-shift_a-2-i >= 0:
                r_new = ti.Vector([0]*{2*n+2}, ti.u16)
                r_new[0] = dig_rem[shift-shift_a-2-i]
                
                for j in range({n*2+1}):
                    r_new[j+1] = r[j]
                
                r = r_new
            else:
                break
            
            i += 1
        
        if back_shift:
            r = bit_shift_down_simple_u16impl(r, norm)
        
        q_ret = ti.Vector([q[i] for i in range({n*2})], ti.u16)
        r_ret = ti.Vector([r[i] for i in range({n*2})], ti.u16)
        
        q_retu32 = from_u16_to_u32(q_ret)
        r_retu32 = from_u16_to_u32(r_ret)
    else:
        q_retu32 = ti.Vector([ti.u32(0xffffffff)]*7, ti.u32)
        r_retu32 = ti.Vector([ti.u32(0xffffffff)]*7, ti.u32)

    return q_retu32, r_retu32, zero_devision

'''

    if verbose:
        print(source)
    
    # with open('mantissa256.py', 'w') as f:
    #     f.write(source)
    #     temp_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(source)
        temp_path = f.name
    
    code = compile(source, temp_path, 'exec')
    
    mod = types.ModuleType(f'mantissa_32_{n}')
    sys.modules[f'mantissa_32_{n}'] = mod

    exec(code, mod.__dict__)
    return mod
    
