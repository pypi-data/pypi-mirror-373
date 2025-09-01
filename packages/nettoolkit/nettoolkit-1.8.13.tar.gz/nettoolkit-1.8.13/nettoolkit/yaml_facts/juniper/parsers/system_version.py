"""juniper show version command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

def get_version(cmd_op):
	"""parse output of : show version

	Args:
		command_output (list): command output

	Returns:
		dict: system level parsed output dictionary
	"""    	
	op_dict = {}
	version, model = "", ""
	fpc_dict = None
	for l in cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("#"): continue
		if l.strip().startswith("---"): continue
		if l.startswith('fpc'):
			fpc = l.split(":")[0]
			if not op_dict.get(fpc):
				op_dict[fpc] = {}
			fpc_dict = op_dict[fpc]
			continue
		if fpc_dict is None: fpc_dict = op_dict
		if not fpc_dict.get('make'): fpc_dict['make'] = 'juniper'
		if l.startswith("Model: "):  fpc_dict['model'] = l.strip().split()[-1]
		if l.startswith("JUNOS Base OS Software Suite"):  
			fpc_dict['junos_version'] = l.strip().split()[-1].replace("[", '').replace("]", '')
	return {'system': op_dict}
# ------------------------------------------------------------------------------
##
#
#  NTC Template not givinng optimal result for chassis switches
#  hence creating it manually
#
##
# ------------------------------------------------------------------------------
