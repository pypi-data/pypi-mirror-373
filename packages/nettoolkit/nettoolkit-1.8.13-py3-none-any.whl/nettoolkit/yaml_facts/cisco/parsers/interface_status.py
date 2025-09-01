# OUTPUT SHOULD BE UNFILTERED ( HEADER ROW REQUIRED IN OUTPUT )
"""cisco show interface status command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

def get_interface_status(command_output):
	"""parse output of : show interface status

	Args:
		command_output (list): command output

	Returns:
		dict: interfaces level parsed output dictionary
	"""    	
	int_status_dict = {}
	parsed_data = parse_to_list_using_ntc('show interfaces status', command_output)
	#
	for spl in parsed_data:
		p = STR.if_standardize(spl[0])
		int_filter = get_cisco_int_type(p)
		if not int_status_dict.get(int_filter):
			int_status_dict[int_filter] = {}
		int_filter_dict = int_status_dict[int_filter]
		if p.lower().startswith("port-channel"): p = int(p[12:])
		if not int_filter_dict.get(p): 
			int_filter_dict[p] = {}
		port = int_filter_dict[p]
		#
		port['media_type'] = spl[6]
		port['duplex'] = spl[4]
		port['speed'] = spl[5]
		port['link_status'] = spl[2]

	return {'interfaces': int_status_dict }

# ------------------------------------------------------------------------------
