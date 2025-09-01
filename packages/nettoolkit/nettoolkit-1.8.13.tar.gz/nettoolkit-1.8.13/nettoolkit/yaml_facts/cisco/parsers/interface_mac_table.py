"""cisco show mac address-table command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

def get_mac_address_table(command_output):
	"""parse output of : show mac address-table

	Args:
		command_output (list): command output

	Returns:
		dict: interfaces level parsed output dictionary
	"""    	
	op_dict = {}
	parsed_data = parse_to_list_using_ntc('show mac address-table', command_output)
	#
	for spl in parsed_data:
		intf_list = spl[-1]
		for intf in intf_list:
			try:
				p = STR.if_standardize(intf)
			except:
				continue
			int_filter = get_cisco_int_type(p)
			if not op_dict.get(int_filter):
				op_dict[int_filter] = {}
			int_filter_dict = op_dict[int_filter]
			if not int_filter_dict.get(p): 
				int_filter_dict[p] = {}
			nbr = int_filter_dict[p]
			# if not nbr.get("mac0"): nbr["mac0"] = 
			# nbr["mac0"][standardize_mac(spl[0])] = ''

			# if not nbr.get("mac2"): nbr["mac2"] = {}
			# nbr['mac2'][mac_2digit_separated(spl[0])] = ''

			if not nbr.get("mac"): nbr["mac"] = {}
			nbr['mac'][mac_4digit_separated(spl[0])] = ''

	return {'interfaces': op_dict }

# ------------------------------------------------------------------------------
