"""完整的中国剩余定理实现"""

import mathematics.number_theory as nbtheory
from mathematics.ntt import NTTContext


class CRTContext:
    """完整的CRT上下文"""

    def __init__(self, num_primes, prime_size, poly_degree):
        self.poly_degree = poly_degree
        self.generate_primes(num_primes, prime_size, mod=2 * poly_degree)
        self.generate_ntt_contexts()

        self.modulus = 1
        for prime in self.primes:
            self.modulus *= prime

        self.precompute_crt()

    def generate_primes(self, num_primes, prime_size, mod):
        """生成素数"""
        self.primes = [1] * num_primes
        possible_prime = (1 << prime_size) + 1
        for i in range(num_primes):
            possible_prime += mod
            while not nbtheory.is_prime(possible_prime):
                possible_prime += mod
            self.primes[i] = possible_prime

    def generate_ntt_contexts(self):
        """生成NTT上下文"""
        self.ntts = []
        for prime in self.primes:
            ntt = NTTContext(self.poly_degree, prime)
            self.ntts.append(ntt)

    def precompute_crt(self):
        """CRT预计算"""
        num_primes = len(self.primes)
        self.crt_vals = [1] * num_primes
        self.crt_inv_vals = [1] * num_primes
        for i in range(num_primes):
            self.crt_vals[i] = self.modulus // self.primes[i]
            self.crt_inv_vals[i] = nbtheory.mod_inv(self.crt_vals[i], self.primes[i])

    def crt(self, value):
        """CRT表示"""
        return [value % p for p in self.primes]

    def reconstruct(self, values):
        """CRT重构"""
        assert len(values) == len(self.primes)
        regular_rep_val = 0

        for i in range(len(values)):
            intermed_val = (values[i] * self.crt_inv_vals[i]) % self.primes[i]
            intermed_val = (intermed_val * self.crt_vals[i]) % self.modulus
            regular_rep_val += intermed_val
            regular_rep_val %= self.modulus

        return regular_rep_val