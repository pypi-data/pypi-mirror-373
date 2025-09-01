"""cisco show version command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

def get_version(command_output):
	"""parse output of : show version

	Args:
		command_output (list): command output

	Returns:
		dict: system level parsed output dictionary
	"""    	
	op_dict = {}
	parsed_data = parse_to_dict_using_ntc('show version', command_output)[0]
	#
	if isinstance(parsed_data['SERIAL'], list ):
		for i, (model, serial, mac) in enumerate(zip(
													parsed_data['HARDWARE'],
													parsed_data['SERIAL'],
													parsed_data['MAC'],
			)):
			sw =  f'Switch-{i+1}'
			op_dict[sw] = {}
			sw_dict = op_dict[sw]
			sw_dict['make'] = 'cisco'
			sw_dict['model'] = model
			sw_dict['serial'] = serial
			sw_dict['mac'] = mac

	op_dict['ios_version'] = parsed_data['VERSION']
	op_dict['boot_image']  = parsed_data['RUNNING_IMAGE']
	op_dict['hostname']    = parsed_data['HOSTNAME']
	op_dict['host-name']   = parsed_data['HOSTNAME']
	op_dict['uptime']      = parsed_data['UPTIME']
	op_dict['conf-reg']    = parsed_data['CONFIG_REGISTER']

	return {'system': op_dict }

# ------------------------------------------------------------------------------
