"""完整的旋转密钥实现"""


class RotationKey:
    """旋转密钥"""

    def __init__(self, r, key):
        self.rotation = r
        self.key = key

    def __str__(self):
        return 'Rotation: ' + str(self.rotation) + '\nr0: ' + str(self.key.p0) + '\nr1: ' + str(self.key.p1)