from enum import IntEnum


class Command(IntEnum):
    """DLMS commands."""

    NONE = 0
    INITIATE_REQUEST = 0x1
    INITIATE_RESPONSE = 0x8
    READ_REQUEST = 0x5
    READ_RESPONSE = 0xC
    WRITE_REQUEST = 0x6
    WRITE_RESPONSE = 0xD
    GET_REQUEST = 0xC0
    GET_RESPONSE = 0xC4
    SET_REQUEST = 0xC1
    SET_RESPONSE = 0xC5
    METHOD_REQUEST = 0xC3
    METHOD_RESPONSE = 0xC7
    DISCONNECT_MODE = 0x1F
    UNACCEPTABLE_FRAME = 0x97
    SNRM = 0x93
    UA = 0x73
    AARQ = 0x60
    AARE = 0x61
    DISCONNECT_REQUEST = 0x53
    RELEASE_REQUEST = 0x62
    RELEASE_RESPONSE = 0x63
    CONFIRMED_SERVICE_ERROR = 0x0E
    EXCEPTION_RESPONSE = 0xD8
    GENERAL_BLOCK_TRANSFER = 0xE0
    ACCESS_REQUEST = 0xD9
    ACCESS_RESPONSE = 0xDA
    DATA_NOTIFICATION = 0x0F
    GLO_GET_REQUEST = 0xC8
    GLO_GET_RESPONSE = 0xCC
    GLO_SET_REQUEST = 0xC9
    GLO_SET_RESPONSE = 0xCD
    GLO_EVENT_NOTIFICATION = 0xCA
    GLO_METHOD_REQUEST = 0xCB
    GLO_METHOD_RESPONSE = 0xCF
    GLO_INITIATE_REQUEST = 0x21
    GLO_READ_REQUEST = 37
    GLO_WRITE_REQUEST = 38
    GLO_INITIATE_RESPONSE = 40
    GLO_READ_RESPONSE = 44
    GLO_WRITE_RESPONSE = 45
    GENERAL_GLO_CIPHERING = 0xDB
    GENERAL_DED_CIPHERING = 0xDC
    GENERAL_CIPHERING = 0xDD
    INFORMATION_REPORT = 0x18
    EVENT_NOTIFICATION = 0xC2
    DED_INITIATE_REQUEST = 65
    DED_READ_REQUEST = 69
    DED_WRITE_REQUEST = 70
    DED_INITIATE_RESPONSE = 72
    DED_READ_RESPONSE = 76
    DED_WRITE_RESPONSE = 77
    DED_CONFIRMED_SERVICE_ERROR = 78
    DED_UNCONFIRMED_WRITE_REQUEST = 86
    DED_INFORMATION_REPORT_REQUEST = 88
    DED_GET_REQUEST = 0xD0
    DED_GET_RESPONSE = 0xD4
    DED_SET_REQUEST = 0xD1
    DED_SET_RESPONSE = 0xD5
    DED_EVENT_NOTIFICATION = 0xD2
    DED_METHOD_REQUEST = 0xD3
    DED_METHOD_RESPONSE = 0xD7
    GATEWAY_REQUEST = 0xE6
    GATEWAY_RESPONSE = 0xE7

    @classmethod
    def toString(cls, value):
        str_ = None
        if value == Command.NONE:
            str_ = "None"
        elif value == Command.INITIATE_REQUEST:
            str_ = "InitiateRequest"
        elif value == Command.INITIATE_RESPONSE:
            str_ = "InitiateResponse"
        elif value == Command.READ_REQUEST:
            str_ = "ReadRequest"
        elif value == Command.READ_RESPONSE:
            str_ = "ReadResponse"
        elif value == Command.WRITE_REQUEST:
            str_ = "WriteRequest"
        elif value == Command.WRITE_RESPONSE:
            str_ = "WriteResponse"
        elif value == Command.GET_REQUEST:
            str_ = "GetRequest"
        elif value == Command.GET_RESPONSE:
            str_ = "GetResponse"
        elif value == Command.SET_REQUEST:
            str_ = "SetRequest"
        elif value == Command.SET_RESPONSE:
            str_ = "SetResponse"
        elif value == Command.METHOD_REQUEST:
            str_ = "MethodRequest"
        elif value == Command.METHOD_RESPONSE:
            str_ = "MethodResponse"
        elif value == Command.UNACCEPTABLE_FRAME:
            str_ = "UnacceptableFrame"
        elif value == Command.SNRM:
            str_ = "Snrm"
        elif value == Command.UA:
            str_ = "Ua"
        elif value == Command.AARQ:
            str_ = "Aarq"
        elif value == Command.AARE:
            str_ = "Aare"
        elif value == Command.DISCONNECT_REQUEST:
            str_ = "Disc"
        elif value == Command.RELEASE_REQUEST:
            str_ = "DisconnectRequest"
        elif value == Command.RELEASE_RESPONSE:
            str_ = "DisconnectResponse"
        elif value == Command.CONFIRMED_SERVICE_ERROR:
            str_ = "ConfirmedServiceError"
        elif value == Command.EXCEPTION_RESPONSE:
            str_ = "ExceptionResponse"
        elif value == Command.GENERAL_BLOCK_TRANSFER:
            str_ = "GeneralBlockTransfer"
        elif value == Command.ACCESS_REQUEST:
            str_ = "AccessRequest"
        elif value == Command.ACCESS_RESPONSE:
            str_ = "AccessResponse"
        elif value == Command.DATA_NOTIFICATION:
            str_ = "DataNotification"
        elif value == Command.GLO_GET_REQUEST:
            str_ = "GloGetRequest"
        elif value == Command.GLO_GET_RESPONSE:
            str_ = "GloGetResponse"
        elif value == Command.GLO_SET_REQUEST:
            str_ = "GloSetRequest"
        elif value == Command.GLO_SET_RESPONSE:
            str_ = "GloSetResponse"
        elif value == Command.GLO_EVENT_NOTIFICATION:
            str_ = "GloEventNotification"
        elif value == Command.GLO_METHOD_REQUEST:
            str_ = "GloMethodRequest"
        elif value == Command.GLO_METHOD_RESPONSE:
            str_ = "GloMethodResponse"
        elif value == Command.GLO_INITIATE_REQUEST:
            str_ = "GloInitiateRequest"
        elif value == Command.GLO_READ_REQUEST:
            str_ = "GloReadRequest"
        elif value == Command.GLO_WRITE_REQUEST:
            str_ = "GloWriteRequest"
        elif value == Command.GLO_INITIATE_RESPONSE:
            str_ = "GloInitiateResponse"
        elif value == Command.GLO_READ_RESPONSE:
            str_ = "GloReadResponse"
        elif value == Command.GLO_WRITE_RESPONSE:
            str_ = "GloWriteResponse"
        elif value == Command.GENERAL_GLO_CIPHERING:
            str_ = "GeneralGloCiphering"
        elif value == Command.GENERAL_DED_CIPHERING:
            str_ = "GeneralDedCiphering"
        elif value == Command.GENERAL_CIPHERING:
            str_ = "GeneralCiphering"
        elif value == Command.INFORMATION_REPORT:
            str_ = "InformationReport"
        elif value == Command.EVENT_NOTIFICATION:
            str_ = "EventNotification"
        elif value == Command.DED_GET_REQUEST:
            str_ = "DedGetRequest"
        elif value == Command.DED_GET_RESPONSE:
            str_ = "DedGetResponse"
        elif value == Command.DED_SET_REQUEST:
            str_ = "DedSetRequest"
        elif value == Command.DED_SET_RESPONSE:
            str_ = "DedSetResponse"
        elif value == Command.DED_EVENT_NOTIFICATION:
            str_ = "DedEventNotification"
        elif value == Command.DED_METHOD_REQUEST:
            str_ = "DedMethodRequest"
        elif value == Command.GATEWAY_REQUEST:
            str_ = "GatewayRequest "
        elif value == Command.GATEWAY_RESPONSE:
            str_ = "GatewayResponse "
        else:
            raise ValueError(str(value))
        return str_

    @classmethod
    def value_of(cls, value):
        if "None".lower() == value.lower():
            ret = Command.NONE
        elif "InitiateRequest".lower() == value.lower():
            ret = Command.INITIATE_REQUEST
        elif "InitiateResponse".lower() == value.lower():
            ret = Command.INITIATE_RESPONSE
        elif "ReadRequest".lower() == value.lower():
            ret = Command.READ_REQUEST
        elif "ReadResponse".lower() == value.lower():
            ret = Command.READ_RESPONSE
        elif "WriteRequest".lower() == value.lower():
            ret = Command.WRITE_REQUEST
        elif "WriteRequest".lower() == value.lower():
            ret = Command.WRITE_RESPONSE
        elif "WriteResponse".lower() == value.lower():
            ret = Command.WRITE_RESPONSE
        elif "GetRequest".lower() == value.lower():
            ret = Command.GET_REQUEST
        elif "GetResponse".lower() == value.lower():
            ret = Command.GET_RESPONSE
        elif "SetRequest".lower() == value.lower():
            ret = Command.SET_REQUEST
        elif "SetResponse".lower() == value.lower():
            ret = Command.SET_RESPONSE
        elif "MethodRequest".lower() == value.lower():
            ret = Command.METHOD_REQUEST
        elif "MethodResponse".lower() == value.lower():
            ret = Command.METHOD_RESPONSE
        elif "UnacceptableFrame".lower() == value.lower():
            ret = Command.UNACCEPTABLE_FRAME
        elif "Snrm".lower() == value.lower():
            ret = Command.SNRM
        elif "Ua".lower() == value.lower():
            ret = Command.UA
        elif "Aarq".lower() == value.lower():
            ret = Command.AARQ
        elif "Aare".lower() == value.lower():
            ret = Command.AARE
        elif "Disc".lower() == value.lower():
            ret = Command.DISCONNECT_REQUEST
        elif "DisconnectRequest".lower() == value.lower():
            ret = Command.RELEASE_REQUEST
        elif "DisconnectResponse".lower() == value.lower():
            ret = Command.RELEASE_RESPONSE
        elif "ConfirmedServiceError".lower() == value.lower():
            ret = Command.CONFIRMED_SERVICE_ERROR
        elif "ExceptionResponse".lower() == value.lower():
            ret = Command.EXCEPTION_RESPONSE
        elif "GeneralBlockTransfer".lower() == value.lower():
            ret = Command.GENERAL_BLOCK_TRANSFER
        elif "AccessRequest".lower() == value.lower():
            ret = Command.ACCESS_REQUEST
        elif "AccessResponse".lower() == value.lower():
            ret = Command.ACCESS_RESPONSE
        elif "DataNotification".lower() == value.lower():
            ret = Command.DATA_NOTIFICATION
        elif "GloGetRequest".lower() == value.lower():
            ret = Command.GLO_GET_REQUEST
        elif "GloGetResponse".lower() == value.lower():
            ret = Command.GLO_GET_RESPONSE
        elif "GloSetRequest".lower() == value.lower():
            ret = Command.GLO_SET_REQUEST
        elif "GloSetResponse".lower() == value.lower():
            ret = Command.GLO_SET_RESPONSE
        elif "GloEventNotification".lower() == value.lower():
            ret = Command.GLO_EVENT_NOTIFICATION
        elif "GloMethodRequest".lower() == value.lower():
            ret = Command.GLO_METHOD_REQUEST
        elif "GloMethodResponse".lower() == value.lower():
            ret = Command.GLO_METHOD_RESPONSE
        elif "GloInitiateRequest".lower() == value.lower():
            ret = Command.GLO_INITIATE_REQUEST
        elif "GloReadRequest".lower() == value.lower():
            ret = Command.GLO_READ_REQUEST
        elif "GloWriteRequest".lower() == value.lower():
            ret = Command.GLO_WRITE_REQUEST
        elif "GloInitiateResponse".lower() == value.lower():
            ret = Command.GLO_INITIATE_RESPONSE
        elif "GloReadResponse".lower() == value.lower():
            ret = Command.GLO_READ_RESPONSE
        elif "GloWriteResponse".lower() == value.lower():
            ret = Command.GLO_WRITE_RESPONSE
        elif "GeneralGloCiphering".lower() == value.lower():
            ret = Command.GENERAL_GLO_CIPHERING
        elif "GeneralDedCiphering".lower() == value.lower():
            ret = Command.GENERAL_DED_CIPHERING
        elif "GeneralCiphering".lower() == value.lower():
            ret = Command.GENERAL_CIPHERING
        elif "InformationReport".lower() == value.lower():
            ret = Command.INFORMATION_REPORT
        elif "EventNotification".lower() == value.lower():
            ret = Command.EVENT_NOTIFICATION
        elif "GatewayRequest".lower() == value.lower():
            ret = Command.GATEWAY_REQUEST
        elif "GatewayResponse".lower() == value.lower():
            ret = Command.GATEWAY_RESPONSE
        else:
            raise ValueError(value)
        return ret
