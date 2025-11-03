"""
优化的FFT实现
修复索引错误和性能问题，保持接口不变
"""

import math
import numpy as np
from typing import List, Union
import time

class FFTContext:
    """FFT上下文类 - 修复索引和性能问题"""

    def __init__(self, fft_length):
        # 修复：验证输入参数
        if fft_length <= 0:
            raise ValueError("FFT长度必须为正整数")

        if (fft_length & (fft_length - 1)) != 0:
            raise ValueError("FFT长度必须是2的幂")

        self.fft_length = fft_length
        self.log2n = int(math.log2(fft_length))

        # 修复：预计算优化
        self._precomputed = False
        self._precompute_twiddles()
        self._precompute_bit_reversal()
        self._precomputed = True

    def _precompute_twiddles(self):
        """预计算旋转因子 - 修复计算错误"""
        n = self.fft_length

        # 修复：正确的旋转因子计算
        self.twiddles = []
        for k in range(n // 2):
            angle = -2 * math.pi * k / n  # 修复：正确的角度符号
            real_part = math.cos(angle)
            imag_part = math.sin(angle)
            self.twiddles.append(complex(real_part, imag_part))

    def _precompute_bit_reversal(self):
        """预计算位反转表 - 修复索引错误"""
        n = self.fft_length
        self.bit_reversal = [0] * n

        # 修复：正确的位反转算法
        for i in range(n):
            reversed_index = 0
            temp = i
            for j in range(self.log2n):
                reversed_index = (reversed_index << 1) | (temp & 1)
                temp >>= 1
            self.bit_reversal[i] = reversed_index

    def fft_optimized(self, x, inverse=False):
        """
        优化的FFT实现 - 修复算法错误

        Args:
            x: 输入信号
            inverse: 是否为逆变换

        Returns:
            FFT结果
        """
        # 修复：输入验证
        if len(x) != self.fft_length:
            raise ValueError(f"输入长度{len(x)}必须等于FFT长度{self.fft_length}")

        # 修复：复制输入避免修改原始数据
        x = x.copy()

        # 位反转重排 - 修复索引错误
        x = self._bit_reverse_copy(x)

        # 迭代FFT计算 - 修复蝴蝶操作
        n = self.fft_length

        for s in range(1, self.log2n + 1):
            m = 1 << s  # 当前段长度
            m2 = m // 2

            # 修复：正确的旋转因子索引
            for k in range(0, n, m):
                for j in range(m2):
                    # 修复：正确的蝴蝶操作索引
                    idx1 = k + j
                    idx2 = idx1 + m2

                    # 获取旋转因子 - 修复索引计算
                    twiddle_index = j * (n // m)
                    if twiddle_index >= len(self.twiddles):
                        twiddle_index = 0
                    w = self.twiddles[twiddle_index]

                    if inverse:
                        w = w.conjugate()  # 逆变换使用共轭

                    # 蝴蝶操作
                    t = w * x[idx2]
                    u = x[idx1]

                    x[idx1] = u + t
                    x[idx2] = u - t

        # 逆变换缩放 - 修复缩放因子
        if inverse:
            for i in range(n):
                x[i] /= n

        return x

    def _bit_reverse_copy(self, x):
        """位反转复制 - 修复索引错误"""
        n = len(x)
        result = [0] * n

        # 修复：使用预计算的位反转表
        for i in range(n):
            result[self.bit_reversal[i]] = x[i]

        return result

    # 保持原有的其他方法，只修复实现
    def fft_2d(self, matrix, inverse=False):
        """2D FFT实现 - 修复二维变换"""
        # 修复：输入验证
        if not matrix or len(matrix) != len(matrix[0]):
            raise ValueError("输入必须是方阵")

        if len(matrix) != self.fft_length:
            raise ValueError("矩阵尺寸必须匹配FFT长度")

        rows = len(matrix)
        cols = len(matrix[0])

        # 修复：行变换
        result = []
        for i in range(rows):
            result.append(self.fft_optimized(matrix[i], inverse))

        # 修复：列变换（转置后处理）
        result_t = [[result[j][i] for j in range(rows)] for i in range(cols)]
        result_t = [self.fft_optimized(row, inverse) for row in result_t]

        # 转置回来
        result = [[result_t[j][i] for j in range(cols)] for i in range(rows)]

        return result

# 保持原有的辅助函数不变
def validate_fft_result(original, transformed, tolerance=1e-10):
    """验证FFT结果 - 修复验证逻辑"""
    if len(original) != len(transformed):
        return False

    # 修复：更精确的能量守恒检查
    energy_original = sum(abs(x)**2 for x in original)
    energy_transformed = sum(abs(x)**2 for x in transformed)

    if abs(energy_original - energy_transformed) > tolerance:
        return False

    return True