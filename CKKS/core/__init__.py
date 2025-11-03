"""
CKKS同态加密核心模块 - 修复导入循环问题
"""

import warnings
from typing import Dict, Any, Optional


class LazyImporter:
    """延迟导入解决循环依赖问题"""

    _modules = {
        'parameters': None,
        'key_generator': None,
        'encoder': None,
        'encryptor': None,
        'decryptor': None,
        'evaluator': None,
        'arithmetic_operations': None,
        'matrix_operations': None,
        'bootstrap_operations': None
    }

    def __getattr__(self, name: str) -> Any:
        if name == "CKKSParameters":
            if self._modules['parameters'] is None:
                from .parameters import CKKSParameters
                self._modules['parameters'] = CKKSParameters
            return self._modules['parameters']

        elif name == "CKKSKeyGenerator":
            if self._modules['key_generator'] is None:
                from .key_generator import CKKSKeyGenerator
                self._modules['key_generator'] = CKKSKeyGenerator
            return self._modules['key_generator']

        elif name == "CKKSEncoder":
            if self._modules['encoder'] is None:
                from .encoder import CKKSEncoder
                self._modules['encoder'] = CKKSEncoder
            return self._modules['encoder']

        elif name == "CKKSEncryptor":
            if self._modules['encryptor'] is None:
                from .encryptor import CKKSEncryptor
                self._modules['encryptor'] = CKKSEncryptor
            return self._modules['encryptor']

        elif name == "CKKSDecryptor":
            if self._modules['decryptor'] is None:
                from .decryptor import CKKSDecryptor
                self._modules['decryptor'] = CKKSDecryptor
            return self._modules['decryptor']

        elif name == "CKKSEvaluator":
            if self._modules['evaluator'] is None:
                from .evaluator import CKKSEvaluator
                self._modules['evaluator'] = CKKSEvaluator
            return self._modules['evaluator']

        elif name == "ArithmeticOperations":
            if self._modules['arithmetic_operations'] is None:
                from operations.arithmetic import ArithmeticOperations
                self._modules['arithmetic_operations'] = ArithmeticOperations
            return self._modules['arithmetic_operations']

        elif name == "MatrixOperations":
            if self._modules['matrix_operations'] is None:
                from operations.matrix_ops import MatrixOperations
                self._modules['matrix_operations'] = MatrixOperations
            return self._modules['matrix_operations']

        elif name == "BootstrappingOperations":
            if self._modules['bootstrap_operations'] is None:
                from operations.bootstrapping import BootstrappingOperations
                self._modules['bootstrap_operations'] = BootstrappingOperations
            return self._modules['bootstrap_operations']

        else:
            raise AttributeError(f"模块 {name} 不存在")


# 创建全局延迟导入器
_importer = LazyImporter()

# 导出主要类
CKKSParameters = _importer.CKKSParameters
CKKSKeyGenerator = _importer.CKKSKeyGenerator
CKKSEncoder = _importer.CKKSEncoder
CKKSEncryptor = _importer.CKKSEncryptor
CKKSDecryptor = _importer.CKKSDecryptor
CKKSEvaluator = _importer.CKKSEvaluator
ArithmeticOperations = _importer.ArithmeticOperations
MatrixOperations = _importer.MatrixOperations
BootstrappingOperations = _importer.BootstrappingOperations

__all__ = [
    'CKKSParameters',
    'CKKSKeyGenerator',
    'CKKSEncoder',
    'CKKSEncryptor',
    'CKKSDecryptor',
    'CKKSEvaluator',
    'ArithmeticOperations',
    'MatrixOperations',
    'BootstrappingOperations'
]

# 版本信息
__version__ = "1.0.0-fixed"
__author__ = "CKKS Project - Fixed Version"


# 初始化检查
def check_environment():
    """检查运行环境是否满足要求"""
    import sys
    import numpy as np

    if sys.version_info < (3, 8):
        warnings.warn("推荐使用 Python 3.8 或更高版本")

    np_version = tuple(map(int, np.__version__.split('.')[:2]))
    if np_version < (1, 19):
        warnings.warn("推荐使用 NumPy 1.19 或更高版本以获得最佳性能")


# 自动环境检查
check_environment()