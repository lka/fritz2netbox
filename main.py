from dotenv import load_dotenv
from src.fritzbox import FritzBox
import json
from pathlib import Path

HOSTS = 'hosts.json'
# Get the Environment Variables
load_dotenv()

if Path(HOSTS).exists():
    with open(HOSTS, 'r', encoding='utf-8') as f:
        hosts = json.load(f)
else:
    fb = FritzBox()
    hosts = fb.get_hosts()
    with open(HOSTS, 'w', encoding='utf-8') as f:
        json.dump(hosts, f, ensure_ascii=False, indent=4)

for index, host in enumerate(hosts, start=1):
    status = 'active' if host['status'] else '-'
    ip = host['ip'] if host['ip'] else '-'
    mac = host['mac'] if host['mac'] else '-'
    hn = host['name']
    print(f'{index:>3}: {ip:<16} {hn:<42} {mac:<17}   {status}')
