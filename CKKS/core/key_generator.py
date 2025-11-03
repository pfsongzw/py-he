from primitives.secret_key import SecretKey
from primitives.public_key import PublicKey
from primitives.rotation_key import RotationKey
from mathematics.polynomial import Polynomial
from utils.random_sampler import sample_triangle, sample_uniform, sample_hamming_weight_vector


class CKKSKeyGenerator:
    """完整的CKKS密钥生成器"""

    def __init__(self, params):
        self.params = params
        self.generate_secret_key(params)
        self.generate_public_key(params)
        self.generate_relin_key(params)

    def generate_secret_key(self, params):
        """生成私钥"""
        key = sample_hamming_weight_vector(params.poly_degree, params.hamming_weight)
        self.secret_key = SecretKey(Polynomial(params.poly_degree, key))

    def generate_public_key(self, params):
        """生成公钥"""
        mod = self.params.big_modulus

        pk_coeff = Polynomial(params.poly_degree, sample_uniform(0, mod, params.poly_degree))
        pk_error = Polynomial(params.poly_degree, sample_triangle(params.poly_degree))
        p0 = pk_coeff.multiply(self.secret_key.s, mod)
        p0 = p0.scalar_multiply(-1, mod)
        p0 = p0.add(pk_error, mod)
        p1 = pk_coeff
        self.public_key = PublicKey(p0, p1)

    def generate_switching_key(self, new_key):
        """生成交换密钥"""
        mod = self.params.big_modulus
        mod_squared = mod ** 2

        swk_coeff = Polynomial(self.params.poly_degree, sample_uniform(0, mod_squared, self.params.poly_degree))
        swk_error = Polynomial(self.params.poly_degree, sample_triangle(self.params.poly_degree))

        sw0 = swk_coeff.multiply(self.secret_key.s, mod_squared)
        sw0 = sw0.scalar_multiply(-1, mod_squared)
        sw0 = sw0.add(swk_error, mod_squared)
        temp = new_key.scalar_multiply(mod, mod_squared)
        sw0 = sw0.add(temp, mod_squared)
        sw1 = swk_coeff
        return PublicKey(sw0, sw1)

    def generate_relin_key(self, params):
        """生成重线性化密钥"""
        sk_squared = self.secret_key.s.multiply(self.secret_key.s, self.params.big_modulus)
        self.relin_key = self.generate_switching_key(sk_squared)

    def generate_rot_key(self, rotation):
        """生成旋转密钥"""
        new_key = self.secret_key.s.rotate(rotation)
        rk = self.generate_switching_key(new_key)
        return RotationKey(rotation, rk)

    def generate_conj_key(self):
        """生成共轭密钥"""
        new_key = self.secret_key.s.conjugate()
        return self.generate_switching_key(new_key)