"""Modul fritzbox test
"""

from unittest import TestCase
from src.fritzbox import FritzBox
from dotenv import load_dotenv

load_dotenv()


class TestFritzBoxAccess(TestCase):
    """TestClass for testing FritzBox access"""

    def setUp(self) -> None:
        self.fb = FritzBox()
        return super().setUp()

    def test_get_hosts(self) -> None:
        """Test that get_hosts() returns at least FritzBox"""
        hosts = self.fb.get_hosts()
        hostnames = list(map(lambda x: x["name"], hosts))
        # print(hostnames)
        self.assertIn("fritz.box", hostnames, "Hostnames contains 'fritz.box'")
