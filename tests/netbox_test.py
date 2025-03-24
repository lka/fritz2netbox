"""Modul fritzbox test
"""

from unittest import TestCase
from src.netbox import NetBox
from dotenv import load_dotenv
import json


load_dotenv()


class TestNetBoxAccess(TestCase):
    """TestClass for testing NetBox access
    """

    def setUp(self) -> None:
        self.nb = NetBox()
        return super().setUp()

    def test_get_json_adresses(self):
        api = '/api/ipam/ip-addresses/'
        adresses = self.nb.get_json(api)
        print(json.dumps(adresses, indent=4))
        self.assertGreater(adresses["count"], 0,
                           'At least 1 IP-adress should be assigned.')
