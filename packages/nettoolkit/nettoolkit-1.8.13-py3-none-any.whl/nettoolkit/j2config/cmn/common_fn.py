

import ipaddress as ip
from nettoolkit.nettoolkit_common import LST
from nettoolkit.addressing import addressing as ip_addressing
from nettoolkit.addressing import IPv4
from nettoolkit.addressing import get_summaries as nt_get_summaries
from nettoolkit.addressing import recapsulate


def str_to_list(item):
	"""splits string and returns list, items separated by either `comma`, `enter` 

	Args:
		item (str, int, float): input string or number value(s)

	Returns:
		list: separated list of input items
	"""	
	if isinstance(item, (str, int, float) ):
		items= []
		csv = item.strip().split(",")
		for _ in csv:
			lsv = _.strip().split("\n")
			for i in lsv:
				items.append(i)
		return items
	else:
		return item

def space_separated(items):
	"""joins provided items (iterables) by `spaces`

	Args:
		items (list): input items

	Returns:
		str: joins items by space
	"""	
	return " ".join(items)

def comma_separated(items):
	"""joins provided items (iterables) by `comma`

	Args:
		items (list): input items

	Returns:
		str: joins items by comma
	"""
	return ",".join(items)

def list_append(lst, item):
	"""append an item to list

	Args:
		lst (list): input list
		item (str, number): item to be appeneded to list

	Returns:
		list: updated list
	"""	
	return lst.append(item)

def list_extend(lst, item):
	"""Extend the list of items to list

	Args:
		lst (list): input list
		item (list): list of items to be extended to input list

	Returns:
		list: updated list
	"""
	return lst.extend(item)

def list_sorted(lst):
	"""provided sorted elements in list

	Args:
		lst (list): input list

	Returns:
		list: updated list
	"""	
	return sorted(lst)

def convert_to_int(lst):
	"""convert numeric string type elements to integer type in a list.

	Args:
		lst (list): converts numeric eliments as integer

	Returns:
		list: updated list
	"""	
	return [ int(x) for x in lst]

def groups_of_nine(lst):
	"""breaks down provided list in to multiple groups with max. nine elements in each group

	Args:
		lst (list): input list

	Returns:
		list: updated list of (lists: containing 9 elements)
	"""	
	lst = LST.convert_vlans_list_to_range_of_vlans_list(lst)
	lst = [ str(_) for _ in lst ]
	return LST.split(lst, 9)	

def physical_if_allowed(vlan, table):
	"""condition: checks for `filter==physical` and `vlan in vlan_members`

	Args:
		vlan (str, int): vlan number
		table (dict): dataframe dictionary

	Returns:
		int: interface value of matching row
	"""	
	for key, data in table.items():
		if data['filter'].lower()=='physical' and int(vlan) in LST.expand_vlan_list(str_to_list(data['vlan_members'])):
			return data['interface']
	return ""

def remove_trailing_zeros(net):
	"""removes the trailing zeros from given ipv6 address

	Args:
		net (str): input ipv6 address

	Returns:
		str: updated ipv6 address by removing trailing zeros
	"""	
	while True:
		trimmers = ( "::0", ":0", "::")
		exit = True
		for t in trimmers:
			if net.endswith(t):
				net = net[:-1*len(t)]
				exit = False
		if exit: break
	return net


def ipv6_urpf_acl_network(subnet):
	"""provides ipv6 address network ip 

	Args:
		subnet (str): ipv6 address

	Returns:
		str: network address value for provided ipv6 address
	"""	
	pfx = ip.ip_interface(subnet)
	return str(pfx.network.network_address)

def nth_ip(net, n, withMask=False):
	"""get n-th ip address of given network.
	withMask: will return value along with mask otherwise only subnet 

	Args:
		net (str): input ipv4 address
		n (int): number (number of ip address to be return from subnet)
		withMask (bool, optional): return with mask or without mask. Defaults to False.

	Returns:
		str: nth ip address from subnet
	"""	
	try:
		_net = str(ip.ip_interface(net).network)
		v4 = ip_addressing(_net)
		return v4.n_thIP(n, True) if withMask else v4[n]
	except ValueError:
		return ""

def mask(net):
	"""get the subnet mask for given network (eg: 24)

	Args:
		net (str): input ipv4 address

	Returns:
		str: subnet mask
	"""	
	if net:
		_net = str(ip.ip_interface(net).network)
		v4 = ip_addressing(_net)
		return v4.mask
	else:
		return 'n/a'

def netmask(net):
	"""get network mask for given network (eg: 255.255.255.0)

	Args:
		net (str): input ipv4 address

	Returns:
		str: subnet mask
	"""	
	try:
		return str(ip.ip_interface(net).netmask)
	except:
		return ""

def invmask(net):
	"""get inverse mask for given network (eg: 0.0.0.255)

	Args:
		net (str): input ipv4 address

	Returns:
		str: subnet mask
	"""	
	v4 = v4addressing(net)
	return str(v4.invmask)

def addressing(net): 
	"""get the ip of given subnet

	Args:
		net (str): input ipv4 address

	Returns:
		str: ip address
	"""	
	return ip.ip_interface(net)

def int_to_str(data):
	"""get the actual physical interface value by removing training sub interfaces.

	Args:
		data (str): input interface string

	Returns:
		str: trunkated interface (after removal of sub-interface value)
	"""	
	return str(data).split(".")[0]

def v4addressing(ip, mask="32"):
	"""get the IPv4 objetct for given ip/mask (default mask=32)

	Args:
		ip (str): input ip address/mask value
		mask (str, optional): ip_mask. Defaults to "32".

	Returns:
		IPv4: IPv4 object
	"""	
	if ip.find("/") > 0: return IPv4(ip)
	return IPv4(ip+"/"+str(mask))

def get_summaries(lst_of_pfxs):
	"""get the summaries for provided prefixes.

	Args:
		lst_of_pfxs (list): list of prefixes to be summarized

	Returns:
		list: list of summarized prefixes
	"""	
	lst_of_pfxs = LST.remove_empty_members(lst_of_pfxs)
	try:
		return nt_get_summaries(*lst_of_pfxs)
	except:
		print(f"[-] ERROR RECEIVE SUMMARIES")# {lst_of_pfxs}")
		return []

def iprint(x): 
	"""i print function to be use withing jinja template for debug.

	Args:
		x (str): value to be print during junja process
	"""	
	print(x)

def get_item(lst, n):
	"""get the nth item from list

	Args:
		lst (list): list containing various items
		n (int): index of item to be retrived 

	Returns:
		str: n-th item from list
	"""
	try:
		if isinstance(lst, (list, tuple)):
			return lst[n]
		else:
			return lst
	except:
		return lst

def as_path_repeat(asn, times):
	"""as-path repeat function

	Args:
		asn (str): as number
		times (int): number of time to be repeated.

	Returns:
		str: as path appended string
	"""	
	if not asn: return ""
	asn = asn.strip() + " "
	asp_prep_string = asn*times
	return asp_prep_string.strip()

def string(s):
	return str(s) + " "

def string_as_is(s):
	return str(s)