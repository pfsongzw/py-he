"""完整的数论函数实现"""

import random
import sympy

def mod_exp(val, exp, modulus):
    """模幂运算"""
    return pow(int(val), int(exp), int(modulus))

def mod_inv(val, modulus):
    """模逆元"""
    return mod_exp(val, modulus - 2, modulus)

def find_generator(modulus):
    """寻找生成元"""
    return sympy.ntheory.primitive_root(modulus)

def root_of_unity(order, modulus):
    """寻找单位根"""
    if ((modulus - 1) % order) != 0:
        raise ValueError(f'必须满足 order | m-1, 其中 m={modulus}, q={order} 不满足条件')

    generator = find_generator(modulus)
    if generator is None:
        raise ValueError(f'在模 {modulus} 下没有原根')

    result = mod_exp(generator, (modulus - 1)//order, modulus)

    if result == 1:
        return root_of_unity(order, modulus)

    return result

def is_prime(number, num_trials=200):
    """素数测试"""
    if number < 2:
        return False
    if number != 2 and number % 2 == 0:
        return False

    exp = number - 1
    while exp % 2 == 0:
        exp //= 2

    for _ in range(num_trials):
        rand_val = int(random.SystemRandom().randrange(1, number))
        new_exp = exp
        power = pow(rand_val, new_exp, number)
        while new_exp != number - 1 and power != 1 and power != number - 1:
            power = (power * power) % number
            new_exp *= 2
        if power != number - 1 and new_exp % 2 == 0:
            return False

    return True