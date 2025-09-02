from enum import IntEnum


class BerType(IntEnum):
    """ BER encoding enumeration values. Todo: rewrite, use https://ru.wikipedia.org/wiki/X.690"""
    EOC = 0x00
    BOOLEAN = 0x1
    INTEGER = 0x2
    BIT_STRING = 0x3
    OCTET_STRING = 0x4
    NULL = 0x5
    OBJECT_IDENTIFIER = 0x6
    OBJECT_DESCRIPTOR = 7
    EXTERNAL = 8
    REAL = 9
    ENUMERATED = 10
    SEQUENCE = 0x10
    SET = 0x11
    UTF8STRING = 12
    NUMERIC_STRING = 18
    PRINTABLE_STRING = 19
    TELETEX_STRING = 20
    VIDEOTEX_STRING = 21
    IA5_STRING = 22
    UTC_TIME = 23
    GENERALIZED_TIME = 24
    GRAPHIC_STRING = 25
    VISIBLE_STRING = 26
    GENERAL_STRING = 27
    UNIVERSAL_STRING = 28
    BMP_STRING = 30
    APPLICATION = 0x40
    CONTEXT = 0x80
    PRIVATE = 0xc0
    CONSTRUCTED = 0x20
