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

    def get_json(self, api: str, payload: str = "") -> json:
        """GET json from api

        Args:
            api (str): api-call "/api/..../?id=x"
            payload (str, optional): normally not used for GET calls.
                                     Defaults to "".

        Returns:
            json: json load from api
        """
        url = self.nb_protocol+'://'+self.nb_host+':'+self.nb_port+api
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token ' + self.token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return json.loads(response.text)
