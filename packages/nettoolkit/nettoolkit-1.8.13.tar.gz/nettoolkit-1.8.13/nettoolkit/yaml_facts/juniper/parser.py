"""Description: Juniper Parser
"""

# ==============================================================================================
#  Imports
# ==============================================================================================
from dataclasses import dataclass, field
from collections import OrderedDict
from nettoolkit.yaml_facts.common import CommonParser
from nettoolkit.yaml_facts.juniper.parsers import *

# ==============================================================================================
#  Local Statics
# ==============================================================================================
JUNIPER_CMD_PARSER_MAP = OrderedDict([
	('show configuration', (
			get_interfaces_running, 
			get_system_running_routes, 
			get_system_running_prefix_lists,
			get_instance_running,
			get_bgp_running,
			get_ospf_running,
			get_ospf3_running,
			get_rip_running,
			get_isis_running,
			get_helper_running,
			get_system_running, 
		)
	),
	# ('show interfaces descriptions', (get_interface_description, )),  # skip: added in show config.
	('show lldp neighbors', (get_lldp_neighbour,)),
	('show chassis hardware', (
			get_chassis_hardware,
			get_chassis_serial,
		)
	),
	('show arp', (get_arp_table,)),
	('show version', (get_version, )),
	# 'show interfaces terse', (),     ## Not implemented yet
	# 'show bgp summary', (),          ## Not implemented yet

])


# ==============================================================================================
#  Local Functions
# ==============================================================================================



# ==============================================================================================
#  Classes
# ==============================================================================================
@dataclass
class JuniperParser(CommonParser):
	"""Juniper Parser Class - parse juniper configurations using JUNIPER_CMD_PARSER_MAP

	Inherits:
		CommonParser (class): Common Parser class
	"""    	
	captures: any
	output_folder: str=''

	cmd_fn_parser_map = JUNIPER_CMD_PARSER_MAP

# ==============================================================================================
#  Main
# ==============================================================================================
if __name__ == '__main__':
	pass

# ==============================================================================================
