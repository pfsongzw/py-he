from mathematics.ntt import NTTContext,FFTContext


class Polynomial:
    """完整的多项式运算实现"""

    def __init__(self, degree, coeffs):
        self.ring_degree = degree
        assert len(coeffs) == degree, f'多项式数组大小{len(coeffs)}不等于环度数{degree}'
        self.coeffs = coeffs

    def add(self, poly, coeff_modulus=None):
        """多项式加法"""
        assert isinstance(poly, Polynomial)

        poly_sum = Polynomial(self.ring_degree, [0] * self.ring_degree)
        poly_sum.coeffs = [self.coeffs[i] + poly.coeffs[i] for i in range(self.ring_degree)]

        if coeff_modulus:
            poly_sum = poly_sum.mod(coeff_modulus)
        return poly_sum

    def subtract(self, poly, coeff_modulus=None):
        """多项式减法"""
        assert isinstance(poly, Polynomial)

        poly_diff = Polynomial(self.ring_degree, [0] * self.ring_degree)
        poly_diff.coeffs = [self.coeffs[i] - poly.coeffs[i] for i in range(self.ring_degree)]

        if coeff_modulus:
            poly_diff = poly_diff.mod(coeff_modulus)
        return poly_diff

    def multiply(self, poly, coeff_modulus, ntt=None, crt=None):
        """多项式乘法"""
        if crt:
            return self.multiply_crt(poly, crt)

        if ntt:
            a = ntt.ftt_fwd(self.coeffs)
            b = ntt.ftt_fwd(poly.coeffs)
            ab = [a[i] * b[i] for i in range(self.ring_degree)]
            prod = ntt.ftt_inv(ab)
            return Polynomial(self.ring_degree, prod)

        return self.multiply_naive(poly, coeff_modulus)

    def multiply_crt(self, poly, crt):
        """CRT多项式乘法"""
        assert isinstance(poly, Polynomial)

        poly_prods = []

        # 对每个素数执行NTT
        for i in range(len(crt.primes)):
            prod = self.multiply(poly, crt.primes[i], ntt=crt.ntts[i])
            poly_prods.append(prod)

        # 使用CRT组合结果
        final_coeffs = [0] * self.ring_degree
        for i in range(self.ring_degree):
            values = [p.coeffs[i] for p in poly_prods]
            final_coeffs[i] = crt.reconstruct(values)

        return Polynomial(self.ring_degree, final_coeffs).mod_small(crt.modulus)

    def multiply_fft(self, poly, round=True):
        """FFT多项式乘法"""
        assert isinstance(poly, Polynomial)

        fft = FFTContext(self.ring_degree * 8)
        a = fft.fft_fwd(self.coeffs + [0] * self.ring_degree)
        b = fft.fft_fwd(poly.coeffs + [0] * self.ring_degree)
        ab = [a[i] * b[i] for i in range(self.ring_degree * 2)]
        prod = fft.fft_inv(ab)
        poly_prod = [0] * self.ring_degree

        for d in range(2 * self.ring_degree - 1):
            index = d % self.ring_degree
            sign = (int(d < self.ring_degree) - 0.5) * 2
            poly_prod[index] += sign * prod[d]

        if round:
            return Polynomial(self.ring_degree, poly_prod).round()
        else:
            return Polynomial(self.ring_degree, poly_prod)

    def multiply_naive(self, poly, coeff_modulus=None):
        """朴素多项式乘法"""
        assert isinstance(poly, Polynomial)

        poly_prod = Polynomial(self.ring_degree, [0] * self.ring_degree)

        for d in range(2 * self.ring_degree - 1):
            index = d % self.ring_degree
            sign = int(d < self.ring_degree) * 2 - 1

            coeff = 0
            for i in range(self.ring_degree):
                if 0 <= d - i < self.ring_degree:
                    coeff += self.coeffs[i] * poly.coeffs[d - i]
            poly_prod.coeffs[index] += sign * coeff

            if coeff_modulus:
                poly_prod.coeffs[index] %= coeff_modulus

        return poly_prod

    def scalar_multiply(self, scalar, coeff_modulus=None):
        """标量乘法"""
        if coeff_modulus:
            new_coeffs = [(scalar * c) % coeff_modulus for c in self.coeffs]
        else:
            new_coeffs = [(scalar * c) for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

    def scalar_integer_divide(self, scalar, coeff_modulus=None):
        """整数除法"""
        if coeff_modulus:
            new_coeffs = [(c // scalar) % coeff_modulus for c in self.coeffs]
        else:
            new_coeffs = [(c // scalar) for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

    def rotate(self, r):
        """多项式旋转"""
        k = 5 ** r
        new_coeffs = [0] * self.ring_degree
        for i in range(self.ring_degree):
            index = (i * k) % (2 * self.ring_degree)
            if index < self.ring_degree:
                new_coeffs[index] = self.coeffs[i]
            else:
                new_coeffs[index - self.ring_degree] = -self.coeffs[i]
        return Polynomial(self.ring_degree, new_coeffs)

    def conjugate(self):
        """多项式共轭"""
        new_coeffs = [0] * self.ring_degree
        new_coeffs[0] = self.coeffs[0]
        for i in range(1, self.ring_degree):
            new_coeffs[i] = -self.coeffs[self.ring_degree - i]
        return Polynomial(self.ring_degree, new_coeffs)

    def round(self):
        """系数舍入"""
        if type(self.coeffs[0]) == complex:
            new_coeffs = [round(c.real) for c in self.coeffs]
        else:
            new_coeffs = [round(c) for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

    def floor(self):
        """系数向下取整"""
        new_coeffs = [int(c) for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

    def mod(self, coeff_modulus):
        """模运算"""
        new_coeffs = [c % coeff_modulus for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

    def mod_small(self, coeff_modulus):
        """小范围模运算"""
        try:
            new_coeffs = [c % coeff_modulus for c in self.coeffs]
            new_coeffs = [c - coeff_modulus if c > coeff_modulus // 2 else c for c in new_coeffs]
        except:
            print(self.coeffs)
            print(coeff_modulus)
            new_coeffs = [c % coeff_modulus for c in self.coeffs]
            new_coeffs = [c - coeff_modulus if c > coeff_modulus // 2 else c for c in new_coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

    def base_decompose(self, base, num_levels):
        """基分解"""
        decomposed = [Polynomial(self.ring_degree, [0] * self.ring_degree) for _ in range(num_levels)]
        poly = self

        for i in range(num_levels):
            decomposed[i] = poly.mod(base)
            poly = poly.scalar_multiply(1 / base).floor()
        return decomposed

    def evaluate(self, inp):
        """多项式求值"""
        result = self.coeffs[-1]

        for i in range(self.ring_degree - 2, -1, -1):
            result = result * inp + self.coeffs[i]

        return result

    def __str__(self):
        """字符串表示"""
        s = ''
        for i in range(self.ring_degree - 1, -1, -1):
            if self.coeffs[i] != 0:
                if s != '':
                    s += ' + '
                if i == 0 or self.coeffs[i] != 1:
                    s += str(int(self.coeffs[i]))
                if i != 0:
                    s += 'x'
                if i > 1:
                    s += '^' + str(i)
        return s