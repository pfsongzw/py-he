"""完整的明文实现"""


class Plaintext:
    """明文"""

    def __init__(self, poly, scaling_factor=None):
        self.poly = poly
        self.scaling_factor = scaling_factor

    def __str__(self):
        return str(self.poly)