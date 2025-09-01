"""juniper interface from config command output parser """

# ------------------------------------------------------------------------------
from .common import *
from .run import Running
from .protocol_ospf_run import get_area_interface_auth_attributes
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  interface parser functions
# ------------------------------------------------------------------------------

def get_int_description(port_dict, l, spl):
	if "description" not in spl: return
	desc_idx = spl.index("description")
	description = " ".join(spl[desc_idx+1:])
	port_dict['description'] = description

def get_int_ip_details(port_dict, l, spl):
	inet_address = _get_v4_address(spl, l)
	if not inet_address: return		
	inet_subnet = _get_v4_subnet(inet_address)
	ip_type = _is_primary_or_secondary(spl)
	if not ip_type:
		dic = add_blankdict_key(port_dict, 'secondary') if port_dict.get("primary") else port_dict
	else:
		dic = add_blankdict_key(port_dict, ip_type)	
	dic['inet_address'] = inet_address
	dic['inet_subnet']  = inet_subnet

def get_int_ipv6_details(port_dict, l, spl):
	address = _get_v6_address(spl, l)
	if not address: return
	link_local = _is_link_local(address)
	if link_local :
		return None
	ip_type = _is_primary_or_secondary(spl)
	if not ip_type:	
		port_dict['inet6_address'] = address
		port_dict['inet6_subnet']  = shrink(get_v6_subnet(address))
	else:
		dic = add_blankdict_key(port_dict, ip_type)	
		dic['inet6_address'] = address
		dic['inet6_subnet']  = shrink(get_v6_subnet(address))

def get_int_port_mode(port_dict, l, spl):
	mode = 'interface-mode' in spl or 'port-mode' in spl
	if not mode: return None
	port_dict['port_mode'] = spl[-1]

def get_int_vlan_details(port_dict, l, spl):
	vlans = get_vlans_juniper(spl, "s")
	if not vlans: return None
	if port_dict.get('port_mode') and port_dict['port_mode'] == 'trunk':
		key = 'vlan_members'
	elif port_dict.get('port_mode') and port_dict['port_mode'] == 'access':
		key = 'access_vlan'
	else:
		return None
	if not port_dict.get(key): 			
		port_dict[key] = str(",".join(vlans))
	else:
		port_dict[key] += ","+str(",".join(vlans))

def get_int_channel_grp(port_dict, l, spl):
	if spl[-2] != "802.3ad": return
	_dict = add_blankdict_key(port_dict, 'port-channel')
	_dict['grp'] = spl[-1][2:]
	_dict['interface'] = spl[-1]


def get_int_instance(port_dict, l, spl):
	port_dict['vrf'] = spl[2]


def get_int_ospf_auth(port_dict, l, spl):
	if "ospf" not in spl or  "authentication" not in spl: return
	ospf_dict = add_blankdict_key(port_dict, 'ospf')
	line = l.split(" protocols ospf ")[-1]
	spl = line.split()
	get_area_interface_auth_attributes(ospf_dict, line, spl)


# ------------------------------------------------------------------------------
#  interface extractor class
# ------------------------------------------------------------------------------

@dataclass
class RunningInterfaces(Running):
	cmd_op: list[str, ] = field(default_factory=[])

	int_attr_functions = (
		get_int_description,
		get_int_ip_details,
		get_int_ipv6_details,		
		get_int_channel_grp,
		get_int_port_mode,
		get_int_vlan_details,
	)		

	instance_attr_functions = (
		get_int_instance,
	)

	ospfauth_attr_functions = (
		get_int_ospf_auth,
	)

	def __post_init__(self):
		super().__post_init__()

	def __call__(self):
		self.iterate_logical_systems(hierarchy='interfaces')

	def start(self):
		self.interface_dict = {}
		self.intf_lines = self.filter_interface_lines()
		self.spl_intf_lines = [ line.strip().split() for line in self.intf_lines ]
		self.get_interfaces_lines_dict()
		#
		self.intstance_lines = self.filter_instance_lines()
		self.spl_intstance_lines = [ line.strip().split() for line in self.intstance_lines ]
		self.get_instance_lines_dict()
		#
		self.ospfauth_lines = self.filter_ospfauth_lines()
		self.spl_ospfauth_lines = [ line.strip().split() for line in self.ospfauth_lines ]
		self.get_ospfauth_lines_dict()
		# #
		self.get_attributes()
		#
		return self.interface_dict

	@property
	def lines_to_function_map(self):
		try:
			return {
				self.int_attr_functions: self.interface_lines_dict,
				self.instance_attr_functions: self.instance_lines_dict,
				self.ospfauth_attr_functions: self.ospfauth_lines_dict,
			}
		except:
			raise Exception(f"[-] MissingFunctionLinesMap: Invalid or unavailable dictionary, Check input")

	### /// Interface /// ###

	def filter_interface_lines(self):
		intf_lines = [line for line in self.set_cmd_op if line.startswith("set interfaces ")]
		intf_lines = [line for line in intf_lines if not line.startswith("set interfaces interface-range")]
		return intf_lines

	def get_interfaces_lines_dict(self):
		self.interface_lines_dict = {}
		int_type = None
		for line, spl in zip(self.intf_lines, self.spl_intf_lines) :
			self.update_lines_dict(line, spl, port_idx=2, lines_dict=self.interface_lines_dict)


	### /// Instance /// ###

	def filter_instance_lines(self):		
		return [line for line in self.set_cmd_op if line.startswith("set routing-instances ")]

	def get_instance_lines_dict(self):
		self.instance_lines_dict = {}
		int_type = None
		for line, spl in zip(self.intstance_lines, self.spl_intstance_lines) :
			if spl[1] != 'routing-instances' or spl[-2] != 'interface': continue
			self.update_lines_dict(line, spl, port_idx=-1, lines_dict=self.instance_lines_dict)

	### /// Ospf auth /// ###

	def filter_ospfauth_lines(self):		
		return [line for line in self.set_cmd_op if line.find(" protocols ospf ") > -1]

	def get_ospfauth_lines_dict(self):
		self.ospfauth_lines_dict = {}
		int_type = None
		for line, spl in zip(self.ospfauth_lines, self.spl_ospfauth_lines) :
			ospf_idx = spl.index('ospf')
			if len(spl)<ospf_idx+6 or spl[ospf_idx+3] != 'interface': continue
			port_idx = ospf_idx + 4
			self.update_lines_dict(line, spl, port_idx, lines_dict=self.ospfauth_lines_dict)

	### /// attributes /// ###

	def get_attributes(self):
		for fns, x_lines_dic in self.lines_to_function_map.items():
			for int_type, intf_dict in x_lines_dic.items():
				type_dict = add_blankdict_key(self.interface_dict, int_type.lower())
				for port, lines_dic in intf_dict.items():
					port_dict = get_numbered_port_dict(op_dict=type_dict, port=port)
					for line in lines_dic['lines']:
						spl = line.split()
						for f in fns:
							# try:
								f(port_dict, line, spl)
							# except IndexError: pass

	### /// lines /// ###

	@staticmethod
	def update_lines_dict(line, spl, port_idx, lines_dict):
		int_type = get_juniper_int_type(spl[port_idx])
		p = _juniper_port(int_type, spl, port_idx)
		if not int_type or not p: return
		type_dict = add_blankdict_key(lines_dict, int_type.lower())
		port_dict = add_blankdict_key(type_dict, p)
		lines  = add_blanklist_key(port_dict, 'lines')
		lines.append(line)


# ===================================================================================================

# ------------------------------------------------------------------------------
#  // port supportive
# ------------------------------------------------------------------------------
def _juniper_port(int_type, spl, port_idx):
	if 'unit' in spl:
		i = spl.index('unit')
		if int(spl[i+1]) != 0:
			return spl[i-1] + "." + spl[i+1]
	if spl[port_idx].endswith(".0"):
		return spl[port_idx][:-2]
	return spl[port_idx]

# ------------------------------------------------------------------------------
# // ipv4
# ------------------------------------------------------------------------------
def _is_v4_addressline(line):	
	if line.find("family inet ") == -1: return None
	if line.find("address") == -1: return None
	return True

def _get_v4_address(spl, line):
	if not _is_v4_addressline(line): return None
	return spl[spl.index("address") + 1]

def _get_v4_subnet(address):
	return get_subnet(address)

def _is_primary_or_secondary(spl):
	if 'primary'   in spl: return 'primary'
	if 'secondary' in spl: return 'secondary'
	return None

# ------------------------------------------------------------------------------
# // ipv6
# ------------------------------------------------------------------------------

def _get_v6_address(spl, line):
	v6ip = _is_v6_addressline(spl, line)
	if not v6ip : return None
	return v6ip

def _is_v6_addressline(spl, line):
	if line.find("family inet6") == -1: return None
	try:
		if spl[spl.index('inet6')+1] != 'address': return None
	except: return None
	return spl[spl.index('inet6')+2]

def _is_link_local(v6_ip):
	return v6_ip.lower().startswith("fe80:")

# ------------------------------------------------------------------------------
# // ospf auth
# ------------------------------------------------------------------------------
def _is_ospf_auth_line(line=None, spl=None):
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
	voice_vlans = set()
	for l in set_cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("#"): continue
		if not l.strip().startswith("set switch-options voip "): continue
		spl = l.split()
		if spl[-2] == 'vlan':
			voice_vlans.add(spl[-1])
	return voice_vlans

# ========================================================================================


# ------------------------------------------------------------------------------
#  interfaces parser calling function
# ------------------------------------------------------------------------------
def get_interfaces_running(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: interfaces level parsed output dictionary
	"""    	
	R  = RunningInterfaces(cmd_op)
	R()
	return R.logical_systems_dict
# ------------------------------------------------------------------------------

