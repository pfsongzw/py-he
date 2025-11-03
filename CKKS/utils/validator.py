"""完整的参数验证器"""
from primitives.ciphertext import Ciphertext


class CKKSValidator:
    """CKKS参数验证器"""

    @staticmethod
    def validate_parameters(params):
        """验证参数有效性"""
        errors = []

        if not (params.poly_degree & (params.poly_degree - 1) == 0 and params.poly_degree != 0):
            errors.append("多项式度数必须是2的幂")

        if params.ciph_modulus <= 0:
            errors.append("密文模数必须为正数")

        if params.scaling_factor <= 1:
            errors.append("缩放因子必须大于1")

        if params.big_modulus <= params.ciph_modulus:
            errors.append("大模数必须大于密文模数")

        if errors:
            raise ValueError("参数验证失败: " + "; ".join(errors))

    @staticmethod
    def validate_ciphertext(ciph, expected_modulus=None):
        """验证密文有效性"""
        if not isinstance(ciph, Ciphertext):
            raise ValueError("密文必须是Ciphertext实例")

        if len(ciph.c0.coeffs) != len(ciph.c1.coeffs):
            raise ValueError("密文组件长度不一致")

        if expected_modulus and ciph.modulus != expected_modulus:
            raise ValueError(f"密文模数不匹配: 期望{expected_modulus}, 实际{ciph.modulus}")

        for coeff in ciph.c0.coeffs + ciph.c1.coeffs:
            if abs(coeff) > ciph.modulus:
                raise ValueError("密文系数超出模数范围")