from DLMS_SPODES.enums import ServiceError, ConfirmedServiceError
from .enums.ApplicationReference import ApplicationReference
from .enums.VdeStateError import VdeStateError
from .enums.HardwareResource import HardwareResource
from .enums.Definition import Definition
from .enums.Access import Access
from .enums.Service import Service
from .enums.Initiate import Initiate
from .enums.LoadDataSet import LoadDataSet
from .enums.Task import Task


class GXDLMSConfirmedServiceError(Exception):
    """
    DLMS specific exception class that has error description available from getDescription method.
    """

    #
    # Constructor for Confirmed ServiceError.
    #
    # @param service
    # @param type
    # @param value
    #
    def __init__(self, service=None, type_=None, value=0):
        Exception.__init__(self, "ServiceError " + self.__getConfirmedServiceError(service) + " exception. " + self.__getServiceError(type_) + " " + self.__getServiceErrorValue(type_, value))
        self.confirmedServiceError = service
        self.serviceError = type_
        self.serviceErrorValue = value

    @classmethod
    def __getConfirmedServiceError(cls, stateError):
        str_ = ""
        if stateError == ConfirmedServiceError.INITIATE_ERROR:
            str_ = "Initiate Error"
        elif stateError == ConfirmedServiceError.READ:
            str_ = "Read"
        elif stateError == ConfirmedServiceError.WRITE:
            str_ = "Write"
        return str_

    @classmethod
    def __getServiceError(cls, error):
        str_ = ""
        if error == ServiceError.APPLICATION_REFERENCE:
            str_ = "Application reference"
        elif error == ServiceError.HARDWARE_RESOURCE:
            str_ = "Hardware resource"
        elif error == ServiceError.VDE_STATE_ERROR:
            str_ = "Vde state error"
        elif error == ServiceError.SERVICE:
            str_ = "Service"
        elif error == ServiceError.DEFINITION:
            str_ = "Definition"
        elif error == ServiceError.ACCESS:
            str_ = "Access"
        elif error == ServiceError.INITIATE:
            str_ = "Initiate"
        elif error == ServiceError.LOAD_DATA_SET:
            str_ = "Load dataset"
        elif error == ServiceError.TASK:
            str_ = "Task"
        elif error == ServiceError.OTHER:
            str_ = "Other Error"
        return str_

    @classmethod
    def __getServiceErrorValue(cls, error, value):
        str_ = ""
        if error == ServiceError.APPLICATION_REFERENCE:
            str_ = str(ApplicationReference(value))
        elif error == ServiceError.HARDWARE_RESOURCE:
            str_ = str(HardwareResource(value))
        elif error == ServiceError.VDE_STATE_ERROR:
            str_ = str(VdeStateError(value))
        elif error == ServiceError.SERVICE:
            str_ = str(Service(value))
        elif error == ServiceError.DEFINITION:
            str_ = str(Definition(value))
        elif error == ServiceError.ACCESS:
            str_ = str(Access(value))
        elif error == ServiceError.INITIATE:
            str_ = str(Initiate(value))
        elif error == ServiceError.LOAD_DATASET:
            str_ = str(LoadDataSet(value))
        elif error == ServiceError.TASK:
            str_ = str(Task(value))
        elif error == ServiceError.OTHER_ERROR:
            str_ = str(value)
        return str_
