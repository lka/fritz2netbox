import os
from dotenv import load_dotenv
from fritzconnection.lib.fritzhosts import FritzHosts

# Get the Environment Variables
load_dotenv()
fritzBoxIP = 'FB_IP'
fritzBoxUser = 'USER'
fritzBoxPWD = 'PASSWORD'

fh = FritzHosts(address=os.getenv(fritzBoxIP),
                user=os.getenv(fritzBoxUser),
                password=os.getenv(fritzBoxPWD))

hosts = fh.get_hosts_info()
for index, host in enumerate(hosts, start=1):
    status = 'active' if host['status'] else '-'
    ip = host['ip'] if host['ip'] else '-'
    mac = host['mac'] if host['mac'] else '-'
    hn = host['name']
    print(f'{index:>3}: {ip:<16} {hn:<42} {mac:<17}   {status}')
