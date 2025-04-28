import requests
import json
import os
import logging

logger = logging.getLogger(__name__)

TOKEN = "TOKEN"
PROTOCOL = "PROTOCOL"
PORT = "PORT"
NETBOX = "NETBOX"


class NetBox:

    def __init__(self):
        self.token: str = os.getenv(TOKEN).strip()
        self.nb_protocol: str = os.getenv(PROTOCOL).strip()
        self.nb_host: str = os.getenv(NETBOX).strip()
        self.nb_port: str = os.getenv(PORT)
        self.ipAddrList: list = None
        self.cookies: list = None
        self.macList: list = None
        self.client: requests.Session = requests.Session()

    def get_url_base(self) -> str:
        """create base of url to Netbox without api part

        Returns:
            str: protocol + host + port
        """
        return self.nb_protocol + "://" + self.nb_host + ":" + self.nb_port

    def get_headers(self) -> dict:
        """create header for protected Netbox access

        Returns:
            dict: headers
        """
        return {
            "accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": "Token " + self.token,
        }

    def get_json(self, api: str, payload: str = "") -> requests.Response:
        """GET json from api

        Args:
            api (str): api-call "/api/..../?id=x"
            payload (str, optional): normally not used for GET calls.
                                     Defaults to "".

        Returns:
            json: json load from api
        """
        url = self.get_url_base() + api
        headers = self.get_headers()
        #        resp = requests.request("GET", url, headers=headers, data=payload)
        resp = self.client.get(url, headers=headers, data=payload)
        if resp.status_code != 200:
            logger.error(f"GET {url} returned {resp.status_code}")
        self.cookies = resp.cookies
        #        print(f"{resp.cookies}")
        return resp

    def get_status(self) -> requests.Response:
        """get status of Netbox instance

        Returns:
            requests.Response: html response
        """
        api = "/api/status/"
        return self.get_json(api)

    def get_ip_adresses(self) -> requests.Response:
        """get IP-Adresslist from netbox

        Returns:
            requests.Response: html response
        """
        api = "/api/ipam/ip-addresses/?limit=0"
        return self.get_json(api)

    def create_ip_address(
        self, ip: str, dns_name: str, tenant_id: int = 1
    ) -> requests.Response:
        """create one IP-Address in Netbox

        Args:
            ip (str): desired IP Address
            dns_name (str): desired DNS Name
            tenant_id (int, optional): ID of tenant. Defaults to 1.

        Returns:
            response from request
        """
        url = self.get_url_base() + "/api/ipam/ip-addresses/"
        headers = self.get_headers()
        payload = json.dumps(
            {
                "address": f"{ip}/24" if len(ip.split("/")) == 1 else ip,
                "dns_name": dns_name,
                "tenant": {"id": f"{tenant_id}"},
                "status": "reserved",
            }
        )
        #        resp = requests.request("POST", url, headers=headers, data=payload)
        resp = self.client.post(
            url, headers=headers, data=payload, cookies=self.cookies
        )
        if resp.status_code != 201:
            logger.error(f"POST {url} returned {resp.status_code}")
        self.cookies = resp.cookies
        return resp

    def delete_ip_address(self, id: str) -> requests.Response:
        """delete one IP-Address in Netbox

        Args:
            ip (int): ID of IP Address to be deleted

        Returns:
            response from request
        """
        url = self.get_url_base() + f"/api/ipam/ip-addresses/{id}/"
        headers = self.get_headers()
        payload = ""

        #        resp = requests.request("DELETE", url, headers=headers, data=payload)
        resp = self.client.delete(
            url, headers=headers, data=payload, cookies=self.cookies
        )
        if resp.status_code != 204:
            logger.error(f"DELETE {url} returned {resp.status_code}")
        self.cookies = resp.cookies
        return resp

    def modify_ip_address(self, id: str, ip: str, dns_name: str) -> requests.Response:
        """Modify desired IP Address with ID to given ip and dns_name

        Args:
            id (str): the ID to be modified
            ip (str): the IP to be set
            dns_name (str): the DNS-Name to be set

        Returns:
            requests.Response: http-Response
        """
        url = self.get_url_base() + f"/api/ipam/ip-addresses/{id}/"
        headers = self.get_headers()
        payload = json.dumps(
            {
                "address": f"{ip}/24" if len(ip.split("/")) == 1 else ip,
                "dns_name": dns_name,
            }
        )

        #        resp = requests.request("PATCH", url, headers=headers, data=payload)
        resp = self.client.patch(
            url, headers=headers, data=payload, cookies=self.cookies
        )
        if resp.status_code != 200:
            logger.error(f"PATCH {url} returned {resp.status_code}")
        self.cookies = resp.cookies
        return resp

    def get_mac_adresses(self, limit: int = 0) -> requests.Response:
        """get MAC-Adresslist from netbox

        Args:
            limit (int): get only limit of entries; Defaults to 0 (no limit)

        Returns:
            requests.Response: html response
        """
        api = f"/api/dcim/mac-addresses/?limit={limit}&brief=1"
        return self.get_json(api)

    def get_interface(self, id: str) -> requests.Response:
        """get desired interface

        Args:
            id (str): id of the interface

        Returns:
            requests.Response: http response
        """
        url = self.get_url_base() + f"/api/dcim/interfaces/{id}/"
        headers = self.get_headers()
        payload = ""

        #        resp = requests.request("GET", url, headers=headers, data=payload)
        resp = self.client.get(url, headers=headers, data=payload, cookies=self.cookies)
        if resp.status_code != 200:
            logger.error(f"GET {url} returned {resp.status_code}")
        self.cookies = resp.cookies
        return resp

    def modify_interface(self, id: str, macID: int) -> requests.Response:
        """get desired interface

        Args:
            id (str): id of the interface
            macID (int): mac ID to be set as primary

        Returns:
            requests.Response: http response
        """
        url = self.get_url_base() + f"/api/dcim/interfaces/{id}/"
        headers = self.get_headers()
        payload = json.dumps({"primary_mac_address": {"id": macID}})
        # print(f"PATCH {url} -> {payload}")
        #        resp = requests.request("PATCH", url, headers=headers, data=payload)
        resp = self.client.patch(
            url, headers=headers, data=payload, cookies=self.cookies
        )
        if resp.status_code != 200:
            logger.error(f"PATCH {url} returned {resp.status_code}")
        self.cookies = resp.cookies
        return resp

    def create_mac_address_if_it_doesnt_exist(
        self, mac: str, interface_id: int = 0
    ) -> requests.Response:
        """creates MAC Address if it doesn't exist in MAC-Addresses

        Args:
            mac (str): desired MAC Address
            interface_id (int, optional): ID of interface. Defaults to 0 (no interface)

        Returns:
            requests.Response: http response
        """
        macList = self._cached_macList()
        # print(f"\n\n{json.dumps(macList, indent=4)}\n\n")
        theMAC = mac.upper()
        mac_found = list(filter(lambda x: x["mac_address"] == theMAC, macList))
        # print(f"\nmac_found: {json.dumps(mac_found, indent=4)}\n")
        if len(mac_found) == 0:
            resp = self.create_mac_address(mac, interface_id)
            if resp.status_code == 201:
                newMac = json.loads(resp.text)
                self.macList.append(newMac)
                # print(f"newMAC generated and appended: {json.dumps(self.macList, indent=4)}")
            return resp
        else:
            id = int(mac_found[0]["id"])
            resp = self.get_mac_address(id)
            return resp

    def get_mac_address(self, id: int) -> requests.Response:
        """get mac address with id

        Args:
            id (int): id of requested MAC address

        Returns:
            requests.Response: html response
        """
        api = f"/api/dcim/mac-addresses/{id}/"
        return self.get_json(api)

    def delete_mac_address(self, id: int) -> requests.Response:
        """delete mac address with id

        Args:
            id (int): id of MAC address to be deleted

        Returns:
            requests.Response: html response
        """
        url = self.get_url_base() + f"/api/dcim/mac-addresses/{id}/"
        headers = self.get_headers()
        payload = ""

        #        resp = requests.request("DELETE", url, headers=headers, data=payload)
        resp = self.client.delete(
            url, headers=headers, data=payload, cookies=self.cookies
        )
        if resp.status_code != 204:
            logger.error(f"DELETE {url} returned {resp.status_code}")
        self.cookies = resp.cookies
        return resp

    def create_mac_address(self, mac: str, interface_id: int = 0) -> requests.Response:
        """create one MAC-Address in Netbox

        Args:
            mac (str): desired MAC Address
            interface_id (int, optional): ID of interface. Defaults to 0 (no interface)

        Returns:
            response from request
        """
        url = self.get_url_base() + "/api/dcim/mac-addresses/"
        headers = self.get_headers()
        if interface_id > 0:
            payload = json.dumps(
                {
                    "mac_address": mac,
                    "assigned_object_type": "dcim.interface",
                    "assigned_object_id": f"{interface_id}",
                }
            )
        else:
            payload = json.dumps(
                {
                    "mac_address": mac,
                }
            )

        #        resp = requests.request("POST", url, headers=headers, data=payload)
        resp = self.client.post(
            url, headers=headers, data=payload, cookies=self.cookies
        )
        if resp.status_code != 201:
            logger.error(f"POST {url} returned {resp.status_code}")
            self.cookies = resp.cookies
        return resp

# ----------- some helpers ---------------------------
    def _cached_macList(self) -> list[dict]:
        """create cached list of MAC addresses, if it doesn' exist

        Returns:
            list[dict]: list of cached MAC addresses
        """
        if self.macList is None:
            resp = self.get_mac_adresses()
            if resp.status_code != 200:
                self.macList = None
                return resp
            self.macList = json.loads(resp.text)["results"]
        return self.macList

    def get_v4_hosts(self, hosts: list) -> list:
        """filter only hosts with v4 addresses

        Args:
            hosts (list): list of hosts in Netbox

        Returns:
            list: list of hosts with v4 Addresses
        """
        return list(filter(lambda x: x["family"]["value"] == 4, hosts))

    def search_hosts_with_dns_name(self, hosts, name) -> list:
        """filter list of hosts with dns_name == name

        Args:
            hosts (_type_): list of hosts
            name (_type_): name to be found

        Returns:
            list: list of hosts with matching name
        """
        the_name = name.casefold()
        return list(filter(lambda x: x["dns_name"] == the_name, hosts))

    def search_hosts_with_ip_address(self, hosts, ip) -> list:
        """filter list of hosts with ip-address == ip

        Args:
            hosts (_type_): list of hosts
            ip (_type_): ip-address to be found

        Returns:
            list: list of hosts with matching ip-address
        """
        return list(filter(lambda x: x["address"].split("/")[0] == ip, hosts))

    def has_interface(self, host: dict) -> bool:
        """check whether host has interface

        Args:
            host (dict): Netbox host

        Returns:
            bool: true if assigned object is dcim.interface
        """
        return (
            host["assigned_object"] and host["assigned_object_type"] == "dcim.interface"
        )

    def search_macList_with_address(self, address: str) -> list:
        """filter list of mac-Adresses with address

        Args:
            address (str): specific MAC to be found

        Returns:
            list: list of MAC Addresses found
        """
        macList = self._cached_macList()
        theMac = address.upper()
        return list(filter(lambda x: x["mac_address"] == theMac, macList))
