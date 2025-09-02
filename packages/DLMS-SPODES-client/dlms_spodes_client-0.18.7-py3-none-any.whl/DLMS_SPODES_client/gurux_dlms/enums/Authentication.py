from enum import IntEnum


class Authentication(IntEnum):
    """
    Authentication enumerates the authentication levels.
    """
    NONE = 0
    LOW = 1
    HIGH = 2
    HIGH_MD5 = 3
    HIGH_SHA1 = 4
    HIGH_GMAC = 5
    HIGH_SHA256 = 6
    HIGH_ECDSA = 7

    @classmethod
    def valueofString(cls, value):
        return Authentication[value.upper()]

    @classmethod
    def toString(cls, value):
        if value == 0:
            tmp = "None"
        elif value == 1:
            tmp = "Low"
        elif value == 2:
            tmp = "High"
        elif value == 3:
            tmp = "HighMd5"
        elif value == 4:
            tmp = "HighSha1"
        elif value == 5:
            tmp = "HighGmac"
        elif value == 6:
            tmp = "HighSha256"
        elif value == 7:
            tmp = "HighEcdsa"
        else:
            raise ValueError("Invalid Authentication value.")
        return tmp
