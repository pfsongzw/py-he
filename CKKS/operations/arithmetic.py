"""完整的算术运算实现"""

import math
from primitives.ciphertext import Ciphertext
from primitives.plaintext import Plaintext
from mathematics.polynomial import Polynomial


class ArithmeticOperations:
    """完整的算术运算"""

    def __init__(self, params, crt_context):
        self.params = params
        self.crt_context = crt_context
        self.big_modulus = params.big_modulus

    def add(self, ciph1, ciph2):
        """同态加法"""
        modulus = ciph1.modulus

        c0 = ciph1.c0.add(ciph2.c0, modulus)
        c0 = c0.mod_small(modulus)
        c1 = ciph1.c1.add(ciph2.c1, modulus)
        c1 = c1.mod_small(modulus)

        return Ciphertext(c0, c1, ciph1.scaling_factor, modulus)

    def add_plain(self, ciph, plain):
        """密文与明文加法"""
        c0 = ciph.c0.add(plain.poly, ciph.modulus)
        c0 = c0.mod_small(ciph.modulus)
        return Ciphertext(c0, ciph.c1, ciph.scaling_factor, ciph.modulus)

    def subtract(self, ciph1, ciph2):
        """同态减法"""
        modulus = ciph1.modulus

        c0 = ciph1.c0.subtract(ciph2.c0, modulus)
        c0 = c0.mod_small(modulus)
        c1 = ciph1.c1.subtract(ciph2.c1, modulus)
        c1 = c1.mod_small(modulus)

        return Ciphertext(c0, c1, ciph1.scaling_factor, modulus)

    def multiply(self, ciph1, ciph2, relin_key):
        """同态乘法"""
        modulus = ciph1.modulus

        c0 = ciph1.c0.multiply(ciph2.c0, modulus, crt=self.crt_context)
        c0 = c0.mod_small(modulus)

        c1 = ciph1.c0.multiply(ciph2.c1, modulus, crt=self.crt_context)
        temp = ciph1.c1.multiply(ciph2.c0, modulus, crt=self.crt_context)
        c1 = c1.add(temp, modulus)
        c1 = c1.mod_small(modulus)

        c2 = ciph1.c1.multiply(ciph2.c1, modulus, crt=self.crt_context)
        c2 = c2.mod_small(modulus)

        return self.relinearize(relin_key, c0, c1, c2,
                                ciph1.scaling_factor * ciph2.scaling_factor, modulus)

    def multiply_plain(self, ciph, plain):
        """密文与明文乘法"""
        c0 = ciph.c0.multiply(plain.poly, ciph.modulus, crt=self.crt_context)
        c0 = c0.mod_small(ciph.modulus)

        c1 = ciph.c1.multiply(plain.poly, ciph.modulus, crt=self.crt_context)
        c1 = c1.mod_small(ciph.modulus)

        return Ciphertext(c0, c1, ciph.scaling_factor * plain.scaling_factor, ciph.modulus)

    def relinearize(self, relin_key, c0, c1, c2, new_scaling_factor, modulus):
        """重线性化"""
        new_c0 = relin_key.p0.multiply(c2, modulus * self.big_modulus, crt=self.crt_context)
        new_c0 = new_c0.mod_small(modulus * self.big_modulus)
        new_c0 = new_c0.scalar_integer_divide(self.big_modulus)
        new_c0 = new_c0.add(c0, modulus)
        new_c0 = new_c0.mod_small(modulus)

        new_c1 = relin_key.p1.multiply(c2, modulus * self.big_modulus, crt=self.crt_context)
        new_c1 = new_c1.mod_small(modulus * self.big_modulus)
        new_c1 = new_c1.scalar_integer_divide(self.big_modulus)
        new_c1 = new_c1.add(c1, modulus)
        new_c1 = new_c1.mod_small(modulus)

        return Ciphertext(new_c0, new_c1, new_scaling_factor, modulus)

    def rescale(self, ciph, division_factor):
        """重缩放"""
        c0 = ciph.c0.scalar_integer_divide(division_factor)
        c1 = ciph.c1.scalar_integer_divide(division_factor)
        return Ciphertext(c0, c1, ciph.scaling_factor // division_factor,
                          ciph.modulus // division_factor)

    def lower_modulus(self, ciph, division_factor):
        """降低模数"""
        new_modulus = ciph.modulus // division_factor
        c0 = ciph.c0.mod_small(new_modulus)
        c1 = ciph.c1.mod_small(new_modulus)
        return Ciphertext(c0, c1, ciph.scaling_factor, new_modulus)