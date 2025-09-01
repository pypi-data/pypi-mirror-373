"""juniper interface description command output parser """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *
# ------------------------------------------------------------------------------


def get_int_description(cmd_op, *args):
	"""parser - show interfaces description command output

	Parsed Fields:
		* port/interface 
		* description

	Args:
		cmd_op (list, str): command output in list/multiline string.

	Returns:
		dict: output dictionary with parsed fields
	"""
	cmd_op = verifid_output(cmd_op)
	op_dict = OrderedDict()

	for l in cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("#"): continue
		if l.startswith("Interface"): 
			desc_begin_at = l.find("Description")
			link_desc_begin_at = l.find("Admin")
			continue
		spl = l.strip().split()
		p = spl[0]
		if not op_dict.get(p): op_dict[p] = {}
		port = op_dict[p]
		if not (port.get('description') and port['description']):
			port['description'] = get_string_trailing(l, desc_begin_at)
		port['link_status'] = l[link_desc_begin_at:link_desc_begin_at+5].strip()
		if not (op_dict.get('filter') and op_dict['filter']):
			int_type = get_juniper_int_type(p)
			port['filter'] = int_type.lower()

	return {'op_dict': op_dict}
# ------------------------------------------------------------------------------
