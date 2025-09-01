"""juniper lldp neighbour command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

def get_lldp_neighbour(cmd_op):
	"""parse output of : show lldp neighbor

	Args:
		command_output (list): command output

	Returns:
		dict: interfaces level parsed output dictionary
	"""    	
	nbr_d = {}
	parsed_data = parse_to_dict_using_ntc('show lldp neighbors', cmd_op)

	for dic in parsed_data:
		port_dict = get_int_port_dict(op_dict=nbr_d, port=dic['LOCAL_INTERFACE'])
		remote_device = get_device_manu(dic['PORT_INFO'])
		port_dict['neighbor'] = {}
		nbr = port_dict['neighbor']
		nbr['hostname'] = remove_domain(dic['SYSTEM_NAME'])
		nbr['fqdn_host'] = dic['SYSTEM_NAME']
		try:
			port_info = standardize_if(dic['PORT_INFO'])
		except:
			port_info = dic['PORT_INFO']
		nbr['port'] = port_info
		nbr['suspected'] = remote_device

	return {'interfaces': nbr_d}

# ------------------------------------------------------------------------------
