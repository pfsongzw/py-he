"""完整的系数到槽位转换实现"""

import mathematics
from primitives.ciphertext import Ciphertext
from primitives.plaintext import Plaintext
from mathematics.polynomial import Polynomial


class CoeffToSlotOperation:
    """完整的系数到槽位转换操作"""

    def __init__(self, params, crt_context, boot_context):
        self.params = params
        self.crt_context = crt_context
        self.boot_context = boot_context
        self.big_modulus = params.big_modulus
        self.scaling_factor = params.scaling_factor

    def apply(self, ciph, rot_keys, conj_key, encoder):
        """应用完整的系数到槽位转换"""
        # 第一部分矩阵变换
        s1 = self._multiply_matrix(ciph, self.boot_context.encoding_mat_conj_transpose0, rot_keys, encoder)
        s2 = self._conjugate(ciph, conj_key)
        s2 = self._multiply_matrix(s2, self.boot_context.encoding_mat_transpose0, rot_keys, encoder)
        ciph0 = self._add(s1, s2)

        # 缩放和重缩放
        constant = self._create_constant_plain(1 / self.params.poly_degree)
        ciph0 = self._multiply_plain(ciph0, constant)
        ciph0 = self._rescale(ciph0, self.scaling_factor)

        # 第二部分矩阵变换
        s1 = self._multiply_matrix(ciph, self.boot_context.encoding_mat_conj_transpose1, rot_keys, encoder)
        s2 = self._conjugate(ciph, conj_key)
        s2 = self._multiply_matrix(s2, self.boot_context.encoding_mat_transpose1, rot_keys, encoder)
        ciph1 = self._add(s1, s2)

        # 缩放和重缩放
        ciph1 = self._multiply_plain(ciph1, constant)
        ciph1 = self._rescale(ciph1, self.scaling_factor)

        return ciph0, ciph1

    def _multiply_matrix(self, ciph, matrix, rot_keys, encoder):
        """矩阵乘法实现"""
        from operations.matrix_ops import MatrixOperations
        matrix_ops = MatrixOperations(self.params, self.crt_context)
        return matrix_ops.multiply_matrix(ciph, matrix, rot_keys, encoder)

    def _conjugate(self, ciph, conj_key):
        """共轭操作实现"""
        from operations.rotation import RotationOperations
        rotation_ops = RotationOperations(self.params, self.crt_context)
        return rotation_ops.conjugate(ciph, conj_key)

    def _add(self, ciph1, ciph2):
        """加法操作实现"""
        from operations.arithmetic import ArithmeticOperations
        arithmetic_ops = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic_ops.add(ciph1, ciph2)

    def _multiply_plain(self, ciph, plain):
        """密文明文乘法实现"""
        from operations.arithmetic import ArithmeticOperations
        arithmetic_ops = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic_ops.multiply_plain(ciph, plain)

    def _rescale(self, ciph, division_factor):
        """重缩放实现"""
        from operations.arithmetic import ArithmeticOperations
        arithmetic_ops = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic_ops.rescale(ciph, division_factor)

    def _create_constant_plain(self, const):
        """创建常数明文"""
        plain_vec = [0] * self.params.poly_degree
        plain_vec[0] = int(const * self.scaling_factor)
        return Plaintext(Polynomial(self.params.poly_degree, plain_vec), self.scaling_factor)