"""cisco show interface description command output parser """

# ------------------------------------------------------------------------------

from nettoolkit.facts_finder.generators.commons import *
from .common import *
# ------------------------------------------------------------------------------

def get_interface_description(cmd_op, *args):
	"""parser - show int descript command output

	Parsed Fields:
		* port/interface
		* description

	Args:
		cmd_op (list, str): command output in list/multiline string.

	Returns:
		dict: output dictionary with parsed fields
	"""
	
	cmd_op = verifid_output(cmd_op)
	int_desc_dict = {}
	start = False
	for l in cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("!"): continue
		if l.startswith("Interface"): 
			desc_begin_at = l.find("Description")
			status_begin_at = l.find("Status")
			protocol_begin_at = l.find("Protocol")
			continue
		spl = l.strip().split()
		p = STR.if_standardize(spl[0])
		if not int_desc_dict.get(p): 
			int_desc_dict[p] = {}
		port = int_desc_dict[p]
		port['description'] = get_string_trailing(l, desc_begin_at)
		#
		admin_status = l[status_begin_at:protocol_begin_at].strip()
		int_status = l[protocol_begin_at:desc_begin_at].strip()
		state = 'up'
		if admin_status in ('admin down', 'administratively down'):
			state = 'administratively down'
		elif int_status in ('down'):
			state = 'down'
		port['link_status'] = state
		#
		if not (int_desc_dict.get('filter') and int_desc_dict['filter']):
			port['filter'] = get_cisco_int_type(p)

	return {'op_dict': int_desc_dict }
# ------------------------------------------------------------------------------
