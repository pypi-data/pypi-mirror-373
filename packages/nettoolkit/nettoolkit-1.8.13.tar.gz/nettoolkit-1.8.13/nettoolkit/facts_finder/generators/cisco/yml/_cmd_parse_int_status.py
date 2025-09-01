# OUTPUT SHOULD BE UNFILTERED ( HEADER ROW REQUIRED IN OUTPUT )
"""cisco show interface status command output parser """

# ------------------------------------------------------------------------------

from nettoolkit.facts_finder.generators.commons import *
# from .common import *
# ------------------------------------------------------------------------------

def get_interface_status_yml(cmd_op, *args):
	"""parser - show int status command output

	Parsed Fields:
		* port/interface
		* port_type
		* duplex
		* speed
		* port_status

	Args:
		cmd_op (list, str): command output in list/multiline string.

	Returns:
		dict: output dictionary with parsed fields
	"""	
	# cmd_op = command output in list/multiline string.
	cmd_op = verifid_output(cmd_op)
	int_status_dict = {}
	start = False
	for l in cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("!"): continue
		if l.strip().startswith("^"): 
			print('missing or invalid input  show interface status, skipped')			
			return int_status_dict
		# // HEADER ROW // #
		if l.startswith("Port"):
			type_begin_at = l.find("Type")
			duplex_begin = l.find("Duplex")
			duplex_end = duplex_begin + 6
			speed_begin = duplex_end
			speed_end = speed_begin + 7
			access_vlan_begin = l.find("Vlan")
			status_begin = l.find("Status")
			status_end = access_vlan_begin - 1
			continue
		# // DATA TABLE ROWS //
		spl = l.strip().split()
		p = STR.if_standardize(spl[0])
		int_status_dict[p] = {}
		port = int_status_dict[p]
		port['media_type'] = get_string_trailing(l, type_begin_at)
		port['duplex'] = get_string_part(l, duplex_begin, duplex_end)
		port['speed'] = get_string_part(l, speed_begin, speed_end)
		port['link_status'] = get_string_part(l, status_begin, status_end)
		if not (int_status_dict.get('filter') and int_status_dict['filter']):
			port['filter'] = get_cisco_int_type(p)
	
	return {'op_dict': int_status_dict }
# ------------------------------------------------------------------------------
