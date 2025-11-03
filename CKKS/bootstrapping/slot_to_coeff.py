"""完整的槽位到系数转换实现"""

from primitives.ciphertext import Ciphertext
from primitives.plaintext import Plaintext
from mathematics.polynomial import Polynomial


class SlotToCoeffOperation:
    """完整的槽位到系数转换操作"""

    def __init__(self, params, crt_context, boot_context):
        self.params = params
        self.crt_context = crt_context
        self.boot_context = boot_context
        self.scaling_factor = params.scaling_factor

    def apply(self, ciph0, ciph1, rot_keys, encoder):
        """应用完整的槽位到系数转换"""
        # 第一部分矩阵变换
        s1 = self._multiply_matrix(ciph0, self.boot_context.encoding_mat0, rot_keys, encoder)

        # 第二部分矩阵变换
        s2 = self._multiply_matrix(ciph1, self.boot_context.encoding_mat1, rot_keys, encoder)

        # 合并结果
        ciph = self._add(s1, s2)

        return ciph

    def _multiply_matrix(self, ciph, matrix, rot_keys, encoder):
        """矩阵乘法实现"""
        from operations.matrix_ops import MatrixOperations
        matrix_ops = MatrixOperations(self.params, self.crt_context)
        return matrix_ops.multiply_matrix(ciph, matrix, rot_keys, encoder)

    def _add(self, ciph1, ciph2):
        """加法操作实现"""
        from operations.arithmetic import ArithmeticOperations
        arithmetic_ops = ArithmeticOperations(self.params, self.crt_context)
        return arithmetic_ops.add(ciph1, ciph2)