"""Description: 
"""

# ==============================================================================================
#  Imports
# ==============================================================================================
from collections import OrderedDict
from dataclasses import dataclass, field
from nettoolkit.nettoolkit_common import *
from nettoolkit.addressing import *
from nettoolkit.pyNetCrypt import *

from nettoolkit.yaml_facts.common import *

# ==============================================================================================
#  Local Statics
# ==============================================================================================
merge_dict = DIC.merge_dict

CISCO_CMD_NTC_PARSER_FILE_MAP = {
	'show interfaces status':     'cisco_ios_show_interfaces_status.textfsm',
	'show cdp neighbors':         'cisco_ios_show_cdp_neighbors.textfsm',
	'show lldp neighbors':        'cisco_ios_show_lldp_neighbors.textfsm',
	'show mac address-table':     'cisco_ios_show_mac-address-table.textfsm',
	'show ip arp':                'cisco_ios_show_ip_arp.textfsm',
	'show version':               'cisco_ios_show_version.textfsm',
	'show interfaces description':'cisco_ios_show_interfaces_description.textfsm', 
}


# ==============================================================================================
#  Local Functions
# ==============================================================================================

def remove_remarks(command_output):
	"""remove remarked lines from cisco output

	Args:
		command_output (list): list of output

	Returns:
		list: updated list of output
	"""    	
	return [line for line in command_output if not line.startswith("!")]

def update_port_on_int_type(p):
	"""update the port to port number based on input port.
	Examples -
	vlan200 will change to 200.
	loopback0 will change to 0. 
	port-channel10 will change to 10.
	tunnel0 will change to 0.
	other types will remain unchanged.

	Args:
		p (str): port string

	Returns:
		int,str: updated ports
	"""    	
	if p.lower().startswith("vlan"):           p = int(p[4:])
	elif p.lower().startswith("loopback"):     p = int(p[8:])
	elif p.lower().startswith("port-channel"): p = int(p[12:])
	elif p.lower().startswith("tunnel"):       p = int(p[6:])
	return p

def parse_to_list_using_ntc(cmd, command_output):
	"""parse command output of a command using ntc template

	Args:
		cmd (str): absolute command
		command_output (list): list of command output

	Returns:
		list: list of parsed output
	"""    	
	return parse_to_list_cmd(cmd, remove_remarks(command_output), CISCO_CMD_NTC_PARSER_FILE_MAP)

def parse_to_dict_using_ntc(cmd, command_output):
	"""parse command output of a command using ntc template

	Args:
		cmd (str): absolute command
		command_output (list): list of command output

	Returns:
		dict: dictionary of parsed output
	"""    	
	return parse_to_dict_cmd(cmd, remove_remarks(command_output), CISCO_CMD_NTC_PARSER_FILE_MAP)

def cisco_addressing_on_list(spl, ip_index, mask_index):
	"""get the IP address object for cisco input format of ( ip address 10.10.0.3 255.255.255.0 )

	Args:
		spl (list): splitted input line
		ip_index (int): ip address index value
		mask_index (int): mask index value

	Returns:
		IPv4, IPv6: ip addressing object
	"""    	
	mask = None if "/" in spl[ip_index] else spl[mask_index]
	return addressing(spl[ip_index], mask)



# ==============================================================================================
#  Classes
# ==============================================================================================



# ==============================================================================================
#  Main
# ==============================================================================================
if __name__ == '__main__':
	pass

# ==============================================================================================
