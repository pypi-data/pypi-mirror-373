import unittest
from src.DLMS_SPODES_client.logger import LogLevel


class TestType(unittest.TestCase):
    def test_connect(self):
        print(LogLevel.STATE)