from mathematics.fft import FFTContext
from primitives.plaintext import Plaintext
from mathematics.polynomial import Polynomial


class CKKSEncoder:
    """完整的CKKS编码器实现"""

    def __init__(self, params):
        self.degree = params.poly_degree
        self.fft = FFTContext(self.degree * 2)

    def encode(self, values, scaling_factor):
        """完整编码实现"""
        num_values = len(values)
        plain_len = num_values << 1

        # 规范嵌入逆变换
        to_scale = self.fft.embedding_inv(values)

        # 缩放和舍入
        message = [0] * plain_len
        for i in range(num_values):
            message[i] = int(to_scale[i].real * scaling_factor + 0.5)
            message[i + num_values] = int(to_scale[i].imag * scaling_factor + 0.5)

        return Plaintext(Polynomial(plain_len, message), scaling_factor)

    def decode(self, plain):
        """完整解码实现"""
        if not isinstance(plain, Plaintext):
            raise ValueError("解码输入必须是明文类型")

        plain_len = len(plain.poly.coeffs)
        num_values = plain_len >> 1

        # 恢复复数表示
        message = [0] * num_values
        for i in range(num_values):
            message[i] = complex(plain.poly.coeffs[i] / plain.scaling_factor,
                                 plain.poly.coeffs[i + num_values] / plain.scaling_factor)

        # 规范嵌入变换
        return self.fft.embedding(message)