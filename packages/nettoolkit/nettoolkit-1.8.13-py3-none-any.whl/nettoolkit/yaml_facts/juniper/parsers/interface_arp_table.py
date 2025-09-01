"""juniper arp table command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------
def get_arp_table(cmd_op, *args):
	"""parse output of : show arp

	Args:
		command_output (list): command output

	Returns:
		dict: interfaces level parsed output dictionary
	"""    	
	nbr_d = {}
	parsed_data = parse_to_dict_using_ntc('show arp', cmd_op)

	for dic in parsed_data:
		port_dict = get_int_port_dict(op_dict=nbr_d, port=dic['INTERFACE'])
		nbr_dict = add_blankdict_key(port_dict, 'neighbor')
		nbr_mac_bind = add_blankdict_key(nbr_dict, 'ip-mac-binding')
		append_attribute(nbr_mac_bind, 'ip', dic['IP_ADDRESS'])
		append_attribute(nbr_mac_bind, 'mac', mac_2digit_separated(dic['MAC']))

	return {'interfaces': nbr_d}
# ------------------------------------------------------------------------------


