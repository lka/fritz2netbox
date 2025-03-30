import os
from fritzconnection.lib.fritzhosts import FritzHosts

fritzBoxIP = "FB_IP"
fritzBoxUser = "USER"
fritzBoxPWD = "PASSWORD"


class FritzBox:

    def __init__(self):
        self.fh = FritzHosts(
            address=os.getenv(fritzBoxIP),
            user=os.getenv(fritzBoxUser),
            password=os.getenv(fritzBoxPWD),
        )

    def get_hosts(self):
        return self.fh.get_hosts_info()

    def get_active_hosts(self, hosts: list[dict], ignore_list: list = []) -> list[dict]:
        """get active hosts which are not in ignore_list

        Args:
            hosts (list[dict]): list of hosts coming from fritz!box
            ignore_list (list, optional): list of ip addresses to be ignored.
            Defaults to [].

        Returns:
            list[dict]: list of active hosts
        """
        if len(hosts) == 0:
            return []
        return list(
            filter(
                lambda x: x["status"]
                and len(x["ip"]) > 0
                and x["ip"] not in ignore_list,
                hosts,
            )
        )

    def print_hosts(self, hosts: list) -> None:
        """print list of hosts

        Args:
            hosts (list): list of hosts coming from fritz!box
        """
        for index, host in enumerate(hosts, start=1):
            status = "active" if host["status"] else "-"
            ip = host["ip"] if host["ip"] else "-"
            mac = host["mac"] if host["mac"] else "-"
            hn = host["name"]
            print(f"{index:>3}: {ip:<16} {hn:<42} {mac:<17}   {status}")

    def get_v4_hosts(self, hosts: list) -> list:
        """get list of v4 hosts from list

        Args:
            hosts (list): hosts (v4 and v6)

        Returns:
            list: only v4 hosts
        """
        return list(filter(lambda x: len(x['ip'].split('.')) == 4, hosts))
