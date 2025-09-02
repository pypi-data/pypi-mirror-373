from DLMS_SPODES.enums import AssociationResult, AcseServiceUser
from .enums import StateError, ServiceError, ErrorCode


class GXDLMSException(Exception):
    """
    DLMS specific exception class that has error description available from
    GetDescription method.
    """
    def __init__(self, errCode, serviceErr=None):
        if isinstance(errCode, StateError) and isinstance(serviceErr, ServiceError):
            Exception.__init__(self, "Meter returns " + self.getStateError(errCode) + " exception. " + self.getServiceError(serviceErr))
        elif isinstance(errCode, AssociationResult):
            Exception.__init__(self, F'Connection is {errCode.name} with {serviceErr.name}')
            self.result = errCode
            self.diagnostic = serviceErr
        else:
            Exception.__init__(self, self.getDescription(errCode))
        self.errorCode = errCode
        self.stateError = None
        self.exceptionServiceError = None

    #
    # Gets state error description.
    #
    # @param stateError
    #            State error enumerator value.
    # State error as an string.
    #
    @classmethod
    def getStateError(cls, stateError):
        if stateError == StateError.SERVICE_NOT_ALLOWED:
            ret = "Service not allowed"
        elif stateError == StateError.SERVICE_UNKNOWN:
            ret = "Service unknown"
        else:
            ret = "Invalid error code."
        return ret

    #
    # Gets service error description.
    #
    # @param serviceError
    #            Service error enumerator value.
    # Service error as an string.
    #
    @classmethod
    def getServiceError(cls, serviceError):
        if serviceError == ServiceError.OPERATION_NOT_POSSIBLE:
            ret = "Operation not possible"
        elif serviceError == ServiceError.SERVICE_NOT_SUPPORTED:
            ret = "Service not supported"
        elif serviceError == ServiceError.OTHER_REASON:
            ret = "Other reason"
        else:
            ret = "Invalid error code."
        return ret

    #
    # Get result as a string.
    #
    # @param result
    #            Enumeration value of AssociationResult.
    # String description of AssociationResult.
    #
    @classmethod
    def getResult(cls, result):
        if result == AssociationResult.REJECTED_PERMANENT:
            ret = "permanently rejected"
        elif result == AssociationResult.REJECTED_TRANSIENT:
            ret = "transient rejected"
        else:
            ret = "Invalid error code."
        return ret

    #
    # Get diagnostic as a string.
    #
    # @param value
    #            Enumeration value of SourceDiagnostic.
    # String description of SourceDiagnostic.
    #
    @classmethod
    def getDiagnostic(cls, value):
        if value == AcseServiceUser.NO_REASON_GIVEN:
            ret = "No reason is given."
        elif value == AcseServiceUser.APPLICATION_CONTEXT_NAME_NOT_SUPPORTED:
            ret = "The application context name is not supported."
        elif value == AcseServiceUser.NOT_RECOGNISED:
            ret = "The authentication mechanism name is not recognized."
        elif value == AcseServiceUser.MECHANISM_NAME_REGUIRED:
            ret = "Authentication mechanism name is required."
        elif value == AcseServiceUser.AUTHENTICATION_FAILURE:
            ret = "Authentication failure."
        elif value == AcseServiceUser.AUTHENTICATION_REQUIRED:
            ret = "Authentication is required."
        else:
            ret = "Invalid error code."
        return ret

    @classmethod
    def getDescription(cls, errCode):
        if errCode == ErrorCode.REJECTED:
            str_ = "Rejected"
        elif errCode == ErrorCode.OK:
            str_ = ""
        elif errCode == ErrorCode.HARDWARE_FAULT:
            str_ = "Access Error : Device reports a hardware fault."
        elif errCode == ErrorCode.TEMPORARY_FAILURE:
            str_ = "Access Error : Device reports a temporary failure."
        elif errCode == ErrorCode.READ_WRITE_DENIED:
            str_ = "Access Error : Device reports Read-Write denied."
        elif errCode == ErrorCode.UNDEFINED_OBJECT:
            str_ = "Access Error : Device reports a undefined object."
        elif errCode == ErrorCode.INCONSISTENT_CLASS:
            str_ = "Access Error : " + "Device reports a inconsistent Class or object."
        elif errCode == ErrorCode.UNAVAILABLE_OBJECT:
            str_ = "Access Error : Device reports a unavailable object."
        elif errCode == ErrorCode.UNMATCHED_TYPE:
            str_ = "Access Error : Device reports a unmatched type."
        elif errCode == ErrorCode.ACCESS_VIOLATED:
            str_ = "Access Error : Device reports scope of access violated."
        elif errCode == ErrorCode.DATA_BLOCK_UNAVAILABLE:
            str_ = "Access Error : Data Block Unavailable."
        elif errCode == ErrorCode.LONG_GET_OR_READ_ABORTED:
            str_ = "Access Error : Long Get Or Read Aborted."
        elif errCode == ErrorCode.NO_LONG_GET_OR_READ_IN_PROGRESS:
            str_ = "Access Error : No Long Get Or Read In Progress."
        elif errCode == ErrorCode.LONG_SET_OR_WRITE_ABORTED:
            str_ = "Access Error : Long Set Or Write Aborted."
        elif errCode == ErrorCode.NO_LONG_SET_OR_WRITE_IN_PROGRESS:
            str_ = "Access Error : No Long Set Or Write In Progress."
        elif errCode == ErrorCode.DATA_BLOCK_NUMBER_INVALID:
            str_ = "Access Error : Data Block Number Invalid."
        elif errCode == ErrorCode.OTHER_REASON:
            str_ = "Access Error : Other Reason."
        else:
            str_ = "Access Error : Unknown error."
        return str_
