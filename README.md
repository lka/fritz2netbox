# fritz2netbox
Get Data from Fritz!Box and put them into Netbox.

## Goal of this implementation

I want to get all IP-addresses (including dns names) from Fritz!Box in my Netbox application.
There should be included all active IP-addresses plus all inactive addresses that are only temporarily active (put them into the ACCEPT list in ".env").
IP-addresses that should be ignored and not included in Netbox are in the IGNORE list in ".env".

✍️ Then assign these IP addresses to the interfaces of the devices in Netbox. ✍️

After this (in the next run) the program assigns corresponding MAC-addresses to the interfaces.
It tries to set the MAC-address as primary_mac_address but there is a bug in Netbox (I have created an issue for the netbox team) it will work after the correction of this.

For speed it up, I put the Fritz!Box data (the TR69 read is very slow) in 'hosts.json'. If you want to get changes from Fritz!Box delete the file 'hosts.json'.

Errors are logged in 'fritz2netbox.log'.