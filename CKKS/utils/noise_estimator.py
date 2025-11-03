"""完整的噪声估计器"""

import math


class NoiseEstimator:
    """噪声估计器"""

    def __init__(self, params):
        self.params = params

    def estimate_initial_noise(self):
        """估计初始噪声"""
        return math.sqrt(self.params.poly_degree / 12.0)

    def estimate_addition_noise(self, noise1, noise2):
        """加法噪声估计"""
        return math.sqrt(noise1 ** 2 + noise2 ** 2)

    def estimate_multiplication_noise(self, noise1, noise2):
        """乘法噪声估计"""
        poly_degree = self.params.poly_degree
        term1 = noise1 * noise2 * poly_degree
        term2 = noise1 * math.sqrt(poly_degree / 3.0)
        term3 = noise2 * math.sqrt(poly_degree / 3.0)
        term4 = poly_degree / 3.0

        return math.sqrt(term1 ** 2 + term2 ** 2 + term3 ** 2 + term4 ** 2)

    def can_perform_operation(self, current_noise, operation_type):
        """检查是否可以执行操作"""
        max_noise = self.params.ciph_modulus / (2 * self.params.scaling_factor)

        if operation_type == "addition":
            expected_noise = current_noise * math.sqrt(2)
        elif operation_type == "multiplication":
            expected_noise = self.estimate_multiplication_noise(current_noise, current_noise)
        else:
            expected_noise = current_noise

        return expected_noise < max_noise * 0.8

    def should_bootstrap(self, current_noise):
        """检查是否应该自举"""
        critical_noise = self.params.ciph_modulus / (8 * self.params.scaling_factor)
        return current_noise > critical_noise