"""cisco show interface description command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

def get_interface_description(command_output):
	"""parse output of : show interface description

	Args:
		command_output (list): command output

	Returns:
		dict: interfaces level parsed output dictionary
	"""    	
	int_desc_dict = {}
	parsed_data = parse_to_list_using_ntc('show interfaces description', command_output)
	#
	for spl in parsed_data:
		p = STR.if_standardize(spl[0])
		int_filter = get_cisco_int_type(p)
		p = update_port_on_int_type(p)
		#
		if not int_desc_dict.get(int_filter): int_desc_dict[int_filter] = {}
		int_filter_dict = int_desc_dict[int_filter]
		if not int_filter_dict.get(p):  int_filter_dict[p] = {}
		port = int_filter_dict[p]
		#
		port['description'] = spl[-1]
		port['admin_status'] = spl[1]
		port['link_status'] =  spl[2]

	return {'interfaces': int_desc_dict }


# ------------------------------------------------------------------------------
