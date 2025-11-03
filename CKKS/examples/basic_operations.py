"""完整的基础运算测试"""

from core.parameters import CKKSParameters
from core.key_generator import CKKSKeyGenerator
from core.encoder import CKKSEncoder
from core.encryptor import CKKSEncryptor
from core.decryptor import CKKSDecryptor
from core.evaluator import CKKSEvaluator


def test_basic_operations():
    """基础运算测试"""
    params = CKKSParameters(
        poly_degree=1024,
        ciph_modulus=1 << 40,
        big_modulus=1 << 50,
        scaling_factor=1 << 30
    )

    keygen = CKKSKeyGenerator(params)
    encoder = CKKSEncoder(params)
    encryptor = CKKSEncryptor(params, keygen.public_key)
    decryptor = CKKSDecryptor(params, keygen.secret_key)
    evaluator = CKKSEvaluator(params)

    # 测试数据
    vec1 = [1.0 + 2.0j, 3.0 + 4.0j]
    vec2 = [2.0 + 1.0j, 4.0 + 3.0j]

    print("测试基础运算:")
    print(f"vec1: {vec1}")
    print(f"vec2: {vec2}")

    # 编码和加密
    plain1 = encoder.encode(vec1, params.scaling_factor)
    plain2 = encoder.encode(vec2, params.scaling_factor)

    ct1 = encryptor.encrypt(plain1)
    ct2 = encryptor.encrypt(plain2)

    # 同态加法
    ct_sum = evaluator.add(ct1, ct2)
    result_sum = decryptor.decrypt(ct_sum)
    decoded_sum = encoder.decode(result_sum)

    print(f"\n同态加法结果:")
    print(f"预期: {[vec1[i] + vec2[i] for i in range(len(vec1))]}")
    print(f"实际: {decoded_sum[:len(vec1)]}")

    # 同态乘法
    ct_prod = evaluator.multiply(ct1, ct2, keygen.relin_key)
    result_prod = decryptor.decrypt(ct_prod)
    decoded_prod = encoder.decode(result_prod)

    print(f"\n同态乘法结果:")
    print(f"预期: {[vec1[i] * vec2[i] for i in range(len(vec1))]}")
    print(f"实际: {decoded_prod[:len(vec1)]}")

    # 验证精度
    def calculate_accuracy(expected, actual):
        errors = [abs(expected[i] - actual[i]) for i in range(len(expected))]
        return sum(errors) / len(errors)

    add_accuracy = calculate_accuracy(
        [vec1[i] + vec2[i] for i in range(len(vec1))],
        decoded_sum[:len(vec1)]
    )

    mul_accuracy = calculate_accuracy(
        [vec1[i] * vec2[i] for i in range(len(vec1))],
        decoded_prod[:len(vec1)]
    )

    print(f"\n精度评估:")
    print(f"加法平均误差: {add_accuracy:.6f}")
    print(f"乘法平均误差: {mul_accuracy:.6f}")

    return add_accuracy < 0.1 and mul_accuracy < 0.5


if __name__ == "__main__":
    success = test_basic_operations()
    if success:
        print("\n✅ 基础运算测试通过!")
    else:
        print("\n❌ 基础运算测试失败!")