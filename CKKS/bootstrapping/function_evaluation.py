"""完整的函数评估实现"""

import math
import cmath
from primitives.ciphertext import Ciphertext
from primitives.plaintext import Plaintext
from mathematics.polynomial import Polynomial


class FunctionEvaluation:
    """完整的函数评估操作"""

    def __init__(self, params, crt_context):
        self.params = params
        self.crt_context = crt_context
        self.scaling_factor = params.scaling_factor
        self.big_modulus = params.big_modulus

    def evaluate_exponential(self, ciph, const, relin_key, encoder, num_iterations=None):
        """完整的指数函数评估"""
        if num_iterations is None:
            num_iterations = self.params.num_taylor_iterations

        const_plain = self._create_complex_constant_plain(const / (2 ** num_iterations), encoder)
        ciph = self._multiply_plain(ciph, const_plain)
        ciph = self._rescale(ciph, self.scaling_factor)

        # 泰勒展开评估
        ciph_exp = self._evaluate_exp_taylor(ciph, relin_key, encoder)

        # 重复平方
        for _ in range(num_iterations):
            ciph_exp = self._multiply(ciph_exp, ciph_exp, relin_key)
            ciph_exp = self._rescale(ciph_exp, self.scaling_factor)

        return ciph_exp

    def evaluate_sine(self, ciph, const, relin_key, encoder):
        """完整的正弦函数评估"""
        # 使用欧拉公式: sin(x) = (e^(ix) - e^(-ix)) / (2i)
        const_pos = const * 1j  # i * const
        const_neg = -const * 1j  # -i * const

        ciph_exp_pos = self.evaluate_exponential(ciph, const_pos, relin_key, encoder)
        ciph_exp_neg = self.evaluate_exponential(ciph, const_neg, relin_key, encoder)

        ciph_sin = self._subtract(ciph_exp_pos, ciph_exp_neg)

        # 除以 2i
        scaling_constant = self._create_complex_constant_plain(1 / (2j), encoder)
        ciph_sin = self._multiply_plain(ciph_sin, scaling_constant)
        ciph_sin = self._rescale(ciph_sin, self.scaling_factor)

        return ciph_sin

    def evaluate_cosine(self, ciph, const, relin_key, encoder):
        """完整的余弦函数评估"""
        # 使用欧拉公式: cos(x) = (e^(ix) + e^(-ix)) / 2
        const_pos = const * 1j  # i * const
        const_neg = -const * 1j  # -i * const

        ciph_exp_pos = self.evaluate_exponential(ciph, const_pos, relin_key, encoder)
        ciph_exp_neg = self.evaluate_exponential(ciph, const_neg, relin_key, encoder)

        ciph_cos = self._add(ciph_exp_pos, ciph_exp_neg)

        # 除以 2
        scaling_constant = self._create_constant_plain(0.5)
        ciph_cos = self._multiply_plain(ciph_cos, scaling_constant)
        ciph_cos = self._rescale(ciph_cos, self.scaling_factor)

        return ciph_cos

    def _evaluate_exp_taylor(self, ciph, relin_key, encoder):
        """泰勒级数指数函数评估"""
        # e^x ≈ 1 + x + x^2/2! + x^3/3! + x^4/4! + x^5/5! + x^6/6! + x^7/7!

        result = self._create_constant_plain(1.0)

        # x 项
        result = self._add(result, ciph)

        # x^2/2! 项
        x2 = self._multiply(ciph, ciph, relin_key)
        x2 = self._rescale(x2, self.scaling_factor)
        x2_scaled = self._multiply_plain(x2, self._create_constant_plain(0.5))
        x2_scaled = self._rescale(x2_scaled, self.scaling_factor)
        result = self._add(result, x2_scaled)

        # x^3/6 项
        x3 = self._multiply(x2, ciph, relin_key)
        x3 = self._rescale(x3, self.scaling_factor)
        x3_scaled = self._multiply_plain(x3, self._create_constant_plain(1 / 6))
        x3_scaled = self._rescale(x3_scaled, self.scaling_factor)
        result = self._add(result, x3_scaled)

        # x^4/24 项
        x4 = self._multiply(x2, x2, relin_key)
        x4 = self._rescale(x4, self.scaling_factor)
        x4_scaled = self._multiply_plain(x4, self._create_constant_plain(1 / 24))
        x4_scaled = self._rescale(x4_scaled, self.scaling_factor)
        result = self._add(result, x4_scaled)

        return result

    def _create_constant_plain(self, const):
        """创建实数常数明文"""
        plain_vec = [0] * self.params.poly_degree
        plain_vec[0] = int(const * self.scaling_factor)
        return Plaintext(Polynomial(self.params.poly_degree, plain_vec), self.scaling_factor)

    def _create_complex_constant_plain(self, const, encoder):
        """创建复数常数明文"""
        plain_vec = [const] * (self.params.poly_degree // 2)
        return encoder.encode(plain_vec, self.scaling_factor)

    def _multiply(self, ciph1, ciph2, relin_key):
        """同态乘法"""
        from operations.arithmetic import ArithmeticOperations
        arithmetic_ops = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic_ops.multiply(ciph1, ciph2, relin_key)

    def _multiply_plain(self, ciph, plain):
        """密文明文乘法"""
        from operations.arithmetic import ArithmeticOperations
        arithmetic_ops = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic_ops.multiply_plain(ciph, plain)

    def _add(self, ciph1, ciph2):
        """同态加法"""
        from operations.arithmetic import ArithmeticOperations
        arithmetic_ops = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic_ops.add(ciph1, ciph2)

    def _subtract(self, ciph1, ciph2):
        """同态减法"""
        from operations.arithmetic import ArithmeticOperations
        arithmetic_ops = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic_ops.subtract(ciph1, ciph2)

    def _rescale(self, ciph, division_factor):
        """重缩放"""
        from operations.arithmetic import ArithmeticOperations
        arithmetic_ops = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic_ops.rescale(ciph, division_factor)