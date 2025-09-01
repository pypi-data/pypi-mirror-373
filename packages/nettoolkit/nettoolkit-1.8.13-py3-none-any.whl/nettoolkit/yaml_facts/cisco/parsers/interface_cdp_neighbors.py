"""cisco show cdp neighbour command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------
def get_cdp_neighbour(command_output):
	"""parse output of : show cdp neighbor

	Args:
		command_output (list): command output

	Returns:
		dict: physical interfaces level parsed output dictionary
	"""    	
	nbr_d = {}
	parsed_data = parse_to_list_using_ntc('show cdp neighbors', command_output)
	#
	for spl in parsed_data:
		local_if = STR.if_standardize(spl[1])
		nbr_d[local_if] = {'neighbor': {}}
		nbr = nbr_d[local_if]['neighbor']
		nbr['hostname'] = spl[0]
		nbr['plateform'] = spl[3]
		try:
			nbr_int = STR.if_standardize(spl[4])
		except:
			nbr_int = spl[4]
		nbr['interface'] = nbr_int

	return {'interfaces': {'physical': nbr_d} }

# ------------------------------------------------------------------------------
