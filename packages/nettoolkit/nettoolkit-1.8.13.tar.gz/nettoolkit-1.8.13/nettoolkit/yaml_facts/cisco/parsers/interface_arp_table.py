"""cisco show arp table command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------


def get_arp_table(command_output):
	"""parse output of : show ip arp

	Args:
		command_output (list): command output

	Returns:
		dict: interfaces level parsed output dictionary
	"""    	
	op_dict = {}
	parsed_data = parse_to_list_using_ntc('show ip arp', command_output)
	#
	for spl in parsed_data:
		try:
			p = STR.if_standardize(spl[-1])
		except:
			continue
		_mac = mac_4digit_separated(spl[3])
		ip = spl[1]
		int_filter = get_cisco_int_type(p)
		if int_filter != 'physical': continue
		if not op_dict.get(int_filter): op_dict[int_filter] = {}
		int_filter_dict = op_dict[int_filter]
		if not int_filter_dict.get(p):  int_filter_dict[p] = {}
		port = int_filter_dict[p]
		if not port.get('mac'): port['mac'] = {}
		port['mac'][_mac] = ip

	return {'interfaces': op_dict }


# ------------------------------------------------------------------------------
