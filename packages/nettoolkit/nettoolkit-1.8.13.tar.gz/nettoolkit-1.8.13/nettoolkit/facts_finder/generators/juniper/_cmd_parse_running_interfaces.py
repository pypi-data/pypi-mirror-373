"""juniper interface from config command output parser """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *
from ._cmd_parse_running import Running


merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningInterfaces(Running):
	"""object for interface level config parser

	Args:
		cmd_op (list, str): config output, either list or multiline string
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the  config output
		"""    		    		
		super().__init__(cmd_op)
		self.interface_dict = OrderedDict()

	def interface_read(self, func):
		"""directive function to get the various interface level output

		Args:
			func (method): method to be executed on interface config line

		Returns:
			dict: parsed output dictionary
		"""    		
		ports_dict = OrderedDict()
		for l in self.set_cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("#"): continue
			if l.startswith("set interfaces interface-range"): continue
			if not l.startswith("set interfaces"): continue
			spl = l.split()
			int_type = None
			for k, v in JUNIPER_IFS_IDENTIFIERS.items():
				if spl[2].startswith(v):
					int_type = k
					break
			if not int_type: 
				print(f"[-] UndefinedInterface(Type)-{spl[2]}")
				continue
			p = _juniper_port(int_type, spl)
			if not p: continue
			if not ports_dict.get(p): ports_dict[p] = {}
			port_dict = ports_dict[p]
			func(port_dict, l, spl, p)
		return ports_dict


	def routing_instance_read(self):
		"""directive function to set the various routing instance level output from interface.
		"""    		
		foundavrf = False
		for l in self.set_cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("#"): continue
			if not l.startswith("set routing-instances "): continue
			spl = l.split()
			try:
				# print(l)
				if spl[3] == 'interface':
					# print(l)
					vrf = spl[2]
					intf = spl[-1]
					# print(vrf, intf)
					self.interface_dict[intf]['intvrf'] = vrf
					foundavrf = True
			except:
				continue

		for intf, intf_vals in self.interface_dict.items():
			intf_vals['intvrf'] = ""
			break

	def ospf_auth_para_read(self, func):
		"""directive function to get the various protocol ospf level output

		Args:
			func (method): method to be executed on ospf config lines

		Returns:
			dict: parsed output dictionary
		"""    		
		ports_dict = OrderedDict()
		for l in self.set_cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("#"): continue
			spl = l.split()
			ospf_idx = _is_ospf_auth_line(l, spl)
			if not ospf_idx: continue
			if len(spl)>ospf_idx+6 and spl[ospf_idx+3] == 'interface':
				p = spl[ospf_idx+4]
				if not p: continue
				if not ports_dict.get(p): ports_dict[p] = {}
				port_dict = ports_dict[p]
				#
				if not (port_dict.get('filter') and port_dict['filter']):
					port_dict['filter'] = get_juniper_int_type(p).lower()
				#
				func(port_dict, l, spl, ospf_idx)
		return ports_dict



	## --------------------------------------------------------------------------------

	def interface_ips(self):
		"""update the interface ipv4 ip address details
		"""    		
		func = self.get_ip_details
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_ip_details(port_dict, l, spl, p):
		"""parser function to update interface ipv4 ip address details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""    		
		subnet = _get_v4_subnet(spl, l)
		if not subnet: return		
		port_dict['subnet'] = subnet

	def interface_v6_ips(self):
		"""update the interface ipv6 ip address details
		"""    		
		func = self.get_ipv6_details
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_ipv6_details(port_dict, l, spl, p):
		"""parser function to update interface ipv6 ip address details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""    		
		address = _get_v6_address(spl, l)
		if not address: return
		link_local = _is_link_local(address)
		if link_local :
			return None
		port_dict['v6subnet'] = get_v6_subnet(address)


	def interface_vlans(self):
		"""update the interface vlan details
		"""   
		func = self.get_int_vlan_details
		merge_dict(self.interface_dict, self.interface_read(func))

	def get_int_vlan_details(self, port_dict, l, spl, p):
		"""parser function to update interface vlan details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""
		vlans = get_vlans_juniper(spl, "s")
		if not vlans: return None
		# key = 'access_vlan'
		if self.interface_dict[p].get('interface_mode') and self.interface_dict[p]['interface_mode'] == 'trunk':
			key = 'vlan_members'
		elif self.interface_dict[p].get('interface_mode') and self.interface_dict[p]['interface_mode'] == 'access':
			key = 'access_vlan'
		else:
			return None
		if not port_dict.get(key): 			
			port_dict[key] = str(",".join(vlans))
		else:
			port_dict[key] += ","+str(",".join(vlans))
		for vlan in vlans:
			if vlan in self.voice_vlans:
				port_dict['voice_vlan'] = vlan

	def interface_mode(self):
		"""update the interface port mode trunk/access details
		"""   
		func = self.get_interface_mode
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_interface_mode(port_dict, l, spl, p):
		"""parser function to update interface port mode trunk/access details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""    		
		mode = 'interface-mode' in spl or 'port-mode' in spl
		if not mode: return None
		if not port_dict.get('interface_mode'): port_dict['interface_mode'] = spl[-1]


	def interface_description(self):
		"""update the interface description details
		"""   
		func = self.get_int_description
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_int_description(port_dict, l, spl, p):
		"""parser function to update interface description details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""    		
		description = ""
		if l.startswith("set interfaces ") and "description" in spl:
			desc_idx = spl.index("description")
			description = " ".join(spl[desc_idx+1:])
		if description and not port_dict.get('description'):
			port_dict['description'] = description
		return port_dict

	def int_filter(self):
		"""update the interface type details
		"""   
		func = self.get_int_filter
		merge_dict(self.interface_dict, self.interface_read(func))

	def get_int_filter(self, port_dict, l, spl, p):
		"""parser function to update interface type details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""
		int_type = get_juniper_int_type(spl[2])
		port_dict['filter'] = int_type.lower()

	def interface_channel_grp(self):
		"""update the interface port channel details
		"""   
		func = self.get_interface_channel_grp
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_interface_channel_grp(port_dict, l, spl, p):
		"""parser function to update interface port channel details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""	
		grp = ''
		if spl[-2] == "802.3ad":
			grp = spl[-1][2:]
			port_dict['channel_grp'] = grp
			port_dict['channel_group_interface'] = spl[-1]
		return port_dict


	# # Add more interface related methods as needed.


	## --------------------------------------------------------------------------------

	def int_dot_zero_merge_to_parent1(self):
		""" merges the value of two keys for `parent` and `parent unit 0` configs
		"""
		parents = set()
		for k, v in self.interface_dict.copy().items():
			if not k.endswith(".0"): continue
			parent = k.split(".")[0]
			if self.interface_dict.get(parent):
				parents.add(k)
				self.interface_dict[parent].update(v)
		for p in parents:
			del(self.interface_dict[p])

	def int_to_int_number(self):
		''' creates an arbirary unique number for each interface on interface types 
		'''
		for k, v in self.interface_dict.items():
			if v['filter'] == 'physical':
				v['int_number'] = get_physical_port_number(k)
				v['logical_int_number'] = get_logical_port_number(k)
				continue
			if v['filter'] == 'aggregated':
				try:
					v['int_number'] = int(k[2:])
					v['logical_int_number'] = get_logical_port_number(int(k[2:]))
				except: pass
			try:
				int_num = int(k)
				v['int_number'] = int_num
				continue
			except:
				pass
			kspl = k.split(".")
			if k.startswith("lo") or not k.endswith(".0"):
				try:
					v['int_number'] = kspl[1]
					v['logical_int_number'] = get_logical_port_number(k)
					if not k.startswith("lo") and not k.endswith(".0"):
						v['filter'] = 'vlan'
				except: pass

	# # Add more interface related methods as needed.

	# ----------------------------------------------------------------------------------
	# ospf auth methods
	# ----------------------------------------------------------------------------------

	def ospf_authentication_details(self):
		"""update the interface ospf authentication details
		"""
		func = self.get_ospf_authentication_details
		merge_dict(self.interface_dict, self.ospf_auth_para_read(func))

	@staticmethod
	def get_ospf_authentication_details(port_dict, l, spl, ospf_idx):
		"""parser function to update interface ospf authentication details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse
			ospf_idx(int): index value from where ospf information starting on set commands list

		Returns:
			None: None
		""" 
		if spl[ospf_idx+5] == 'interface-type':
			port_dict['ospf_auth_type'] = spl[-1]
		if spl[ospf_idx+5] == 'authentication':
			pw = " ".join(spl[ospf_idx+6:]).strip().split("##")[0].strip()
			if pw[0] == '"': pw = pw[1:]
			if pw[-1] == '"': pw = pw[:-1]
			try:
				pw = juniper_decrypt(pw)
			except: pass
			port_dict['ospf_auth'] = pw
		return port_dict


	# # Add more interface related methods as needed.


# ------------------------------------------------------------------------------

def get_physical_port_number(port):
	""" physical interface - interface number calculator.

	Args:
		port (str): string lateral for various types of juniper interface/port

	Returns:
		int: a number assign to port value (sequencial)
	"""
	spl_port_sc = port.split(":")
	port = spl_port_sc[0]
	spl_port_dot = port.split(".")
	port = spl_port_dot[0]
	#
	port_lst = port.split("-")[-1].split("/")
	port_id = 0
	for i, n in enumerate(reversed(port_lst)):
		multiplier = 100**i
		nm = int(n)*multiplier
		port_id += nm
	return port_id

def get_logical_port_number(port):
	""" physical interface - logical interface number calculator.

	Args:
		port (str): string lateral for various types of juniper interface/port

	Returns:
		int: a logical port number assign to port value (sequencial)
	"""
	spl_port_sc = port.split(":")
	port = spl_port_sc[0]
	spl_port_dot = port.split(".")
	port = spl_port_dot[0]
	#
	if len(spl_port_sc) > 1:
		return spl_port_sc[-1]
	if len(spl_port_dot) > 1:
		return spl_port_dot[-1]
	return ''

def get_interfaces_running(cmd_op, *args):
	"""defines set of methods executions. to get various inteface parameters.
	uses RunningInterfaces in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""    	
	R  = RunningInterfaces(cmd_op)
	R.voice_vlans = set_of_voice_vlans(R.set_cmd_op)
	R.interface_ips()
	R.interface_v6_ips()
	R.interface_mode()
	R.interface_vlans()
	R.interface_description()
	R.interface_channel_grp()
	R.int_filter()


	# # update more interface related methods as needed.
	R.int_to_int_number()
	R.routing_instance_read()
	R.ospf_authentication_details()
	R.int_dot_zero_merge_to_parent1()       ## added in place of above


	if not R.interface_dict:
		R.interface_dict['dummy_int'] = ''
	return {'op_dict': R.interface_dict}



# ------------------------------------------------------------------------------

def _juniper_port(int_type, spl):
	"""get port/interface number based on interface type for split line

	Args:
		int_type (str): interface type ## deprycated, unused
		spl (list): splitted set command line list

	Returns:
		str: port number for given unit
	"""	   	
	if 'unit' in spl:
		i = spl.index('unit')
		return spl[i-1] + "." + spl[i+1]
	else:
		return spl[2]

def _get_v4_subnet(spl, line):
	"""get ipv4 subnet/mask detail from provided splitted set command line list, or string line.

	Args:
		spl (list): splitted set command line list
		line (str): string set command line

	Returns:
		str: subnet if found or None
	"""	
	if not _is_v4_addressline(line): return None
	return get_subnet(spl[spl.index("address") + 1])


def _is_v4_addressline(line):	
	"""check is there any ipv4 address configured in provided string line.

	Args:
		line (str): string set command line

	Returns:
		bool: True if found else None
	"""	
	if line.find("family inet") == -1: return None
	if line.find("address") == -1: return None
	return True
# ------------------------------------------------------------------------------


def _get_v6_address(spl, line):
	"""get ipv6 address (with Mask) from provided splitted set command line list, or string line.

	Args:
		spl (list): splitted set command line list
		line (str): string set command line

	Returns:
		str: ipv6 address if found else None
	"""	
	v6ip = _is_v6_addressline(spl, line)
	if not v6ip : return None
	return v6ip

def _is_v6_addressline(spl, line):
	"""check if any ipv6 address configured in provided string line.

	Args:
		line (str): string set command line

	Returns:
		bool,str: ipv6 address if found else None
	"""	
	if line.find("family inet6") == -1: return None
	try:
		if spl[spl.index('inet6')+1] != 'address': return None
	except: return None
	return spl[spl.index('inet6')+2]

def _is_link_local(v6_ip):
	"""checks if provided ipv6 ip is link local address or not

	Args:
		v6_ip (str): ipv6 address string

	Returns:
		bool: True if it is link local address else False
	"""	
	return v6_ip.lower().startswith("fe80:")

# ------------------------------------------------------------------------------
# // ospf auth
# ------------------------------------------------------------------------------
def _is_ospf_auth_line(line=None, spl=None):
	""" checks if provided line/splitted line is an ospf authentication line or not (provide either argument)

	Args:
		line (str, optional): set command line. Defaults to None.
		spl (list, optional): splitted set command line. Defaults to None.

	Returns:
		int: index value where `ospf` starts if line contains `protocol ospf` else None
	"""	
	if not spl:
		spl = line.split()
	if 'ospf' in spl and 'protocols' in spl:
		if spl.index('protocols') + 1 == spl.index('ospf'):
			return spl.index('ospf')
	return None

# ------------------------------------------------------------------------------
# // voice vlans
# ------------------------------------------------------------------------------

def set_of_voice_vlans(set_cmd_op):
	"""get the set of voice vlans configured in provided set commands configuration.

	Args:
		set_cmd_op (list): set command output

	Returns:
		set: set of voice vlans found in output
	"""	
	voice_vlans = set()
	for l in set_cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("#"): continue
		if not l.strip().startswith("set switch-options voip "): continue
		spl = l.split()
		if spl[-2] == 'vlan':
			voice_vlans.add(spl[-1])
	return voice_vlans

# ------------------------------------------------------------------------------
