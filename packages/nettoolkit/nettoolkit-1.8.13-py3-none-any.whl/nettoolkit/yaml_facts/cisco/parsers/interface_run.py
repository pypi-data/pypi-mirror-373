"""cisco show running-config parser for interface section outputs """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  interface attr functions
# ------------------------------------------------------------------------------

## //// STATES //// ##
def get_int_description(port_dict, l, spl):
	if spl[0] != 'description': return
	port_dict['description'] = " ".join(spl[1:])

def get_int_state(port_dict, l, spl):
	if spl[0] != 'shutdown': return
	port_dict['link_status'] = 'administratively down'

## //// IP v4/v6 ADDRESS //// ##
def get_int_ip_details(port_dict, l, spl):
	address = get_inet_address(l)
	secondary_address = get_secondary_inet_address(l)
	if address:
		port_dict['inet_address'] = address
		port_dict['inet_subnet'] = get_subnet(address)
	if secondary_address: 
		port_dict['inet_address_secondary'] = secondary_address
		port_dict['inet_subnet_secondary'] = get_subnet(secondary_address)

def get_int_ipv6_details(port_dict, l, spl):
	link_local = 'link-local' in spl
	if l.find("anycast") > -1: return None
	address = get_inetv6_address(l, link_local)
	if link_local or not address: return None
	port_dict['inet6_address'] = address
	port_dict['inet6_subnet'] = shrink(get_v6_subnet(address))
	port_dict['h4block'] = IPv6(address).getHext(4)

## //// SWITCHPORT //// ##
def get_int_mode_details(port_dict, l, spl):
	if not l.strip().startswith('switchport mode '): return
	port_dict['interface_mode'] = spl[-1]

def get_int_vlan_details(port_dict, l, spl):
	vlans = get_vlans_cisco(l)
	if not vlans: return None
	for k, v in vlans.items():
		if v and port_dict.get(k): 
			port_dict[k] += ","+str(v)
		elif v and not port_dict.get(k): 
			port_dict[k] = v

## //// VRF INSTANCE //// ##
def get_int_vrf(port_dict, l, spl):
	vrf = None
	if (l.startswith("vrf forwarding") 
		or l.startswith("ip vrf forwarding")):
		vrf = spl[-1]
	if not vrf: return None
	port_dict['vrf'] = vrf

## //// UDLD //// ##
def get_int_udld(port_dict, l, spl):
	if not l.strip().startswith("udld port "): return
	port_dict['int_udld'] = " ".join(spl[2:])

## //// PORT CHANNEL //// ##
def get_int_channel_group(port_dict, l, spl):
	po = None
	if spl[0] != "channel-group": return
	po = spl[1]
	po_mode = spl[-1]
	po_dict = add_blankdict_key(port_dict, 'port-channel')
	po_dict['interface'] = "Port-channel" + po
	po_dict['mode'] = po_mode
	po_dict['group'] = po

## //// DHCP HELPER //// ##
def get_int_v4_helpers(port_dict, l, spl):
	if spl[2] != "helper-address": return
	append_attribute(port_dict, 'v4_helpers', spl[-1])

def get_int_v6_helpers(port_dict, l, spl):	
	if not l.startswith("ipv6 dhcp relay destination"): return
	append_attribute(port_dict, 'v6_helpers', spl[-1])

## //// IP RIP //// ##
def get_int_rip(port_dict, l, spl):	
	if l.startswith('ip rip '):
		rip_dict = add_blankdict_key(port_dict, 'rip')
		_int_rip_auth_keychain(rip_dict, l, spl)
		_int_rip_auth_mode(rip_dict, l, spl)
		_int_rip_version(rip_dict, l, spl)
	if 'rip' in spl:
		rip_dict = add_blankdict_key(port_dict, 'rip')
		_int_rip_summary_address(rip_dict, l, spl)
	_int_rip_split_horizon(port_dict, l, spl)

def _int_rip_auth_keychain(rip_dict, l, spl):
	if not l.startswith("ip rip authentication key-chain"): return
	dic = add_blankdict_key(rip_dict, 'authentication')
	dic['key-chain'] = spl[-1]

def _int_rip_auth_mode(rip_dict, l, spl):
	if not l.startswith("ip rip authentication mode "): return
	dic = add_blankdict_key(rip_dict, 'authentication')
	dic['mode'] = spl[-1]

def _int_rip_version(rip_dict, l, spl):
	txrx = ('send', 'receive')
	for way in txrx:
		if not l.startswith(f"ip rip {way} version"): continue
		rip_dict[f'{way}-version'] = spl[-1]

def _int_rip_split_horizon(port_dict, l, spl):
	if l.find("ip split horizon") == -1: return
	rip_dict = add_blankdict_key(port_dict, 'rip')
	rip_dict['split-horizon'] = spl[1] == 'no'

def _int_rip_summary_address(rip_dict, l, spl):
	if not l.startswith("ip summary-address rip "): return
	network = str(addressing(spl[-2], spl[-1]))
	append_attribute(rip_dict, 'summaries', network)

## //// IP OSPF //// ##
def get_int_ospf_auth(port_dict, l, spl):
	if not l.startswith("ip ospf "): return
	ospf_dict = add_blankdict_key(port_dict, 'ospf')
	if spl[2] == "authentication-key":
		try:
			update_key_value(ospf_dict, 'auth_key', decrypt_type7(spl[-1]))
		except:
			update_key_value(ospf_dict, 'auth_key', spl[-1])
	elif spl[2] == "message-digest-key":
		try:
			update_key_value(ospf_dict, 'md5_key', decrypt_type7(l.strip().split()[-1]))
		except:
			update_key_value(ospf_dict, 'md5_key', l.strip().split()[-1])
	elif spl[2] == "authentication":
		update_key_value(ospf_dict, 'auth_type', spl[-1])
	elif spl[2] == "network":
		update_key_value(ospf_dict, 'network_type', l.split(' ospf network ')[-1])

## //// IP EIGRP //// ##
def get_int_eigrp(port_dict, l, spl):	
	if 'eigrp' not in spl: return
	dic = add_blankdict_key(port_dict, 'eigrp')
	dic = add_blankdict_key(dic, next_index_item(spl, 'eigrp'))  ##  PROCESS ID 
	_int_eigrp_auth(dic, l, spl)
	_int_eigrp_summary(dic, l, spl)
	_int_eigrp_splithorizon(dic, l, spl)
	_int_eigrp_attrs(dic, l, spl)

def _int_eigrp_auth(dic, l, spl):
	if 'authentication' not in spl: return
	if 'mode' in spl:
		dic = add_blankdict_key(dic, 'authentication')
		update_key_value(dic, 'mode', spl[-1])
	if 'key-chain' in spl:
		dic = add_blankdict_key(dic, 'authentication')
		update_key_value(dic, 'key-chain', spl[-1] )

def _int_eigrp_summary(dic, l, spl):
	if "summary-address" not in spl: return
	dic = add_blankdict_key(dic, 'summaries')
	dic = add_blankdict_key(dic, str( cisco_addressing_on_list(spl, 4, 5) ))
	diff = 1 if "/" in spl[4] else 0
	if len(spl) > 6-diff:
		try:
			append_attribute(dic, 'AD', spl[6-diff])
		except: pass
		if 'leak-map' in spl:
			update_key_value(dic, 'leak-map', next_index_item(spl, 'leak-map'))

def _int_eigrp_splithorizon(dic, l, spl):
	if "split-horizon" not in spl: return
	dic["split-horizon"] = spl[0] != 'no'

def _int_eigrp_attrs(dic, l, spl):
	attrs = ('hello-interval', 'hold-time', 'bandwidth-percent', )
	_int_update_next_attrs(dic, l, spl, attrs)

## //// IP ISIS //// ##
def get_int_isis(port_dict, l, spl):	
	if 'isis' not in spl: return
	isis_dict = add_blankdict_key(port_dict, 'isis')
	_int_isis_router_area(isis_dict, l, spl)
	_int_isis_attrs(isis_dict, l, spl)
	_int_isis_attrs_for_level(isis_dict, l, spl)
	_int_isis_auth(isis_dict, l, spl)

def _int_isis_router_area(dic, l, spl):
	if l.startswith("ip router isis"):
		area = 0 if len(spl) == 3 else spl[-1]
		isis_af_type = 'ipv4'
	elif l.startswith("ipv6 router isis"):
		area = 0 if len(spl) == 3 else spl[-1]
		isis_af_type = 'ipv6'
	else:
		return
	update_key_value(dic, 'area-id', area)
	update_key_value(dic, 'af-type', isis_af_type)

def _int_isis_attrs(dic, l, spl):
	attrs = ('protocol', 'network', 'circuit-type', 'tag',  )
	if spl[1] not in attrs: return
	_int_update_next_attrs(dic, l, spl, attrs)

def _int_isis_attrs_for_level(dic, l, spl):
	attrs = ('priority', 'metric',  'ipv6')
	if spl[1] not in attrs: return
	dic = add_blankdict_key(dic, spl[1])
	_int_isis_add_trailings(dic, l, spl, 1)	

def _int_isis_auth(dic, l, spl):
	auth_candidates = ("authentication", "password")
	if spl[1] not in auth_candidates: return
	dic = add_blankdict_key(dic, spl[1])
	_int_isis_add_trailings(dic, l, spl, 1)	

     ### COMMON ###
def _int_isis_add_trailings(dic, l, spl, candidate_index):
	for i in range(candidate_index+1, len(spl)-1):
		if i+2 < len(spl): 
			dic = add_blankdict_key(dic, spl[i])
		else:
			update_key_value(dic, spl[i], spl[-1])
	
def _int_update_next_attrs(dic, l, spl, attrs):
	for attr in attrs:
		if attr not in spl: continue
		dic[attr] = spl[-1]


# ====================================================================================================
#  interface Config extractor Class
# ====================================================================================================

@dataclass
class RunningInterfaces():
	cmd_op: list[str,] = field(default_factory=[])

	attr_functions = [
		get_int_description,
		get_int_state,
		get_int_ip_details,
		get_int_ipv6_details,
		get_int_mode_details,
		get_int_vlan_details,
		get_int_vrf,
		get_int_udld,
		get_int_channel_group,
		get_int_v4_helpers,
		get_int_v6_helpers,	
		get_int_rip,
		get_int_ospf_auth,
		get_int_eigrp,
		get_int_isis,

	]

	def __post_init__(self):
		self.interface_dict = {}
		self.port_lines_dict = self.get_interfaces_lines_dict()
		self._iterate()

	def _iterate(self):
		for int_type, ports_dict in self.port_lines_dict.items():
			int_type_dic = add_blankdict_key(self.interface_dict, int_type)
			for port, port_lines_dict in ports_dict.items():
				dic = add_blankdict_key(int_type_dic, port)
				dic.update( self._get_attributes(port_lines_dict['lines']) )


	def _get_attributes(self, lines):
		attr_dict = {}
		for line in lines:
			line = line.strip()
			spl  = line.split()
			for f in self.attr_functions:
				try: 
					f(attr_dict, line, spl)
				except IndexError: pass
		return attr_dict		


	def get_interfaces_lines_dict(self):
		int_toggle = False
		port_lines_dict = {}
		for l in self.cmd_op:
			if blank_line(l): continue
			if int_toggle and l.strip().startswith("!"): 
				int_toggle = False
				append_attribute(port_dict, 'lines', lst)
				continue
			if l.startswith("interface "):
				p = get_interface_cisco(l)
				if not p: continue
				#
				int_filter = get_cisco_int_type(p)
				int_type_dict = add_blankdict_key(port_lines_dict, int_filter)
				p = update_port_on_int_type(p)
				port_dict = add_blankdict_key(int_type_dict, p)
				int_toggle = True
				lst = []
				continue
			if int_toggle:
				lst.append(l)
		return port_lines_dict


# ====================================================================================================
#  interface running Config extractor function
# ====================================================================================================


def get_interfaces_running(command_output):
	"""parse output of : show running-config

	Args:
		command_output (list): command output

	Returns:
		dict: interfaces level parsed output dictionary
	"""    	
	R  = RunningInterfaces(command_output)

	return {'interfaces': R.interface_dict }

# ====================================================================================================
