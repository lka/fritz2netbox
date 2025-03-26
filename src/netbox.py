import requests
import json
import os

TOKEN = 'TOKEN'


class NetBox():

    def __init__(self, host: str = 'homeassistant', port: str = '5580'):
        self.token = os.getenv(TOKEN)
        self.nb_protocol = 'http'
        self.nb_host = host
        self.nb_port = port

    def get_url_base(self) -> str:
        """create base of url to  nezbox without api part

        Returns:
            str: protocol + host + port
        """
        return self.nb_protocol+'://'+self.nb_host+':'+self.nb_port

    def get_headers(self) -> dict:
        """create header for protected Netbox access

        Returns:
            dict: headers
        """
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Token ' + self.token
        }

    def get_json(self, api: str, payload: str = "") -> json:
        """GET json from api

        Args:
            api (str): api-call "/api/..../?id=x"
            payload (str, optional): normally not used for GET calls.
                                     Defaults to "".

        Returns:
            json: json load from api
        """
        url = self.get_url_base()+api
        headers = self.get_headers()
        response = requests.request("GET", url, headers=headers,
                                    data=payload)
        return json.loads(response.text)

    def create_ip_address(self, ip: str, dns_name: str, tenant_id: int = 1)\
            -> requests.Response:
        """create one IP-Address in Netbox

        Args:
            ip (str): desired IP Address
            dns_name (str): desired DNS Name
            tenant_id (int, optional): ID of tenant. Defaults to 1.

        Returns:
            response from request
        """
        url = self.get_url_base()+'/api/ipam/ip-addresses/'
        headers = self.get_headers()
        payload = json.dumps(
            {
                "address": f"{ip}/24" if len(ip.split('/')) == 1 else ip,
                "dns_name": dns_name,
                "tenant": {
                    "id": f"{tenant_id}"
                },
                "status": "reserved"
            }
        )

        return requests.request("POST", url, headers=headers,
                                data=payload)

    def delete_ip_address(self, id: str) -> requests.Response:
        """delete one IP-Address in Netbox

        Args:
            ip (int): ID of IP Address to be deleted

        Returns:
            response from request
        """
        url = self.get_url_base()+f"/api/ipam/ip-addresses/{id}/"
        headers = self.get_headers()
        payload = ""

        return requests.request("DELETE", url, headers=headers,
                                data=payload)
