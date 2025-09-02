from .enums.Security import Security
from .CountType import CountType
from DLMS_SPODES.cosem_interface_classes.security_setup.ver1 import SecuritySuite


class AesGcmParameter:
    def __init__(self, tag=0, systemTitle=None, blockCipherKey=None, authenticationKey=None):
        """
        Constructor.
        tag : Tag.
        systemTitle : System title.
        blockCipherKey : Block cipher key.
        authenticationKey : Authentication key.
        """
        self.tag = tag
        self.security = Security.NONE
        self.invocationCounter = 0
        # Used security suite.
        self.securitySuite = SecuritySuite.AES_GCM_128_AUT_ENCR_AND_AES_128_KEY_WRAP
        self.blockCipherKey = blockCipherKey
        self.authenticationKey = authenticationKey
        self.systemTitle = systemTitle
        self.recipientSystemTitle = None
        # Count type.
        self.type_ = CountType.PACKET
        self.dateTime = None
        self.otherInformation = None
        self.countTag = None
        self.keyParameters = None
        self.keyCipheredData = None
        self.cipheredContent = None
        # Shared secret is generated when connection is made.
        self.sharedSecret = None
        # xml settings. This is used only on xml parser.
        self.xml = None
        # System title is not send on pre-established connecions.
        self.ignoreSystemTitle = False
