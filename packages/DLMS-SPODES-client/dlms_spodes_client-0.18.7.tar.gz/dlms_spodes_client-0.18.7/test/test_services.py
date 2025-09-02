import unittest
from src.DLMS_SPODES_client.services import get_client_from_csv
from src.DLMS_SPODES_client.client import IDFactory


class TestType(unittest.TestCase):
    def test_get_from_csv(self):
        id_factory = IDFactory("#")
        res = get_client_from_csv("конфигурация GSM.csv", id_factory=id_factory)
        print(res)
