"""完整的自举操作实现"""

import math
from primitives.ciphertext import Ciphertext
from primitives.plaintext import Plaintext
from mathematics.polynomial import Polynomial


class BootstrappingOperations:
    """完整的自举操作"""

    def __init__(self, params, crt_context, boot_context):
        self.params = params
        self.crt_context = crt_context
        self.boot_context = boot_context
        self.big_modulus = params.big_modulus
        self.scaling_factor = params.scaling_factor

    def bootstrap(self, ciph, rot_keys, conj_key, relin_key, encoder):
        """完整自举流程"""
        # 保存原始状态
        old_modulus = ciph.modulus
        old_scaling_factor = self.scaling_factor

        # 提升模数
        self.raise_modulus(ciph)

        # 系数到槽位转换
        ciph0, ciph1 = self.coeff_to_slot(ciph, rot_keys, conj_key, encoder)

        # 指数函数评估
        const = self.scaling_factor / old_modulus * 2 * math.pi * 1j
        ciph_exp0 = self.exp(ciph0, const, relin_key, encoder)
        ciph_neg_exp0 = self.conjugate(ciph_exp0, conj_key)
        ciph_exp1 = self.exp(ciph1, const, relin_key, encoder)
        ciph_neg_exp1 = self.conjugate(ciph_exp1, conj_key)

        # 计算正弦
        ciph_sin0 = self.subtract(ciph_exp0, ciph_neg_exp0)
        ciph_sin1 = self.subtract(ciph_exp1, ciph_neg_exp1)

        # 缩放答案
        plain_const = self.create_complex_constant_plain(
            old_modulus / self.scaling_factor * 0.25 / math.pi / 1j, encoder)
        ciph0 = self.multiply_plain(ciph_sin0, plain_const)
        ciph1 = self.multiply_plain(ciph_sin1, plain_const)
        ciph0 = self.rescale(ciph0, self.scaling_factor)
        ciph1 = self.rescale(ciph1, self.scaling_factor)

        # 槽位到系数转换
        ciph = self.slot_to_coeff(ciph0, ciph1, rot_keys, encoder)

        # 恢复缩放因子
        self.scaling_factor = old_scaling_factor
        ciph.scaling_factor = self.scaling_factor

        print("------------ 自举模数变化 -------------")
        print(f"原始模数 q: {int(math.log(old_modulus, 2))} 位")
        print(f"提升模数 Q_0: {int(math.log(self.big_modulus, 2))} 位")
        print(f"最终模数 Q_1: {int(math.log(ciph.modulus, 2))} 位")

        return ciph

    def coeff_to_slot(self, ciph, rot_keys, conj_key, encoder):
        """系数到槽位转换"""
        s1 = self.multiply_matrix(ciph, self.boot_context.encoding_mat_conj_transpose0,
                                  rot_keys, encoder)
        s2 = self.conjugate(ciph, conj_key)
        s2 = self.multiply_matrix(s2, self.boot_context.encoding_mat_transpose0, rot_keys,
                                  encoder)
        ciph0 = self.add(s1, s2)
        constant = self.create_constant_plain(1 / self.params.poly_degree)
        ciph0 = self.multiply_plain(ciph0, constant)
        ciph0 = self.rescale(ciph0, self.scaling_factor)

        s1 = self.multiply_matrix(ciph, self.boot_context.encoding_mat_conj_transpose1,
                                  rot_keys, encoder)
        s2 = self.conjugate(ciph, conj_key)
        s2 = self.multiply_matrix(s2, self.boot_context.encoding_mat_transpose1, rot_keys,
                                  encoder)
        ciph1 = self.add(s1, s2)
        ciph1 = self.multiply_plain(ciph1, constant)
        ciph1 = self.rescale(ciph1, self.scaling_factor)

        return ciph0, ciph1

    def slot_to_coeff(self, ciph0, ciph1, rot_keys, encoder):
        """槽位到系数转换"""
        s1 = self.multiply_matrix(ciph0, self.boot_context.encoding_mat0, rot_keys,
                                  encoder)
        s2 = self.multiply_matrix(ciph1, self.boot_context.encoding_mat1, rot_keys,
                                  encoder)
        ciph = self.add(s1, s2)
        return ciph

    def exp_taylor(self, ciph, relin_key, encoder):
        """泰勒指数函数"""
        ciph2 = self.multiply(ciph, ciph, relin_key)
        ciph2 = self.rescale(ciph2, self.scaling_factor)

        ciph4 = self.multiply(ciph2, ciph2, relin_key)
        ciph4 = self.rescale(ciph4, self.scaling_factor)

        const = self.create_constant_plain(1)
        ciph01 = self.add_plain(ciph, const)

        const = self.create_constant_plain(1)
        ciph01 = self.multiply_plain(ciph01, const)
        ciph01 = self.rescale(ciph01, self.scaling_factor)

        const = self.create_constant_plain(3)
        ciph23 = self.add_plain(ciph, const)

        const = self.create_constant_plain(1 / 6)
        ciph23 = self.multiply_plain(ciph23, const)
        ciph23 = self.rescale(ciph23, self.scaling_factor)

        ciph23 = self.multiply(ciph23, ciph2, relin_key)
        ciph23 = self.rescale(ciph23, self.scaling_factor)
        ciph01 = self.lower_modulus(ciph01, self.scaling_factor)
        ciph23 = self.add(ciph23, ciph01)

        const = self.create_constant_plain(5)
        ciph45 = self.add_plain(ciph, const)

        const = self.create_constant_plain(1 / 120)
        ciph45 = self.multiply_plain(ciph45, const)
        ciph45 = self.rescale(ciph45, self.scaling_factor)

        const = self.create_constant_plain(7)
        ciph = self.add_plain(ciph, const)

        const = self.create_constant_plain(1 / 5040)
        ciph = self.multiply_plain(ciph, const)
        ciph = self.rescale(ciph, self.scaling_factor)

        ciph = self.multiply(ciph, ciph2, relin_key)
        ciph = self.rescale(ciph, self.scaling_factor)

        ciph45 = self.lower_modulus(ciph45, self.scaling_factor)
        ciph = self.add(ciph, ciph45)

        ciph = self.multiply(ciph, ciph4, relin_key)
        ciph = self.rescale(ciph, self.scaling_factor)

        ciph23 = self.lower_modulus(ciph23, self.scaling_factor)
        ciph = self.add(ciph, ciph23)

        return ciph

    def raise_modulus(self, ciph):
        """提升模数"""
        self.scaling_factor = ciph.modulus
        ciph.scaling_factor = self.scaling_factor
        ciph.modulus = self.big_modulus

    def exp(self, ciph, const, relin_key, encoder):
        """指数函数"""
        num_iterations = self.boot_context.num_taylor_iterations
        const_plain = self.create_complex_constant_plain(const / 2 ** num_iterations, encoder)
        ciph = self.multiply_plain(ciph, const_plain)
        ciph = self.rescale(ciph, self.scaling_factor)
        ciph = self.exp_taylor(ciph, relin_key, encoder)

        for _ in range(num_iterations):
            ciph = self.multiply(ciph, ciph, relin_key)
            ciph = self.rescale(ciph, self.scaling_factor)

        return ciph

    def create_constant_plain(self, const):
        """创建常数明文"""
        plain_vec = [0] * (self.params.poly_degree)
        plain_vec[0] = int(const * self.scaling_factor)
        return Plaintext(Polynomial(self.params.poly_degree, plain_vec), self.scaling_factor)

    def create_complex_constant_plain(self, const, encoder):
        """创建复数常数明文"""
        plain_vec = [const] * (self.params.poly_degree // 2)
        return encoder.encode(plain_vec, self.scaling_factor)

    # 辅助运算方法
    def add(self, ciph1, ciph2):
        from operations.arithmetic import ArithmeticOperations
        arithmetic = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic.add(ciph1, ciph2)

    def add_plain(self, ciph, plain):
        from operations.arithmetic import ArithmeticOperations
        arithmetic = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic.add_plain(ciph, plain)

    def subtract(self, ciph1, ciph2):
        from operations.arithmetic import ArithmeticOperations
        arithmetic = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic.subtract(ciph1, ciph2)

    def multiply(self, ciph1, ciph2, relin_key):
        from operations.arithmetic import ArithmeticOperations
        arithmetic = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic.multiply(ciph1, ciph2, relin_key)

    def multiply_plain(self, ciph, plain):
        from operations.arithmetic import ArithmeticOperations
        arithmetic = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic.multiply_plain(ciph, plain)

    def rescale(self, ciph, division_factor):
        from operations.arithmetic import ArithmeticOperations
        arithmetic = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic.rescale(ciph, division_factor)

    def lower_modulus(self, ciph, division_factor):
        from operations.arithmetic import ArithmeticOperations
        arithmetic = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic.lower_modulus(ciph, division_factor)

    def conjugate(self, ciph, conj_key):
        from operations.rotation import RotationOperations
        rotation = RotationOperations(self.params, self.crt_context)
        return rotation.conjugate(ciph, conj_key)

    def multiply_matrix(self, ciph, matrix, rot_keys, encoder):
        from operations.matrix_ops import MatrixOperations
        matrix_ops = MatrixOperations(self.params, self.crt_context)
        return matrix_ops.multiply_matrix(ciph, matrix, rot_keys, encoder)