import os
from dotenv import load_dotenv
from src.fritzbox import FritzBox
from src.netbox import NetBox
import json
from pathlib import Path
import logging

HOSTS = "hosts.json"
IGNORE = "IGNORE"
ACCEPT = "ACCEPT"
LOGFILE = "LOGFILE"

# enable logging
logger = logging.getLogger(__name__)
# Get the Environment Variables
load_dotenv()


def main():
    logging.basicConfig(filename=os.getenv(LOGFILE), level=logging.INFO)
#    logger.info("Started")

    ignore_list = os.getenv(IGNORE) if os.getenv(IGNORE) else []
    accept_list = os.getenv(ACCEPT) if os.getenv(ACCEPT) else []

    hosts = []
    if Path(HOSTS).exists():
        with open(HOSTS, "r", encoding="utf-8") as f:
            hosts = json.load(f)
    else:
        fb = FritzBox()
        hosts = fb.get_hosts()
        with open(HOSTS, "w", encoding="utf-8") as f:
            json.dump(hosts, f, ensure_ascii=False, indent=4)

    # get only active hosts, which are not in ignore_list
    hosts = FritzBox.get_active_hosts(None, hosts, ignore_list, accept_list)
    hosts_v4 = FritzBox.get_v4_hosts(None, hosts)

    FritzBox.print_hosts(None, hosts_v4)
    if FritzBox.hostnames_has_duplicates(None, hosts_v4):
        print("Attention: in the Fritz!Box are duplicate hostnames.\nPlease change them.")
        exit(-1)

    # get actually known IP-Adresses in Netbox
    nb = NetBox()
    try:
        resp = nb.get_ip_adresses()
    except IOError as e:
        logger.error(e)
        print(f"Error: {e}")
        exit(-1)
    if resp.status_code != 200:  # not OK
        logger.info("Finished due to wrong return value")
        print("Finished due to wrong return value accessing netbox")
        exit(-1)  # exit with failure

    nb_hosts = json.loads(resp.text)["results"]
    # print(json.dumps(nb_hosts, indent=4))

    # use only IP-V4 Adresses
    nb_v4_hosts = nb.get_v4_hosts(nb_hosts)
    # print(json.dumps(nb_v4_hosts, indent=4))

    print("\n------------------------------\n")
    for host in hosts_v4:
        found_in_nb = nb.search_hosts_with_dns_name(nb_v4_hosts, host["name"])
        if len(found_in_nb) == 0:  # hostname doesn't exist in netbox
            # print(found_in_nb)
            # print(f"insert {host['ip']} {host['name']} in Netbox")
            resp = nb.create_ip_address(host["ip"], host["name"])
            if resp.status_code != 201:  # ip already exists
                # get host with IP Address
                found_in_nb = nb.search_hosts_with_ip_address(nb_v4_hosts, host["ip"])
                if len(found_in_nb) > 0:
                    # change dns_name
                    resp = nb.modify_ip_address(
                        found_in_nb[0]["id"], found_in_nb[0]["address"], host["name"]
                    )
                    if resp.status_code != 200:
                        print(
                            f"failed to set {host['ip']} " f"{host['name']} in Netbox"
                        )
                        print(resp.text)
                else:
                    print(f"failed to insert {host['ip']} " f"{host['name']} in Netbox")
                    continue
                    # print(resp.text)
            else:
                print(f"IP-Address {host['ip']}, {host['name']} created; assign it to interface please")
                continue
        else:
            # print(f"{host['ip']} {host['name']} found in Netbox")
            if len(found_in_nb) == 1:
                if host["ip"] + "/24" != found_in_nb[0]["address"]:
                    # print("IP Address has changed")
                    resp = nb.modify_ip_address(
                        found_in_nb[0]["id"], host["ip"], host["name"]
                    )
                    if resp.status_code != 200:
                        print(
                            f"failed to set {host['ip']} " f"{host['name']} in Netbox"
                        )
                        print(resp.text)
        if nb.has_interface(found_in_nb[0]):
            id = found_in_nb[0]["assigned_object"]["id"]
            resp = nb.get_interface(id)
            # print(resp)
            if resp.status_code == 200:
                # print(resp.headers)
                interface = json.loads(resp.text)
                # print(json.dumps(interface, indent=4))
                resp = nb.create_mac_address_if_it_doesnt_exist(
                    host["mac"], interface["id"]
                )
                if interface["mac_address"] != host["mac"]:
                    print(
                        "\n-----------------------\n"
                        f"Interface: MAC {interface['mac_address']} != "
                        f"Host MAC {host['mac']}"
                    )
                    # print("\nInterface: " f"{json.dumps(interface, indent=4)}")
                    macID = nb.search_macList_with_address(host["mac"])[0]["id"]
                    resp = nb.modify_interface(interface["id"], macID)
                    if resp.status_code != 200:
                        print(
                            f"could not set MAC {host['mac']} "
                            f"in interface {interface['id']}"
                        )
                    else:
                        # print(resp.text)
                        print(
                            f"changed MAC to {host['mac']} "
                            f"in interface {interface['id']}"
                        )
#    logger.info("Finished")


if __name__ == "__main__":
    main()
