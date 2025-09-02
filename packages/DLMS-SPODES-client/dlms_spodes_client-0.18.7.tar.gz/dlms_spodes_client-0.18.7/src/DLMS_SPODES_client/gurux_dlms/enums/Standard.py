from enum import IntEnum


class Standard(IntEnum):
    """Used DLMS standard."""
    #Meter uses default DLMS IEC 62056 standard. https://dlms.com
    DLMS = 0
    #Meter uses India DLMS standard IS 15959-2. https://www.standardsbis.in
    INDIA = 1
    #Meter uses Italy DLMS standard UNI/TS 11291-11-2. https://uni.com
    ITALY = 2
    #Meter uses Saudi Arabia DLMS standard.
    SAUDI_ARABIA = 3
    #Meter uses IDIS DLMS standard. https://www.idis-association.com/
    IDIS = 4
    # Russia СПОДЭС
    RUSSIA = 99

