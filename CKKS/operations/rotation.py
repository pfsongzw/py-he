"""完整的旋转操作实现"""

from primitives.ciphertext import Ciphertext
from mathematics.polynomial import Polynomial


class RotationOperations:
    """完整的旋转操作"""

    def __init__(self, params, crt_context):
        self.params = params
        self.crt_context = crt_context
        self.big_modulus = params.big_modulus

    def rotate(self, ciph, rotation, rot_key):
        """同态旋转"""
        rot_ciph0 = ciph.c0.rotate(rotation)
        rot_ciph1 = ciph.c1.rotate(rotation)
        rot_ciph = Ciphertext(rot_ciph0, rot_ciph1, ciph.scaling_factor, ciph.modulus)
        return self.switch_key(rot_ciph, rot_key.key)

    def conjugate(self, ciph, conj_key):
        """同态共轭"""
        conj_ciph0 = ciph.c0.conjugate().mod_small(ciph.modulus)
        conj_ciph1 = ciph.c1.conjugate().mod_small(ciph.modulus)
        conj_ciph = Ciphertext(conj_ciph0, conj_ciph1, ciph.scaling_factor, ciph.modulus)
        return self.switch_key(conj_ciph, conj_key)

    def switch_key(self, ciph, key):
        """密钥交换"""
        c0 = key.p0.multiply(ciph.c1, ciph.modulus * self.big_modulus, crt=self.crt_context)
        c0 = c0.mod_small(ciph.modulus * self.big_modulus)
        c0 = c0.scalar_integer_divide(self.big_modulus)
        c0 = c0.add(ciph.c0, ciph.modulus)
        c0 = c0.mod_small(ciph.modulus)

        c1 = key.p1.multiply(ciph.c1, ciph.modulus * self.big_modulus, crt=self.crt_context)
        c1 = c1.mod_small(ciph.modulus * self.big_modulus)
        c1 = c1.scalar_integer_divide(self.big_modulus)
        c1 = c1.mod_small(ciph.modulus)

        return Ciphertext(c0, c1, ciph.scaling_factor, ciph.modulus)