"""完整的位操作实现"""

from math import log

def reverse_bits(value, width):
    """位反转"""
    binary_val = '{:0{width}b}'.format(value, width=width)
    return int(binary_val[::-1], 2)

def bit_reverse_vec(values):
    """向量位反转"""
    result = [0] * len(values)
    for i in range(len(values)):
        result[i] = values[reverse_bits(i, int(log(len(values), 2)))]
    return result