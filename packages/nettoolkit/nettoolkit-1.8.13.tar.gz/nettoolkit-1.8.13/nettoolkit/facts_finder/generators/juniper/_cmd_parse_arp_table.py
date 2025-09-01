"""juniper arp table command output parser """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *
# ------------------------------------------------------------------------------

def get_arp_table(cmd_op, *args):
	"""parser - show arp command output

	Parsed Fields:
		* port/interface 
		* ip
		* mac, mac2, mac4
		* dns
		* vlan

	Args:
		cmd_op (list, str): command output in list/multiline string.

	Returns:
		dict: output dictionary with parsed fields
	"""
	cmd_op = verifid_output(cmd_op)
	op_dict = OrderedDict()

	nbr_d, remote_hn = {}, ""
	nbr_table_start = False
	for l in cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("#"): continue
		spl = l.strip().split()
		_mac = standardize_mac(spl[0])
		ip = spl[1]
		dns = spl[2].split(".")[0]
		if dns.isdigit(): dns = spl[2]
		try:
			vlan = spl[3]	
			p = spl[4].replace("[","").replace("]","").split(".")[0]
			_add_arp(op_dict, p, _mac, ip, dns, vlan)
			_add_arp(op_dict, vlan, _mac, ip, dns, vlan)
		except: pass
		## add/modify for ae interface as well to add arp if need.

	return {'op_dict': op_dict}
# ------------------------------------------------------------------------------
def _add_arp(op_dict, p, _mac, ip, dns, vlan):
	"""add the detais to output dictionary

	Args:
		op_dict (dict): dicationary with/without info
		p (str): port
		_mac (str): mac address
		ip (str): ip address
		dns (str): dns name
		vlan (str): vlan number
	"""    	
	if not op_dict.get(p): op_dict[p] = {'neighbor': {}}
	nbr = op_dict[p]['neighbor']
	if not nbr.get("mac"): nbr["mac"] = set()
	if not nbr.get("mac2"): nbr["mac2"] = set()
	if not nbr.get("mac4"): nbr["mac4"] = set()
	if not nbr.get("ip"): nbr["ip"] = set()
	if not nbr.get("dns"): nbr["dns"] = set()
	if not nbr.get("vlan"): nbr["vlan"] = set()
	nbr["mac"].add(standardize_mac(_mac))
	nbr['mac2'].add(mac_2digit_separated(_mac))
	nbr['mac4'].add(mac_4digit_separated(_mac))
	nbr["ip"].add(ip)
	nbr["dns"].add(dns)
	nbr['vlan'].add(vlan.replace("irb.",""))
# ------------------------------------------------------------------------------


