"""Modul fritzbox test
"""

from unittest import TestCase
from src.netbox import NetBox
from dotenv import load_dotenv
import json
from ipaddress import IPv4Network
import random


load_dotenv()


class TestNetBoxAccess(TestCase):
    """TestClass for testing NetBox access"""

    def setUp(self) -> None:
        self.nb = NetBox()
        self.adresses = self.nb.get_ip_adresses()
        return super().setUp()

    def get_next_ipv4(self, ip: str, reserved: list) -> str:
        pre_network = IPv4Network(ip, strict=False)
        network = IPv4Network(
            str(pre_network.network_address) + "/" + str(pre_network.netmask)
        )
        hosts_iterator = (host for host in network.hosts() if str(host) not in reserved)
        retval = next(hosts_iterator)
        return format(retval) + "/" + ip.rsplit("/")[1]

    def get_next_free_ipv4(self, hosts: list) -> None:
        v4addresse_objects = list(
            filter(lambda x: x["family"]["value"] == 4, hosts["results"])
        )
        v4addresses = list(map(lambda x: x["address"], v4addresse_objects))
        reserved = list(map(lambda x: x.split("/")[0], v4addresses))
        return self.get_next_ipv4(v4addresses[0], reserved)

    def test_get_json(self):
        """Test the access of Netbox"""
        api = "/api/ipam/ip-addresses/"
        adresses = self.nb.get_json(api)
        # print(json.dumps(json.loads(adresses.text), indent=4))
        self.assertEqual(adresses.status_code, 200, "should return Status Code OK")
        adresses = json.loads(adresses.text)
        self.assertGreater(
            adresses["count"], 1, "At least 1 IP-adress should be assigned."
        )

    def test_create_ip_address(self):
        """Test create one IP Address and delete it"""
        if self.adresses.status_code != 200:
            self.fail("Can't get IP-Adresses")
        adresses = json.loads(self.adresses.text)
        # print(json.dumps(adresses, indent=4))
        adr = self.get_next_free_ipv4(adresses)
        # print(f"\nNew address: '{adr}'")
        res = self.nb.create_ip_address(
            adr, "Dummy_For_Tests_Only_" "_should_never_be_seen"
        )
        # print(res.text)
        # print(json.dumps(res.text, indent=4))
        self.assertEqual(res.status_code, 201, "should be created")
        data = json.loads(res.text)
        id = data["id"]
        # print(f"ID to be deleted: '{id}'")
        nres = self.nb.delete_ip_address(str(id))
        # print(nres.status_code)
        self.assertEqual(nres.status_code, 204, "should be deleted")

    def test_modify_ip_address(self):
        """patch IP Adress and DNS-Name"""
        if self.adresses.status_code != 200:
            self.fail("Can't get IP-Adresses")
        addresses = json.loads(self.adresses.text)
        adrList = list(
            filter(
                lambda x: x["address"] is not None
                and x["dns_name"] is not None
                and x["family"]["value"] == 4,
                addresses["results"],
            )
        )
        # print(json.dumps(adrList, indent=4))
        adr = adrList[random.randint(0, len(adrList) - 1)]
        # print(json.dumps(adr, indent=4))
        res = self.nb.modify_ip_address(adr["id"], adr["address"], adr["dns_name"])
        # print(res.status_code)
        # print(json.dumps(res.text, indent=4))
        self.assertEqual(res.status_code, 200, "should be modified")
