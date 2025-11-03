import math
from mathematics.crt import CRTContext


class CKKSParameters:
    """完整的CKKS参数配置"""

    def __init__(self, poly_degree, ciph_modulus, big_modulus, scaling_factor,
                 taylor_iterations=6, prime_size=59, hamming_weight=None):
        self.poly_degree = poly_degree
        self.ciph_modulus = ciph_modulus
        self.big_modulus = big_modulus
        self.scaling_factor = scaling_factor
        self.num_taylor_iterations = taylor_iterations
        self.prime_size = prime_size
        self.hamming_weight = hamming_weight if hamming_weight else poly_degree // 4
        self.crt_context = self._create_crt_context()

    def _create_crt_context(self):
        """创建CRT上下文"""
        if self.prime_size:
            num_primes = 1 + int((1 + math.log(self.poly_degree, 2) +
                                  4 * math.log(self.big_modulus, 2)) / self.prime_size)
            return CRTContext(num_primes, self.prime_size, self.poly_degree)
        return None

    def print_parameters(self):
        """打印完整参数信息"""
        print("CKKS完整参数配置:")
        print(f"  多项式度数: {self.poly_degree}")
        print(f"  密文模数: {self.ciph_modulus} (2^{int(math.log(self.ciph_modulus, 2))})")
        print(f"  大模数: {self.big_modulus} (2^{int(math.log(self.big_modulus, 2))})")
        print(f"  缩放因子: {self.scaling_factor} (2^{int(math.log(self.scaling_factor, 2))})")
        print(f"  泰勒迭代次数: {self.num_taylor_iterations}")
        print(f"  汉明权重: {self.hamming_weight}")
        print(f"  素数大小: {self.prime_size}位")
        print(f"  RNS支持: {'是' if self.crt_context else '否'}")