"""cisco show arp table command output parser """

# ------------------------------------------------------------------------------

from nettoolkit.facts_finder.generators.commons import *
from .common import *
# ------------------------------------------------------------------------------

def get_arp_table(cmd_op, *args):
	"""parser - show ip arp command output

	Parsed Fields:
		* port/interface 
		* ip address
		* mac address

	Args:
		cmd_op (list, str): command output in list/multiline string.

	Returns:
		dict: output dictionary with parsed fields
	"""    	
	cmd_op = verifid_output(cmd_op)
	op_dict = {}
	start = False
	for l in cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("!"): continue
		if l.startswith("Protocol"): continue
		if l.find("Incomplete")>0: continue
		if l.strip().startswith("%") and l.endswith("does not exist."): continue
		spl = l.strip().split()
		try:
			p = STR.if_standardize(spl[-1])
			_mac = standardize_mac(spl[3])
			ip = spl[1]
		except:
			pass
		if not op_dict.get(p): op_dict[p] = {}
		port = op_dict[p]
		if not port.get(_mac): port[_mac] = set()
		port[_mac].add(ip)
	return {'op_dict': op_dict }

# ------------------------------------------------------------------------------
# NOT WORKING AS EXPECTED
# ------------------------------------------------------------------------------
