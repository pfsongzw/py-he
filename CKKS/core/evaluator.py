import mathematics
from primitives.ciphertext import Ciphertext
from primitives.plaintext import Plaintext
from operations.arithmetic import ArithmeticOperations
from operations.matrix_ops import MatrixOperations
from operations.rotation import RotationOperations
from operations.bootstrapping import BootstrappingOperations
from bootstrapping.context import CKKSBootstrappingContext


class CKKSEvaluator:
    """完整的CKKS同态运算器"""

    def __init__(self, params):
        self.degree = params.poly_degree
        self.big_modulus = params.big_modulus
        self.scaling_factor = params.scaling_factor
        self.boot_context = CKKSBootstrappingContext(params)
        self.crt_context = params.crt_context

        self.arithmetic = ArithmeticOperations(params, self.crt_context)
        self.matrix_ops = MatrixOperations(params, self.crt_context)
        self.rotation_ops = RotationOperations(params, self.crt_context)
        self.bootstrapping_ops = BootstrappingOperations(params, self.crt_context, self.boot_context)

    def add(self, ciph1, ciph2):
        """同态加法"""
        assert isinstance(ciph1, Ciphertext)
        assert isinstance(ciph2, Ciphertext)
        assert ciph1.scaling_factor == ciph2.scaling_factor, "缩放因子不相等"
        assert ciph1.modulus == ciph2.modulus, "模数不相等"

        return self.arithmetic.add(ciph1, ciph2)

    def add_plain(self, ciph, plain):
        """密文与明文加法"""
        assert isinstance(ciph, Ciphertext)
        assert isinstance(plain, Plaintext)
        assert ciph.scaling_factor == plain.scaling_factor, "缩放因子不相等"

        return self.arithmetic.add_plain(ciph, plain)

    def subtract(self, ciph1, ciph2):
        """同态减法"""
        assert isinstance(ciph1, Ciphertext)
        assert isinstance(ciph2, Ciphertext)
        assert ciph1.scaling_factor == ciph2.scaling_factor, "缩放因子不相等"
        assert ciph1.modulus == ciph2.modulus, "模数不相等"

        return self.arithmetic.subtract(ciph1, ciph2)

    def multiply(self, ciph1, ciph2, relin_key):
        """同态乘法"""
        assert isinstance(ciph1, Ciphertext)
        assert isinstance(ciph2, Ciphertext)
        assert ciph1.modulus == ciph2.modulus, "模数不相等"

        return self.arithmetic.multiply(ciph1, ciph2, relin_key)

    def multiply_plain(self, ciph, plain):
        """密文与明文乘法"""
        assert isinstance(ciph, Ciphertext)
        assert isinstance(plain, Plaintext)

        return self.arithmetic.multiply_plain(ciph, plain)

    def relinearize(self, relin_key, c0, c1, c2, new_scaling_factor, modulus):
        """重线性化"""
        return self.arithmetic.relinearize(relin_key, c0, c1, c2, new_scaling_factor, modulus)

    def rescale(self, ciph, division_factor):
        """重缩放"""
        return self.arithmetic.rescale(ciph, division_factor)

    def lower_modulus(self, ciph, division_factor):
        """降低模数"""
        return self.arithmetic.lower_modulus(ciph, division_factor)

    def switch_key(self, ciph, key):
        """密钥交换"""
        return self.rotation_ops.switch_key(ciph, key)

    def rotate(self, ciph, rotation, rot_key):
        """同态旋转"""
        return self.rotation_ops.rotate(ciph, rotation, rot_key)

    def conjugate(self, ciph, conj_key):
        """同态共轭"""
        return self.rotation_ops.conjugate(ciph, conj_key)

    def multiply_matrix_naive(self, ciph, matrix, rot_keys, encoder):
        """朴素矩阵乘法"""
        return self.matrix_ops.multiply_matrix_naive(ciph, matrix, rot_keys, encoder)

    def multiply_matrix(self, ciph, matrix, rot_keys, encoder):
        """快速矩阵乘法"""
        return self.matrix_ops.multiply_matrix(ciph, matrix, rot_keys, encoder)

    def create_constant_plain(self, const):
        """创建常数明文"""
        return self.bootstrapping_ops.create_constant_plain(const)

    def create_complex_constant_plain(self, const, encoder):
        """创建复数常数明文"""
        return self.bootstrapping_ops.create_complex_constant_plain(const, encoder)

    def coeff_to_slot(self, ciph, rot_keys, conj_key, encoder):
        """系数到槽位转换"""
        return self.bootstrapping_ops.coeff_to_slot(ciph, rot_keys, conj_key, encoder)

    def slot_to_coeff(self, ciph0, ciph1, rot_keys, encoder):
        """槽位到系数转换"""
        return self.bootstrapping_ops.slot_to_coeff(ciph0, ciph1, rot_keys, encoder)

    def exp_taylor(self, ciph, relin_key, encoder):
        """泰勒指数函数"""
        return self.bootstrapping_ops.exp_taylor(ciph, relin_key, encoder)

    def raise_modulus(self, ciph):
        """提升模数"""
        return self.bootstrapping_ops.raise_modulus(ciph)

    def exp(self, ciph, const, relin_key, encoder):
        """指数函数"""
        return self.bootstrapping_ops.exp(ciph, const, relin_key, encoder)

    def bootstrap(self, ciph, rot_keys, conj_key, relin_key, encoder):
        """完整自举操作"""
        return self.bootstrapping_ops.bootstrap(ciph, rot_keys, conj_key, relin_key, encoder)