from enum import IntEnum


class MBusEncryptionMode(IntEnum):
    """Encryption modes."""

    # Encryption is not used.
    NONE = 0

    # AES with Counter Mode = CTR) noPadding and IV.
    AES_128 = 1

    # DES with Cipher Block Chaining Mode = CBC).
    DES_CBC = 2

    # DES with Cipher Block Chaining Mode = CBC) and Initial Vector.
    DES_CBC_IV = 3

    # AES with Cipher Block Chaining Mode = CBC) and Initial Vector.
    AES_CBC_IV = 5

    # AES 128 with Cipher Block Chaining Mode = CBC) and dynamic key and
    # Initial Vector with 0.
    AES_CBC_IV0 = 7

    # TLS
    Tls = 13
