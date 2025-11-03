"""完整的随机采样实现"""

import random

def sample_uniform(min_val, max_val, num_samples):
    """均匀分布采样"""
    if num_samples == 1:
        return random.randrange(min_val, max_val)
    return [random.randrange(min_val, max_val) for _ in range(num_samples)]

def sample_triangle(num_samples):
    """三角形分布采样"""
    sample = [0] * num_samples
    for i in range(num_samples):
        r = random.randrange(0, 4)
        if r == 0:
            sample[i] = -1
        elif r == 1:
            sample[i] = 1
        else:
            sample[i] = 0
    return sample

def sample_hamming_weight_vector(length, hamming_weight):
    """汉明权重向量采样"""
    sample = [0] * length
    total_weight = 0

    while total_weight < hamming_weight:
        index = random.randrange(0, length)
        if sample[index] == 0:
            r = random.randint(0, 1)
            if r == 0:
                sample[index] = -1
            else:
                sample[index] = 1
            total_weight += 1

    return sample

def sample_random_complex_vector(length):
    """随机复数向量采样"""
    sample = [0] * length
    for i in range(length):
        a = random.random()
        b = random.random()
        sample[i] = a + b * 1j
    return sample

def sample_random_real_vector(length):
    """随机实数向量采样"""
    sample = [0] * length
    for i in range(length):
        sample[i] = random.random()
    return sample