"""完整的性能测试"""

import time
from core.parameters import CKKSParameters
from core.key_generator import CKKSKeyGenerator
from core.encoder import CKKSEncoder
from core.encryptor import CKKSEncryptor
from core.decryptor import CKKSDecryptor
from core.evaluator import CKKSEvaluator


def performance_test():
    """性能测试"""
    params = CKKSParameters(
        poly_degree=2048,
        ciph_modulus=1 << 40,
        big_modulus=1 << 50,
        scaling_factor=1 << 30
    )

    print("开始性能测试...")

    # 密钥生成时间
    start_time = time.time()
    keygen = CKKSKeyGenerator(params)
    keygen_time = time.time() - start_time

    encoder = CKKSEncoder(params)
    encryptor = CKKSEncryptor(params, keygen.public_key)
    decryptor = CKKSDecryptor(params, keygen.secret_key)
    evaluator = CKKSEvaluator(params)

    # 测试数据
    vec = [complex(i, i + 1) for i in range(16)]

    # 编码时间
    start_time = time.time()
    plain = encoder.encode(vec, params.scaling_factor)
    encode_time = time.time() - start_time

    # 加密时间
    start_time = time.time()
    ciphertext = encryptor.encrypt(plain)
    encrypt_time = time.time() - start_time

    # 解密时间
    start_time = time.time()
    decrypted = decryptor.decrypt(ciphertext)
    decrypt_time = time.time() - start_time

    # 解码时间
    start_time = time.time()
    decoded = encoder.decode(decrypted)
    decode_time = time.time() - start_time

    # 同态运算时间
    start_time = time.time()
    ct_squared = evaluator.multiply(ciphertext, ciphertext, keygen.relin_key)
    multiply_time = time.time() - start_time

    start_time = time.time()
    ct_sum = evaluator.add(ciphertext, ciphertext)
    add_time = time.time() - start_time

    print("\n性能测试结果:")
    print(f"密钥生成: {keygen_time:.4f}秒")
    print(f"编码: {encode_time:.4f}秒")
    print(f"加密: {encrypt_time:.4f}秒")
    print(f"解密: {decrypt_time:.4f}秒")
    print(f"解码: {decode_time:.4f}秒")
    print(f"同态乘法: {multiply_time:.4f}秒")
    print(f"同态加法: {add_time:.4f}秒")

    # 验证正确性
    expected_square = [v * v for v in vec]
    actual_square = encoder.decode(decryptor.decrypt(ct_squared))

    accuracy = sum(abs(expected_square[i] - actual_square[i]) for i in range(len(vec))) / len(vec)
    print(f"\n计算精度: {accuracy:.6f}")

    return accuracy < 0.5


if __name__ == "__main__":
    success = performance_test()
    if success:
        print("\n✅ 性能测试通过!")
    else:
        print("\n❌ 性能测试失败!")