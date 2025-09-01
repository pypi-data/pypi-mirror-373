"""cisco show lldp neighbour command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------
def get_lldp_neighbour(command_output):
	"""parse output of : show lldp neighbor

	Args:
		command_output (list): command output

	Returns:
		dict: physical interfaces level parsed output dictionary
	"""    	
	nbr_d = {}
	parsed_data = parse_to_list_using_ntc('show lldp neighbors', command_output)
	#
	for spl in parsed_data:
		local_if = STR.if_standardize(spl[1])
		nbr_d[local_if] = {'neighbor': {}}
		nbr = nbr_d[local_if]['neighbor']
		nbr['hostname'] = spl[0]
		try:
			nbrintf = STR.if_standardize(spl[3])
		except:
			nbrintf = spl[3]
		nbr['interface'] = nbrintf

	return {'interfaces': {'physical': nbr_d} }

# ------------------------------------------------------------------------------
