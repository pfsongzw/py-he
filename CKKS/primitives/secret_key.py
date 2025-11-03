"""完整的密钥实现"""


class SecretKey:
    """私钥"""

    def __init__(self, s):
        self.s = s

    def __str__(self):
        return str(self.s)