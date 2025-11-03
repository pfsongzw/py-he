from core.parameters import CKKSParameters
from core.key_generator import CKKSKeyGenerator
from core.encoder import CKKSEncoder
from core.encryptor import CKKSEncryptor
from core.decryptor import CKKSDecryptor
from core.evaluator import CKKSEvaluator
import mathematics


def demo_complete_ckks():
    """完整的CKKS演示"""
    # 初始化参数
    params = CKKSParameters(
        poly_degree=4096,
        ciph_modulus=1 << 40,
        big_modulus=1 << 50,
        scaling_factor=1 << 30,
        taylor_iterations=6,
        prime_size=59,
        hamming_weight=1024
    )

    params.print_parameters()

    # 初始化所有组件
    keygen = CKKSKeyGenerator(params)
    encoder = CKKSEncoder(params)
    encryptor = CKKSEncryptor(params, keygen.public_key)
    decryptor = CKKSDecryptor(params, keygen.secret_key)
    evaluator = CKKSEvaluator(params)

    # 生成旋转密钥
    rotation_keys = {}
    for rotation in [1, 2, 4, 8, 16, 32]:
        rotation_keys[rotation] = keygen.generate_rot_key(rotation)

    conj_key = keygen.generate_conj_key()

    print("\n🔑 密钥生成完成")

    # 测试数据
    vec1 = [1.5 + 2.5j, 3.5 + 4.5j, 5.5 + 6.5j, 7.5 + 8.5j]
    vec2 = [2.0 + 1.0j, 4.0 + 3.0j, 6.0 + 5.0j, 8.0 + 7.0j]

    print(f"原始数据:")
    print(f"vec1: {vec1}")
    print(f"vec2: {vec2}")

    # 编码和加密
    plain1 = encoder.encode(vec1, params.scaling_factor)
    plain2 = encoder.encode(vec2, params.scaling_factor)

    ct1 = encryptor.encrypt(plain1)
    ct2 = encryptor.encrypt(plain2)

    print(f"\n🔒 加密完成")

    # 同态加法
    ct_sum = evaluator.add(ct1, ct2)
    result_sum = decryptor.decrypt(ct_sum)
    decoded_sum = encoder.decode(result_sum)

    print(f"\n➕ 同态加法:")
    print(f"预期: {[vec1[i] + vec2[i] for i in range(len(vec1))]}")
    print(f"实际: {decoded_sum[:len(vec1)]}")

    # 同态乘法
    ct_prod = evaluator.multiply(ct1, ct2, keygen.relin_key)
    result_prod = decryptor.decrypt(ct_prod)
    decoded_prod = encoder.decode(result_prod)

    print(f"\n✖️ 同态乘法:")
    print(f"预期: {[vec1[i] * vec2[i] for i in range(len(vec1))]}")
    print(f"实际: {decoded_prod[:len(vec1)]}")

    # 同态旋转
    ct_rotated = evaluator.rotate(ct1, 1, rotation_keys[1])
    result_rotated = decryptor.decrypt(ct_rotated)
    decoded_rotated = encoder.decode(result_rotated)

    print(f"\n🔄 同态旋转:")
    print(f"预期旋转: {vec1[1:]} + {vec1[:1]}")
    print(f"实际旋转: {decoded_rotated[:len(vec1)]}")

    # 同态共轭
    ct_conjugated = evaluator.conjugate(ct1, conj_key)
    result_conjugated = decryptor.decrypt(ct_conjugated)
    decoded_conjugated = encoder.decode(result_conjugated)

    print(f"\n🔄 同态共轭:")
    print(f"预期共轭: {[v.conjugate() for v in vec1]}")
    print(f"实际共轭: {decoded_conjugated[:len(vec1)]}")

    # 测试重缩放
    ct_rescaled = evaluator.rescale(ct_prod, params.scaling_factor)
    print(f"\n📏 重缩放完成:")
    print(f"原始模数: {ct_prod.modulus}")
    print(f"重缩放后模数: {ct_rescaled.modulus}")
    print(f"原始缩放因子: {ct_prod.scaling_factor}")
    print(f"重缩放后缩放因子: {ct_rescaled.scaling_factor}")

    # 测试自举（如果噪声水平允许）
    try:
        # 创建高噪声密文
        ct_high_noise = ct_prod
        for i in range(2):
            ct_high_noise = evaluator.multiply(ct_high_noise, ct_high_noise, keygen.relin_key)
            ct_high_noise = evaluator.rescale(ct_high_noise, params.scaling_factor)

        print(f"\n🔄 尝试自举...")
        ct_bootstrapped = evaluator.bootstrap(ct_high_noise, rotation_keys, conj_key,
                                              keygen.relin_key, encoder)

        result_bootstrapped = decryptor.decrypt(ct_bootstrapped)
        decoded_bootstrapped = encoder.decode(result_bootstrapped)

        print(f"自举后解密成功")
        print(f"自举结果: {decoded_bootstrapped[:len(vec1)]}")

    except Exception as e:
        print(f"自举失败: {e}")


if __name__ == "__main__":
    demo_complete_ckks()