"""完整的矩阵运算实现"""

from math import log, sqrt
from primitives.ciphertext import Ciphertext
from primitives.plaintext import Plaintext
from mathematics.polynomial import Polynomial


class MatrixOperations:
    """完整的矩阵运算"""

    def __init__(self, params, crt_context):
        self.params = params
        self.crt_context = crt_context
        self.scaling_factor = params.scaling_factor

    def multiply_matrix_naive(self, ciph, matrix, rot_keys, encoder):
        """朴素矩阵乘法"""
        diag = self.diagonal(matrix, 0)
        diag_plain = encoder.encode(diag, self.scaling_factor)
        ciph_prod = self._multiply_plain(ciph, diag_plain)

        for j in range(1, len(matrix)):
            diag = self.diagonal(matrix, j)
            diag_plain = encoder.encode(diag, self.scaling_factor)
            rot = self._rotate(ciph, j, rot_keys[j])
            ciph_temp = self._multiply_plain(rot, diag_plain)
            ciph_prod = self._add(ciph_prod, ciph_temp)

        return ciph_prod

    def multiply_matrix(self, ciph, matrix, rot_keys, encoder):
        """快速矩阵乘法"""
        matrix_len = len(matrix)
        matrix_len_factor1 = int(sqrt(matrix_len))
        if matrix_len != matrix_len_factor1 * matrix_len_factor1:
            matrix_len_factor1 = int(sqrt(2 * matrix_len))
        matrix_len_factor2 = matrix_len // matrix_len_factor1

        ciph_rots = [0] * matrix_len_factor1
        ciph_rots[0] = ciph
        for i in range(1, matrix_len_factor1):
            ciph_rots[i] = self._rotate(ciph, i, rot_keys[i])

        outer_sum = None
        for j in range(matrix_len_factor2):
            inner_sum = None
            shift = matrix_len_factor1 * j
            for i in range(matrix_len_factor1):
                diagonal = self.diagonal(matrix, shift + i)
                diagonal = self.rotate_vector(diagonal, -shift)
                diagonal_plain = encoder.encode(diagonal, self.scaling_factor)
                dot_prod = self._multiply_plain(ciph_rots[i], diagonal_plain)
                if inner_sum:
                    inner_sum = self._add(inner_sum, dot_prod)
                else:
                    inner_sum = dot_prod

            rotated_sum = self._rotate(inner_sum, shift, rot_keys[shift])
            if outer_sum:
                outer_sum = self._add(outer_sum, rotated_sum)
            else:
                outer_sum = rotated_sum

        outer_sum = self._rescale(outer_sum, self.scaling_factor)
        return outer_sum

    def diagonal(self, mat, diag_index):
        """获取矩阵对角线"""
        return [mat[j % len(mat)][(diag_index + j) % len(mat)] for j in range(len(mat))]

    def rotate_vector(self, vec, rotation):
        """旋转向量"""
        return [vec[(j + rotation) % len(vec)] for j in range(len(vec))]

    def conjugate_matrix(self, matrix):
        """矩阵共轭"""
        conj_matrix = [[0] * len(matrix[i]) for i in range(len(matrix))]
        for i, row in enumerate(matrix):
            for j in range(len(row)):
                conj_matrix[i][j] = matrix[i][j].conjugate()
        return conj_matrix

    def transpose_matrix(self, matrix):
        """矩阵转置"""
        transpose = [[0] * len(matrix) for _ in range(len(matrix[0]))]
        for i, row in enumerate(matrix):
            for j in range(len(row)):
                transpose[j][i] = matrix[i][j]
        return transpose

    def _multiply_plain(self, ciph, plain):
        """密文明文乘法"""
        c0 = ciph.c0.multiply(plain.poly, ciph.modulus, crt=self.crt_context)
        c0 = c0.mod_small(ciph.modulus)
        c1 = ciph.c1.multiply(plain.poly, ciph.modulus, crt=self.crt_context)
        c1 = c1.mod_small(ciph.modulus)
        return Ciphertext(c0, c1, ciph.scaling_factor * plain.scaling_factor, ciph.modulus)

    def _add(self, ciph1, ciph2):
        """密文加法"""
        c0 = ciph1.c0.add(ciph2.c0, ciph1.modulus).mod_small(ciph1.modulus)
        c1 = ciph1.c1.add(ciph2.c1, ciph1.modulus).mod_small(ciph1.modulus)
        return Ciphertext(c0, c1, ciph1.scaling_factor, ciph1.modulus)

    def _rotate(self, ciph, rotation, rot_key):
        """密文旋转"""
        rot_ciph0 = ciph.c0.rotate(rotation)
        rot_ciph1 = ciph.c1.rotate(rotation)
        rot_ciph = Ciphertext(rot_ciph0, rot_ciph1, ciph.scaling_factor, ciph.modulus)
        return self._switch_key(rot_ciph, rot_key.key)

    def _switch_key(self, ciph, key):
        """密钥交换"""
        c0 = key.p0.multiply(ciph.c1, ciph.modulus * self.params.big_modulus, crt=self.crt_context)
        c0 = c0.mod_small(ciph.modulus * self.params.big_modulus)
        c0 = c0.scalar_integer_divide(self.params.big_modulus)
        c0 = c0.add(ciph.c0, ciph.modulus).mod_small(ciph.modulus)

        c1 = key.p1.multiply(ciph.c1, ciph.modulus * self.params.big_modulus, crt=self.crt_context)
        c1 = c1.mod_small(ciph.modulus * self.params.big_modulus)
        c1 = c1.scalar_integer_divide(self.params.big_modulus)
        c1 = c1.mod_small(ciph.modulus)

        return Ciphertext(c0, c1, ciph.scaling_factor, ciph.modulus)

    def _rescale(self, ciph, division_factor):
        """重缩放"""
        c0 = ciph.c0.scalar_integer_divide(division_factor)
        c1 = ciph.c1.scalar_integer_divide(division_factor)
        return Ciphertext(c0, c1, ciph.scaling_factor // division_factor,
                          ciph.modulus // division_factor)