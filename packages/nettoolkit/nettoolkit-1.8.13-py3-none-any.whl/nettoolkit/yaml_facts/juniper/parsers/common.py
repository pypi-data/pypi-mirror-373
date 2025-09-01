"""Description: 
"""

# ==============================================================================================
#  Imports
# ==============================================================================================
from dataclasses import dataclass, field
from collections import OrderedDict
from nettoolkit.nettoolkit_common import *
from nettoolkit.addressing import *
from nettoolkit.pyNetCrypt import *
from nettoolkit.pyJuniper import JSet

from nettoolkit.yaml_facts.common import *

# ==============================================================================================
#  Local Statics
# ==============================================================================================
merge_dict = DIC.merge_dict

JUNIPER_CMD_NTC_PARSER_FILE_MAP = {
	'show chassis hardware' : 'juniper_junos_show_chassis_hardware.textfsm',
	'show lldp neighbors'   : 'juniper_junos_show_lldp_neighbors.textfsm'  ,
	# 'show version'          : 'juniper_junos_show_version.textfsm',        # NIU, chassis info wrong
	'show arp'              : 'juniper_junos_show_arp.textfsm',

}


# ==============================================================================================
#  Local Functions
# ==============================================================================================

def remove_remarks(command_output):
	"""remove remarked lines from juniper output

	Args:
		command_output (list): list of output

	Returns:
		list: updated list of output
	"""    	
	return [line for line in command_output if not line.startswith("#")]

def get_int_port_dict(op_dict, port):
	"""get an interface number from provided port and update op_dict

	Args:
		op_dict (dict): output dict
		port (str): portid

	Returns:
		dict: updated op_dict
	"""    	
	int_filter = get_juniper_int_type(port).lower()
	if not op_dict.get(int_filter):
		op_dict[int_filter] = {}
	int_filter_dict = op_dict[int_filter]
	#
	return get_numbered_port_dict(int_filter_dict, port)

def get_numbered_port_dict(op_dict, port):
	"""update port number for irb, ae, lo interfaces.

	Args:
		op_dict (dict): output dict
		port (str): portid

	Returns:
		dict: updated op_dict
	"""    	
	if port.startswith("irb."): 
		port=int(port[4:])
	elif port.startswith("ae") or port.startswith("lo"): 
		port=port[2:]
	return add_blankdict_key(op_dict, port)

def parse_to_list_using_ntc(cmd, command_output):
	"""parse command output of a command using ntc template

	Args:
		cmd (str): absolute command
		command_output (list): list of command output

	Returns:
		dict: list of parsed output
	"""    	
	return parse_to_list_cmd(cmd, remove_remarks(command_output), JUNIPER_CMD_NTC_PARSER_FILE_MAP)

def parse_to_dict_using_ntc(cmd, command_output):
	"""parse command output of a command using ntc template

	Args:
		cmd (str): absolute command
		command_output (list): list of command output

	Returns:
		dict: dictionary of parsed output
	"""    	
	return parse_to_dict_cmd(cmd, remove_remarks(command_output), JUNIPER_CMD_NTC_PARSER_FILE_MAP)


# ==============================================================================================

def get_pw(spl, key):
	"""get the juniper decrypted password

	Args:
		spl (list): list of splitted output line
		key (str): input password

	Returns:
		str: decrypted password if possible, or same as input
	"""    	
	pw = spl[spl.index(key)+1]
	if pw[0] == '"': pw = pw[1:]
	if pw[-1] == '"': pw = pw[:-1]
	return juniper_decrypt( pw )



# ==============================================================================================
#  Classes
# ==============================================================================================



# ==============================================================================================
#  Main
# ==============================================================================================
if __name__ == '__main__':
	pass

# ==============================================================================================
