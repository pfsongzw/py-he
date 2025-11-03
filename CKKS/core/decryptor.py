from primitives.plaintext import Plaintext


class CKKSDecryptor:
    """完整的CKKS解密器"""

    def __init__(self, params, secret_key):
        self.poly_degree = params.poly_degree
        self.crt_context = params.crt_context
        self.secret_key = secret_key

    def decrypt(self, ciphertext, c2=None):
        """完整解密实现"""
        (c0, c1) = (ciphertext.c0, ciphertext.c1)

        message = c1.multiply(self.secret_key.s, ciphertext.modulus, crt=self.crt_context)
        message = c0.add(message, ciphertext.modulus)

        if c2:
            secret_key_squared = self.secret_key.s.multiply(self.secret_key.s, ciphertext.modulus)
            c2_message = c2.multiply(secret_key_squared, ciphertext.modulus, crt=self.crt_context)
            message = message.add(c2_message, ciphertext.modulus)

        message = message.mod_small(ciphertext.modulus)
        return Plaintext(message, ciphertext.scaling_factor)