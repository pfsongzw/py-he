from primitives.ciphertext import Ciphertext
from mathematics.polynomial import Polynomial
from utils.random_sampler import sample_triangle


class CKKSEncryptor:
    """完整的CKKS加密器"""

    def __init__(self, params, public_key, secret_key=None):
        self.poly_degree = params.poly_degree
        self.coeff_modulus = params.ciph_modulus
        self.big_modulus = params.big_modulus
        self.crt_context = params.crt_context
        self.public_key = public_key
        self.secret_key = secret_key

    def encrypt_with_secret_key(self, plain):
        """私钥加密"""
        assert self.secret_key != None, '私钥不存在'

        sk = self.secret_key.s
        random_vec = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))
        error = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))

        c0 = sk.multiply(random_vec, self.coeff_modulus, crt=self.crt_context)
        c0 = error.add(c0, self.coeff_modulus)
        c0 = c0.add(plain.poly, self.coeff_modulus)
        c0 = c0.mod_small(self.coeff_modulus)

        c1 = random_vec.scalar_multiply(-1, self.coeff_modulus)
        c1 = c1.mod_small(self.coeff_modulus)

        return Ciphertext(c0, c1, plain.scaling_factor, self.coeff_modulus)

    def encrypt(self, plain):
        """公钥加密"""
        p0 = self.public_key.p0
        p1 = self.public_key.p1

        random_vec = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))
        error1 = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))
        error2 = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))

        c0 = p0.multiply(random_vec, self.coeff_modulus, crt=self.crt_context)
        c0 = error1.add(c0, self.coeff_modulus)
        c0 = c0.add(plain.poly, self.coeff_modulus)
        c0 = c0.mod_small(self.coeff_modulus)

        c1 = p1.multiply(random_vec, self.coeff_modulus, crt=self.crt_context)
        c1 = error2.add(c1, self.coeff_modulus)
        c1 = c1.mod_small(self.coeff_modulus)

        return Ciphertext(c0, c1, plain.scaling_factor, self.coeff_modulus)

    def raise_modulus(self, new_modulus):
        """提升模数"""
        self.coeff_modulus = new_modulus