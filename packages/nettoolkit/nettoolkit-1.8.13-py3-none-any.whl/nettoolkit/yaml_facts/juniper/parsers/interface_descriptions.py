"""juniper interface description command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------


def get_interface_description(cmd_op):
	"""parse output of : show interfaces description

	Args:
		command_output (list): command output

	Returns:
		dict: interfaces level parsed output dictionary
	"""    	
	op_dict = {}
	for l in cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("#"): continue
		if l.startswith("Interface"): 
			desc_begin_at = l.find("Description")
			link_desc_begin_at = l.find("Admin")
			continue
		spl = l.strip().split()
		p = spl[0]
		if p.endswith(".0"): p = p[:-2]
		port = get_int_port_dict(op_dict=op_dict, port=p)
		if not (port.get('description') and port['description']):
			port['description'] = get_string_trailing(l, desc_begin_at)
		port['link_status'] = l[link_desc_begin_at:link_desc_begin_at+5].strip()

	return {'interfaces': op_dict}
# ------------------------------------------------------------------------------
