import os
from fritzconnection.lib.fritzhosts import FritzHosts
fritzBoxIP = 'FB_IP'
fritzBoxUser = 'USER'
fritzBoxPWD = 'PASSWORD'


class FritzBox():

    def __init__(self):
        self.fh = FritzHosts(address=os.getenv(fritzBoxIP),
                             user=os.getenv(fritzBoxUser),
                             password=os.getenv(fritzBoxPWD))

    def get_hosts(self):
        return self.fh.get_hosts_info()
