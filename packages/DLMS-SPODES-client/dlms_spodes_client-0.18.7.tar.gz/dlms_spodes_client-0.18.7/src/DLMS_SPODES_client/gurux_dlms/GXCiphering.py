from .enums import Security
from DLMS_SPODES.cosem_interface_classes.security_setup.ver1 import SecuritySuite
from .GXDLMSChippering import GXDLMSChippering
from . import AesGcmParameter
from .GXByteBuffer import GXByteBuffer


# pylint: disable=too-many-instance-attributes, too-many-function-args, too-many-public-methods
class GXCiphering:
    """
    Gurux DLMS/COSEM Transport security (Ciphering) settings.
    """
    def __init__(self, title):
        """
        # Constructor. Default values are from the Green Book.
        title: Used system title.
        """
        self.publicKeys = list()
        self.certificates = list()
        self.security = Security.NONE
        # System title.
        self.systemTitle = title
        # Block cipher key.
        self.blockCipherKey = bytearray((0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F))
        self.authenticationKey = bytearray((0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xDB, 0xDC, 0xDD, 0xDE, 0xDF))
        # Dedicated key.
        self.dedicatedKey = None
        # Certificates.
        self.certificates = None
        # Ephemeral key pair.
        self.ephemeralKeyPair = None
        # recipient system title.
        self.recipientSystemTitle = None
        # Invocation Counter.
        self.invocationCounter = 0
        # Used security suite.
        self.securitySuite = SecuritySuite.AES_GCM_128_AUT_ENCR_AND_AES_128_KEY_WRAP
        # Signing key pair.
        self.signingKeyPair = None
        # Client key agreement key pair.
        self.keyAgreementKeyPair = None
        # Target (Server or client) Public key.
        self.publicKeys = None
        # Shared secret is generated when connection is made.
        self.sharedSecret = None

    @classmethod
    def decrypt(cls, c, p, data):
        tmp = []
        p.sharedSecret = c.sharedSecret
        tmp = GXDLMSChippering.decryptAesGcm(p, data)
        c.sharedSecret = p.sharedSecret
        return tmp

    #
    # Cipher PDU.
    #      *
    # @param p
    #            Aes GCM Parameter.
    # @param data
    #            Plain text.
    # @return Secured data.
    #
    @classmethod
    def encrypt(cls, p, data) -> bytearray:
        if p.security != Security.NONE:
            tmp = GXDLMSChippering.encryptAesGcm(p, data)
            p.invocationCounter = p.invocationCounter + 1
            return tmp
        return data

    def reset(self):
        """
        Reset encrypt settings.
        """
        self.security = Security.NONE
        self.invocationCounter = 0

    def isCiphered(self):
        """
        Is ciphering used.
        """
        return self.security != Security.NONE

    #
    # Generate GMAC password from given challenge.
    #      *
    # @param challenge
    #            Client to Server or Server to Client challenge.
    # @return Generated challenge.
    #
    def generateGmacPassword(self, challenge):
        p = AesGcmParameter(0x10, self.systemTitle, self.blockCipherKey, self.authenticationKey)
        p.security = Security.AUTHENTICATION
        p.invocationCounter = self.invocationCounter
        bb = GXByteBuffer()
        GXDLMSChippering.encryptAesGcm(p, challenge)
        bb.setUInt8(0x10)
        bb.setUInt32(self.invocationCounter)
        bb.set(p.countTag)
        return bb.array()

    def getSecurity(self):
        """
        Used security.
        """
        return self.security

    def setSecurity(self, value):
        """
        Used security.
        """
        self.security = value

    def getSystemTitle(self):
        """
        System title.
        """
        return self.systemTitle

    #
    # Recipient system Title.
    #
    def getRecipientSystemTitle(self):
        """
        Recipient system Title.
        """
        return self.recipientSystemTitle

    def getBlockCipherKey(self):
    # Block cipher key.
        return self.blockCipherKey

    def getAuthenticationKey(self):
    # Authentication key.
        return self.authenticationKey

    def setAuthenticationKey(self, value):
        # Authentication key.
        self.authenticationKey = value

    def getInvocationCounter(self):
        # Invocation counter.
        return self.invocationCounter

    def getSecuritySuite(self):
        # Used security suite.
        return self.securitySuite

    def getEphemeralKeyPair(self):
        # Ephemeral key pair.
        return self.ephemeralKeyPair

    def setEphemeralKeyPair(self, value):
        # Ephemeral key pair.
        self.ephemeralKeyPair = value

    def getKeyAgreementKeyPair(self):
        # Client's key agreement key pair.
        return self.keyAgreementKeyPair

    def setKeyAgreementKeyPair(self, value):
        # Client's key agreement key pair.
        self.keyAgreementKeyPair = value

    def getPublicKeys(self):
        # Target (Server or client) Public key.
        return self.publicKeys

    def getCertificates(self):
        # Available certificates.
        return self.certificates

    def getSigningKeyPair(self):
        # Signing key pair.
        return self.signingKeyPair

    def setSigningKeyPair(self, value):
        # Signing key pair.
        self.signingKeyPair = value

    def getSharedSecret(self):
        # Shared secret is generated when connection is made.
        return self.sharedSecret

    def setSharedSecret(self, value):
        # Shared secret is generated when connection is made.
        self.sharedSecret = value

    def getDedicatedKey(self):
        # Dedicated key.
        return self.dedicatedKey

    def setDedicatedKey(self, value):
        # Dedicated key.
        self.dedicatedKey = value
