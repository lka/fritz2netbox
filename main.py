from dotenv import load_dotenv
from src.fritzbox import FritzBox

# Get the Environment Variables
load_dotenv()


fb = FritzBox()
hosts = fb.get_hosts()

for index, host in enumerate(hosts, start=1):
    status = 'active' if host['status'] else '-'
    ip = host['ip'] if host['ip'] else '-'
    mac = host['mac'] if host['mac'] else '-'
    hn = host['name']
    print(f'{index:>3}: {ip:<16} {hn:<42} {mac:<17}   {status}')
