import math
from operations.matrix_ops import MatrixOperations


class CKKSBootstrappingContext:
    """完整的自举上下文"""

    def __init__(self, params):
        self.poly_degree = params.poly_degree
        self.old_modulus = params.ciph_modulus
        self.num_taylor_iterations = params.num_taylor_iterations
        self.generate_encoding_matrices()

    def get_primitive_root(self, index):
        """获取本原根"""
        angle = math.pi * index / self.poly_degree
        return complex(math.cos(angle), math.sin(angle))

    def generate_encoding_matrices(self):
        """生成编码矩阵"""
        num_slots = self.poly_degree // 2
        primitive_roots = [0] * num_slots
        power = 1

        for i in range(num_slots):
            primitive_roots[i] = self.get_primitive_root(power)
            power = (power * 5) % (2 * self.poly_degree)

        # 计算槽位到系数变换矩阵
        self.encoding_mat0 = [[1] * num_slots for _ in range(num_slots)]
        self.encoding_mat1 = [[1] * num_slots for _ in range(num_slots)]

        for i in range(num_slots):
            for k in range(1, num_slots):
                self.encoding_mat0[i][k] = self.encoding_mat0[i][k - 1] * primitive_roots[i]

        for i in range(num_slots):
            self.encoding_mat1[i][0] = self.encoding_mat0[i][-1] * primitive_roots[i]

        for i in range(num_slots):
            for k in range(1, num_slots):
                self.encoding_mat1[i][k] = self.encoding_mat1[i][k - 1] * primitive_roots[i]

        # 计算系数到槽位变换矩阵
        self.encoding_mat_transpose0 = MatrixOperations.transpose_matrix(self.encoding_mat0)
        self.encoding_mat_conj_transpose0 = MatrixOperations.conjugate_matrix(self.encoding_mat_transpose0)
        self.encoding_mat_transpose1 = MatrixOperations.transpose_matrix(self.encoding_mat1)
        self.encoding_mat_conj_transpose1 = MatrixOperations.conjugate_matrix(self.encoding_mat_transpose1)