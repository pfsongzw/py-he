"""完整的公钥实现"""


class PublicKey:
    """公钥"""

    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

    def __str__(self):
        return 'p0: ' + str(self.p0) + '\n + p1: ' + str(self.p1)