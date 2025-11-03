from math import log, pi, cos, sin
import mathematics.number_theory as nbtheory
from utils.bit_operations import reverse_bits,bit_reverse_vec


class NTTContext:
    """完整的NTT上下文实现"""

    def __init__(self, poly_degree, coeff_modulus, root_of_unity=None):
        assert (poly_degree & (poly_degree - 1)) == 0, \
            "多项式度数必须是2的幂"
        self.coeff_modulus = coeff_modulus
        self.degree = poly_degree

        if not root_of_unity:
            root_of_unity = nbtheory.root_of_unity(order=2 * poly_degree, modulus=coeff_modulus)

        self.precompute_ntt(root_of_unity)

    def precompute_ntt(self, root_of_unity):
        """NTT预计算"""
        self.roots_of_unity = [1] * self.degree
        for i in range(1, self.degree):
            self.roots_of_unity[i] = \
                (self.roots_of_unity[i - 1] * root_of_unity) % self.coeff_modulus

        root_of_unity_inv = nbtheory.mod_inv(root_of_unity, self.coeff_modulus)
        self.roots_of_unity_inv = [1] * self.degree
        for i in range(1, self.degree):
            self.roots_of_unity_inv[i] = \
                (self.roots_of_unity_inv[i - 1] * root_of_unity_inv) % self.coeff_modulus

        self.reversed_bits = [0] * self.degree
        width = int(log(self.degree, 2))
        for i in range(self.degree):
            self.reversed_bits[i] = reverse_bits(i, width) % self.degree

    def ntt(self, coeffs, rou):
        """NTT变换"""
        num_coeffs = len(coeffs)
        assert len(rou) == num_coeffs, \
            "单位根长度太小"

        result = bit_reverse_vec(coeffs)
        log_num_coeffs = int(log(num_coeffs, 2))

        for logm in range(1, log_num_coeffs + 1):
            for j in range(0, num_coeffs, (1 << logm)):
                for i in range(1 << (logm - 1)):
                    index_even = j + i
                    index_odd = j + i + (1 << (logm - 1))

                    rou_idx = (i << (1 + log_num_coeffs - logm))
                    omega_factor = (rou[rou_idx] * result[index_odd]) % self.coeff_modulus

                    butterfly_plus = (result[index_even] + omega_factor) % self.coeff_modulus
                    butterfly_minus = (result[index_even] - omega_factor) % self.coeff_modulus

                    result[index_even] = butterfly_plus
                    result[index_odd] = butterfly_minus

        return result

    def ftt_fwd(self, coeffs):
        """前向FTT"""
        num_coeffs = len(coeffs)
        assert num_coeffs == self.degree, "ftt_fwd: 输入长度不匹配"

        ftt_input = [(int(coeffs[i]) * self.roots_of_unity[i]) % self.coeff_modulus
                     for i in range(num_coeffs)]

        return self.ntt(coeffs=ftt_input, rou=self.roots_of_unity)

    def ftt_inv(self, coeffs):
        """逆向FTT"""
        num_coeffs = len(coeffs)
        assert num_coeffs == self.degree, "ntt_inv: 输入长度不匹配"

        to_scale_down = self.ntt(coeffs=coeffs, rou=self.roots_of_unity_inv)
        poly_degree_inv = nbtheory.mod_inv(self.degree, self.coeff_modulus)

        result = [(int(to_scale_down[i]) * self.roots_of_unity_inv[i] * poly_degree_inv) \
                  % self.coeff_modulus for i in range(num_coeffs)]

        return result


class FFTContext:
    """完整的FFT上下文实现"""

    def __init__(self, fft_length):
        self.fft_length = fft_length
        self.precompute_fft()

    def precompute_fft(self):
        """FFT预计算"""
        self.roots_of_unity = [0] * self.fft_length
        self.roots_of_unity_inv = [0] * self.fft_length
        for i in range(self.fft_length):
            angle = 2 * pi * i / self.fft_length
            self.roots_of_unity[i] = complex(cos(angle), sin(angle))
            self.roots_of_unity_inv[i] = complex(cos(-angle), sin(-angle))

        num_slots = self.fft_length // 4
        self.reversed_bits = [0] * num_slots
        width = int(log(num_slots, 2))
        for i in range(num_slots):
            self.reversed_bits[i] = reverse_bits(i, width) % num_slots

        self.rot_group = [1] * num_slots
        for i in range(1, num_slots):
            self.rot_group[i] = (5 * self.rot_group[i - 1]) % self.fft_length

    def fft(self, coeffs, rou):
        """FFT变换"""
        num_coeffs = len(coeffs)
        assert len(rou) >= num_coeffs, \
            f"单位根长度太小: {len(rou)}"

        result = bit_reverse_vec(coeffs)
        log_num_coeffs = int(log(num_coeffs, 2))

        for logm in range(1, log_num_coeffs + 1):
            for j in range(0, num_coeffs, (1 << logm)):
                for i in range(1 << (logm - 1)):
                    index_even = j + i
                    index_odd = j + i + (1 << (logm - 1))

                    rou_idx = (i * self.fft_length) >> logm
                    omega_factor = rou[rou_idx] * result[index_odd]

                    butterfly_plus = result[index_even] + omega_factor
                    butterfly_minus = result[index_even] - omega_factor

                    result[index_even] = butterfly_plus
                    result[index_odd] = butterfly_minus

        return result

    def fft_fwd(self, coeffs):
        """前向FFT"""
        return self.fft(coeffs, rou=self.roots_of_unity)

    def fft_inv(self, coeffs):
        """逆向FFT"""
        num_coeffs = len(coeffs)
        result = self.fft(coeffs, rou=self.roots_of_unity_inv)

        for i in range(num_coeffs):
            result[i] /= num_coeffs

        return result

    def check_embedding_input(self, values):
        """检查嵌入输入"""
        assert len(values) <= self.fft_length / 4, \
            f"输入向量长度必须小于等于 {self.fft_length / 4}"

    def embedding(self, coeffs):
        """规范嵌入"""
        self.check_embedding_input(coeffs)
        num_coeffs = len(coeffs)
        result = bit_reverse_vec(coeffs)
        log_num_coeffs = int(log(num_coeffs, 2))

        for logm in range(1, log_num_coeffs + 1):
            idx_mod = 1 << (logm + 2)
            gap = self.fft_length // idx_mod
            for j in range(0, num_coeffs, (1 << logm)):
                for i in range(1 << (logm - 1)):
                    index_even = j + i
                    index_odd = j + i + (1 << (logm - 1))

                    rou_idx = (self.rot_group[i] % idx_mod) * gap
                    omega_factor = self.roots_of_unity[rou_idx] * result[index_odd]

                    butterfly_plus = result[index_even] + omega_factor
                    butterfly_minus = result[index_even] - omega_factor

                    result[index_even] = butterfly_plus
                    result[index_odd] = butterfly_minus

        return result

    def embedding_inv(self, coeffs):
        """规范嵌入逆变换"""
        self.check_embedding_input(coeffs)
        num_coeffs = len(coeffs)
        result = coeffs.copy()
        log_num_coeffs = int(log(num_coeffs, 2))

        for logm in range(log_num_coeffs, 0, -1):
            idx_mod = 1 << (logm + 2)
            gap = self.fft_length // idx_mod
            for j in range(0, num_coeffs, 1 << logm):
                for i in range(1 << (logm - 1)):
                    index_even = j + i
                    index_odd = j + i + (1 << (logm - 1))

                    rou_idx = (self.rot_group[i] % idx_mod) * gap

                    butterfly_plus = result[index_even] + result[index_odd]
                    butterfly_minus = result[index_even] - result[index_odd]
                    butterfly_minus *= self.roots_of_unity_inv[rou_idx]

                    result[index_even] = butterfly_plus
                    result[index_odd] = butterfly_minus

        to_scale_down = bit_reverse_vec(result)

        for i in range(num_coeffs):
            to_scale_down[i] /= num_coeffs

        return to_scale_down