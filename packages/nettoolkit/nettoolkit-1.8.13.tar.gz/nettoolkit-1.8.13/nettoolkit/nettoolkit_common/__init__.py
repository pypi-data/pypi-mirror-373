__doc__ = '''Networking Tool Set Common Functions
'''


__all__ = [
	# .gpl
	'Default', 'Container', 'DifferenceDict', 
	'STR', 'IO', 'LST', 'DIC', 'LOG', 'DB', 'XL_READ', 'XL_WRITE', 
	'DictMethods', 'Multi_Execution', 'standardize_if', 'get_username', 'get_password', 
	'get_juniper_int_type', 'get_cisco_int_type', 'get_device_manu',

	# common
	"remove_domain", "read_file", "get_op", "get_ops", "blank_line", "get_device_manufacturar", "detect_device_type", "verifid_output", 
	"get_string_part", "get_string_trailing", "standardize_mac", "mac_2digit_separated", "mac_4digit_separated", 
	"flatten", "dataframe_generate", "printmsg", "read_yaml_mode_us", "open_text_file", "open_excel_file",
	"open_folder", 
	"CapturesOut",
	"get_file_name", "get_file_path", "create_folders", "deprycation_warning",

	# facts
	"add_blankdict_key", "add_blankset_key", "add_blanklist_key", "add_blanktuple_key", "add_blanknone_key", "update_key_value",
	"next_index_item", "append_attribute", "get_instance_parameter_for_items", "update_true_instance_items", "get_nest_attributes",
	"get_appeneded_value", "add_to_list",

	# networking
	"nslookup", "IP", "get_int_ip", "get_int_mask",
	'get_vlans_juniper', 'get_juniper_pw_string', 
	'expand_if', 'expand_if_dict', 'get_interface_cisco', 'get_vlans_cisco', 'trunk_vlans_cisco',
	'get_vrf_cisco',

	# formatting
	'print_banner', 'print_table',
]




from .gpl import (
	Default, Container, 
	DifferenceDict, DictMethods, DIC,
	STR, IO, LST, LOG, DB, XL_READ, XL_WRITE, 
	Multi_Execution, 
	standardize_if,
	get_username, get_password, 
	get_juniper_int_type, get_cisco_int_type, get_device_manu
	)
from .common import (
	CapturesOut,
	remove_domain, read_file, get_op, get_ops, blank_line, get_device_manufacturar, detect_device_type, verifid_output, 
	get_string_part, get_string_trailing, standardize_mac, mac_2digit_separated, mac_4digit_separated,
	flatten, dataframe_generate, printmsg, read_yaml_mode_us, open_text_file, open_excel_file,
	open_folder,
	get_file_name, get_file_path, create_folders, deprycation_warning
)
from .facts import (
	add_blankdict_key, add_blankset_key, add_blanklist_key, add_blanktuple_key, add_blanknone_key, update_key_value,
	next_index_item, append_attribute, get_instance_parameter_for_items, update_true_instance_items, get_nest_attributes,
	get_appeneded_value, add_to_list,
)
from .networking import (
	IP, 
	nslookup, get_int_ip, get_int_mask,
	get_vlans_juniper, get_juniper_pw_string, 
	expand_if, expand_if_dict, get_interface_cisco, get_vlans_cisco, trunk_vlans_cisco,
	# get_inet_address, get_secondary_inet_address, inet_address, get_inetv6_address,
	get_vrf_cisco
)
from .formatting import print_banner, print_table
