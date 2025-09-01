
# ---------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------
from os import popen
from nettoolkit.pyNetCrypt.jpw_cracker import juniper_decrypt
from nettoolkit.nettoolkit_common.gpl import standardize_if, STR, LST

# ---------------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------------
def nslookup(ip):
	"""return discovered hostname for provided ip

	Args:
		ip (str): ip address

	Returns:
		str: domain name string
	"""	
	lst = popen(f"nslookup {ip}").read().split("\n")
	for line in lst:
		if line.startswith("Name"): return line.split()[-1]
	return ""

def get_int_ip(ip): 
	"""get ip address from ip/mask info

	Args:
		ip (str): ip with mask

	Returns:
		str: ip address
	"""	
	return ip.split("/")[0]

def get_int_mask(ip): 
	"""get mask from ip/mask info

	Args:
		ip (str): ip with mask

	Returns:
		str: mask
	"""	
	return ip.split("/")[-1]
# ================================================================================================


# -----------------------------------------------------------------------------
#                               IP OPERATIONS                                 #
# -----------------------------------------------------------------------------

class IP():
	"""Collection of static methods for Networking on (IP).
	see more...	
	"""

	@staticmethod
	def ping_average(ip):
		"""return average ping responce for provided ip

		Args:
			ip (str): ip address string

		Returns:
			int, None: responce time or None
		"""		
		lst = popen(f"ping {ip}").read().split("\n")
		for x in lst:
			if "Average" in x:
				avg = x.split()[-1]
				s = ''
				for i, n in enumerate(avg):
					if n.isdigit(): s += n
				return int(s)

	@staticmethod
	def bin2dec(binmask):
		"""convert binary mask to decimal mask

		Args:
			binmask (str): binary mask value

		Returns:
			int: Decimal mask
		"""		
		return 32 - IP.inv2dec(binmask)

	@staticmethod
	def inv2dec(invmask):
		"""convert inverse mask to decimal mask

		Args:
			invmask (str): inverse mask value

		Returns:
			int: Decimal mask
		"""		
		m_octs = invmask.split(".")
		count_of_ones = 0
		for x in m_octs:
			x = bin(int(x))
			count_of_ones += x.count("1")
		return 32 - count_of_ones



# ------------------------------------------------------------------------------
# JUNIPER HELPER FUNCTIONS FOR FACTS DERIVE
# ------------------------------------------------------------------------------
def get_vlans_juniper(spl, how="s"):
	"""get the list of vlans on the interface

	Args:
		spl (list): splitted line

	Returns:
		list: list of vlans
	"""    	
	memberlist_identifiers = ('vlan-id-list', 'members')
	is_any_members = False
	for memid in memberlist_identifiers:
		is_any_members = memid in spl
		if is_any_members: break
	if not is_any_members: return None
	_rng_vls = spl[spl.index(memid)+1:][0].split("-")
	_spl_vls = [x for x in range(int(_rng_vls[0]), int(_rng_vls[-1])+1)]
	int_vl_list = [int(vl) for vl in _spl_vls]
	str_vl_list = [str(vl) for vl in _spl_vls]
	if how == 's':
		return str_vl_list
	else:
		return int_vl_list

def get_juniper_pw_string(spl, key_index):
	"""get plain-text-password from encrypted password. 

	Args:
		spl (list): splitted set command list for password entry.
		key_index (int): index of password 

	Returns:
		str: decrypted password
	"""	
	pw = " ".join(spl[key_index:]).strip().split("##")[0].strip()
	if pw[0] == '"': pw = pw[1:]
	if pw[-1] == '"': pw = pw[:-1]
	try:
		pw = juniper_decrypt(pw)
	except: pass
	return pw


# ------------------------------------------------------------------------------
# CISCO HELPER FUNCTIONS FOR FACTS DERIVE
# ------------------------------------------------------------------------------


def expand_if(ifname):
	"""get the full length interface string for variable length interface

	Args:
		ifname (str): variable length interface name

	Returns:
		str: updated interface string
	"""    	
	return standardize_if(ifname, True)

def expand_if_dict(d):
	"""returns updated the dictionary with standard expanded interface format in keys.

	Args:
		d (dict): dictionary where keys are interface names

	Returns:
		dict: updated dictionary keys with standard expanded interface format
	"""
	return {standardize_if(k, True):v for k, v in d.items()}

def get_interface_cisco(line):
	"""get the standard interface string from interface config line

	Args:
		ifname (str): line starting with interface [interface name]

	Returns:
		str: standard interface string
	"""    	
	return STR.if_standardize(line[10:])


# ----------------------------------------------------------
def get_vlans_cisco(line):
	"""set of vlan numbers allowed for the interface.

	Args:
		line (str): interface config line containing vlan info

	Returns:
		dict: vlan information dictionary
	"""    	
	vlans = {'vlan_members': set(), 'access_vlan': None, 'voice_vlan': None, 'native_vlan': None}
	line = line.strip()
	if line.startswith("switchport trunk allowed"):
		vlans['vlan_members'] = LST.list_variants(trunk_vlans_cisco(line))['csv_list']
	elif line.startswith("switchport access vlan"):
		vlans['access_vlan'] = line.split()[-1]
	elif line.startswith("switchport voice vlan"):
		vlans['voice_vlan'] = line.split()[-1]
	elif line.startswith("switchport trunk native"):
		vlans['native_vlan'] = line.split()[-1]
	else:
		return None
	return vlans

def trunk_vlans_cisco(line):
	"""supportive to get_vlans_cisco(). derives trunk vlans

	Args:
		line (str): interface config line containing vlan info

	Returns:
		list, set: list or set of trunk vlans
	"""    	
	for i, s in enumerate(line):
		if s.isdigit(): break
	line = line[i:]
	# vlans_str = line.split()[-1]
	# vlans = vlans_str.split(",")
	line = line.replace(" ", "")
	vlans = line.split(",")
	if not line.find("-")>0:
		return vlans
	else:
		newvllist = []
		for vlan in vlans:
			if vlan.find("-")==-1: 
				newvllist.append(vlan)
				continue
			splvl = vlan.split("-")
			for vl in range(int(splvl[0]), int(splvl[1])+1):
				newvllist.append(vl)
		return set(newvllist)
# ---------------------------------------------------------------




# ---------------------------------------------------------------

def get_vrf_cisco(line):
	"""get the standard vrf string from vrf config line

	Args:
		ifname (str): line starting with vrf definition [vrf name]

	Returns:
		str: standard interface string
	"""    	
	vrfname = line.split()[-1]	
	return vrfname



# ---------------------------------------------------------------