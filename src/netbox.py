import requests
import json
import os
import logging

logger = logging.getLogger(__name__)

TOKEN = "TOKEN"


class NetBox:

    def __init__(self, host: str = "homeassistant", port: str = "5580"):
        self.token = os.getenv(TOKEN)
        self.nb_protocol = "http"
        self.nb_host = host
        self.nb_port = port
        self.ipAddrList = None
        self.cookies = None
        self.client = requests.Session()

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
        if self.cookies:
            # print(f"cookie found {self.cookies}")
            # for cookie in self.cookies:
            #     print(cookie.name, cookie.value, cookie.domain)
            return {
                "accept": "*/*",
                "Content-Type": "application/json",
            }
        else:
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
        resp = self.client.post(url, headers=headers, data=payload, cookies=self.cookies)
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
        resp = self.client.delete(url, headers=headers, data=payload, cookies=self.cookies)
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
        resp = self.client.patch(url, headers=headers, data=payload, cookies=self.cookies)
        if resp.status_code != 200:
            logger.error(f"PATCH {url} returned {resp.status_code}")
        self.cookies = resp.cookies
        return resp

    def get_mac_adresses(self) -> requests.Response:
        """get MAC-Adresslist from netbox

        Returns:
            requests.Response: html response
        """
        api = "/api/dcim/mac-addresses/?limit=0"
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
        payload = json.dumps(
            {"pimary_mac_address": {"id": f"{macID}"}}
        )
        print(f"PATCH {url} -> {payload}")
#        resp = requests.request("PATCH", url, headers=headers, data=payload)
        resp = self.client.patch(url, headers=headers, data=payload, cookies=self.cookies)
        if resp.status_code != 200:
            logger.error(f"PATCH {url} returned {resp.status_code}")
        self.cookies = resp.cookies
        return resp

    def create_mac_address_if_it_doesnt_exist(
        self, mac: str, interface_id: int
    ) -> requests.Response:
        """creates MAC Address if it doesn't exist in MAC-Addresses

        Args:
            mac (str): desired MAC Address
            interface_id (int): ID of interface.

        Returns:
            requests.Response: http response
        """
        resp = self.get_mac_adresses()
        if resp.status_code != 200:
            return resp
        macList = json.loads(resp.text)["results"]
        # print(f"\n\n{json.dumps(macList, indent=4)}\n\n")
        if len(list(filter(lambda x: x["mac_address"] == mac, macList))) == 0:
            resp = self.create_mac_address(mac, interface_id)
        return resp

    def create_mac_address(self, mac: str, interface_id: int) -> requests.Response:
        """create one IP-Address in Netbox

        Args:
            mac (str): desired MAC Address
            interface_id (int): ID of interface.

        Returns:
            response from request
        """
        url = self.get_url_base() + "/api/dcim/mac-addresses/"
        headers = self.get_headers()
        payload = json.dumps(
            {
                "mac_address": mac,
                "assigned_object_type": "dcim.interface",
                "assigned_object_id": f"{interface_id}",
            }
        )

#        resp = requests.request("POST", url, headers=headers, data=payload)
        resp = self.client.post(url, headers=headers, data=payload, cookies=self.cookies)
        if resp.status_code != 201:
            logger.error(f"POST {url} returned {resp.status_code}")
            self.cookies = resp.cookies
        return resp

    def get_v4_hosts(self, hosts: list) -> list:
        """get only hosts with v4 addresses

        Args:
            hosts (list): list of hosts in Netbox

        Returns:
            list: list of hosts with v4 Addresses
        """
        return list(filter(lambda x: x["family"]["value"] == 4, hosts))

    def search_hosts_with_dns_name(self, hosts, name) -> list:
        """get list of hosts with dns_name == name

        Args:
            hosts (_type_): list of hosts
            name (_type_): name to be found

        Returns:
            list: list of hosts with matching name
        """
        return list(filter(lambda x: x["dns_name"] == name, hosts))

    def search_hosts_with_ip_address(self, hosts, ip) -> list:
        """get list of hosts with ip-address == ip

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

    def search_macList_with_address(self, macList: list, address: str) -> list:
        """get list of mac-Adresses with address

        Args:
            macList (list): list of MAC - Addresses
            address (str): specific MAC to be found

        Returns:
            list: list of MAC Addresses found
        """
        return list(filter(lambda x: x["mac_address"] == address, macList))
