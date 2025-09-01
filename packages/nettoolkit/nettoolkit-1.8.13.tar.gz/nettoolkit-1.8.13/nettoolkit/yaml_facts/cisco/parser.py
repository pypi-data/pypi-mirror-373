"""Description: Cisco Parser
"""

# ==============================================================================================
#  Imports
# ==============================================================================================
from dataclasses import dataclass, field
from collections import OrderedDict
from nettoolkit.yaml_facts.common import CommonParser
from nettoolkit.yaml_facts.cisco.parsers import *

# ==============================================================================================
#  Local Statics
# ==============================================================================================
CISCO_CMD_PARSER_MAP = OrderedDict([
	('show running-config', (
			get_interfaces_running, 
			get_system_running_routes,
			get_system_running_prefix_lists,
			get_bgp_running, 
			get_rip_running,
			get_eigrp_running,
			get_ospf_running,
			get_isis_running,
			get_vrfs_running,
			get_system_running, 
	)),
	('show interfaces status', (get_interface_status, )),
	('show cdp neighbors', (get_cdp_neighbour, )),
	('show lldp neighbors', (get_lldp_neighbour, )),
	# ('show interfaces description', (get_interface_description, )),    ## part of runing so removed
	# ('show mac address-table', (get_mac_address_table, )),             ## skip for now.. slower
	# ('show ip arp', (get_arp_table, )),                                ## skip for now.. slower
	('show version', (get_version, )),
])


# ==============================================================================================
#  Local Functions
# ==============================================================================================



# ==============================================================================================
#  Classes
# ==============================================================================================
@dataclass
class CiscoParser(CommonParser):
	"""Cisco Parser Class - parse juniper configurations using CISCO_CMD_PARSER_MAP

	Inherits:
		CommonParser (class): Common Parser class
	"""    	
	captures: any
	output_folder: str=''

	cmd_fn_parser_map = CISCO_CMD_PARSER_MAP

# ==============================================================================================
#  Main
# ==============================================================================================
if __name__ == '__main__':
	pass

# ==============================================================================================
