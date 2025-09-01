"""cisco running-config parser for bgp section output """

# ------------------------------------------------------------------------------
from .common import *
from .protocols import ProtocolsConfig, get_protocol_instance_dict
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  RIP ATTR FUNCS
# ------------------------------------------------------------------------------

def __update_item_for_next_index(attr_dict, pg_dict, spl, item, f=None):
	if item not in spl: return 
	n_pg_dict = pg_dict if spl[1] == attr_dict else pg_dict['peers'][spl[1]]
	if not f:
		n_pg_dict[item] = next_index_item(spl, item)
	else:
		n_pg_dict[item] = f(next_index_item(spl, item))

def _get_str_next_items(attr_dict, pg_dict, line, spl):
	items = ('local-as', 'remote-as', 'update-source', 'unsuppress-map', 
		'exist-map', 'non-exist-map',
	)
	for item in items:
		__update_item_for_next_index(attr_dict, pg_dict, spl, item, f=None)

def _get_int_next_items(attr_dict, pg_dict, line, spl):
	items = ('advertisement-interval', )
	for item in items:
		__update_item_for_next_index(attr_dict, pg_dict, spl, item, f=int)


def __update_stub_items(attr_dict, pg_dict, spl, item):
	if item not in spl: return 
	n_pg_dict = pg_dict if spl[1] == attr_dict else pg_dict['peers'][spl[1]]
	n_pg_dict[item] = True

def _get_stub_items(attr_dict, pg_dict, line, spl):
	items = ('shutdown', 'activate', 'suppress-inactive')
	for item in items:
		__update_stub_items(attr_dict, pg_dict, spl, item)



def _get_password(attr_dict, pg_dict, line, spl):
	if spl[2] == 'password': 
		pg_dict['password'] = decrypt_type7(spl[-1]) if spl[3] == "7" else spl[-1]

def _get_description(attr_dict, pg_dict, line, spl):
	item = 'description'
	if item not in spl: return 
	n_pg_dict = pg_dict if spl[1] == attr_dict else pg_dict['peers'][spl[1]]
	n_pg_dict[item] = " ".join(spl[spl.index(item)+1:])

def _get_peers(attr_dict, pg_dict, line, spl):
	if len(spl)<4: return
	if spl[2] == 'peer-group' and spl[3] == attr_dict: 
		peers_dict = add_blankdict_key(pg_dict, 'peers')
		add_blankdict_key(peers_dict, spl[1])

def _get_max_prefix_attrs(attr_dict, pg_dict, line, spl):
	if not 'maximum-prefix' in spl:  return
	n_pg_dict = pg_dict if spl[1] == attr_dict else pg_dict['peers'][spl[1]]
	#
	max_pfx_dict = add_blankdict_key(n_pg_dict, 'max-prefix')
	mpidx = spl.index('maximum-prefix')
	max_pfx_dict['max_prefix_allowed'] = int(spl[mpidx+1])
	try:
		max_pfx_dict['threshold'] = int(spl[mpidx+2])
	except: pass
	if 'restart' in spl:
		max_pfx_dict['restart_interval'] =  int(spl[spl.index('restart')+1])
	if 'warning-only' in spl:
		max_pfx_dict['warning_only'] = True


def _get_default_originate(attr_dict, pg_dict, line, spl):
	item = 'default-originate'
	if item not in spl: return
	if 'route-map' not in spl:
		__update_stub_items(attr_dict, pg_dict, spl, item)
	else:
		rm = next_index_item(spl, 'route-map')
		n_pg_dict = pg_dict if spl[1] == attr_dict else pg_dict['peers'][spl[1]]
		n_pg_dict[item] = {'route-map': rm}

def _get_soft_reconfiguration(attr_dict, pg_dict, line, spl):
	item = 'soft-reconfiguration'
	if item not in spl: return
	if 'inbound' not in spl:
		__update_stub_items(attr_dict, pg_dict, spl, item)
	else:
		n_pg_dict = pg_dict if spl[1] == attr_dict else pg_dict['peers'][spl[1]]
		n_pg_dict[item] = 'inbound'

def _get_route_map(attr_dict, pg_dict, line, spl):
	item = 'route-map'
	if item != spl[2]: return
	rm = spl[3]
	way = spl[4]
	n_pg_dict = pg_dict if spl[1] == attr_dict else pg_dict['peers'][spl[1]]
	n_pg_dict[item] = {rm: way}

def _get_inherited_template(attr_dict, pg_dict, line, spl):
	item = 'inherit'
	if item not in spl: return
	items = ( 'peer-session', 'peer-policy' )
	for item in items:
		if item not in spl: continue
		n_pg_dict = pg_dict if spl[1] == attr_dict else pg_dict['peers'][spl[1]]
		inherited_template_name = next_index_item(spl, item)
		n_pg_dict[f'inherit-{item}'] = inherited_template_name


# ====================================================================================================

def _get_router_id(vrf_dict, line, spl):
	if line.startswith("bgp router-id "):
		vrf_dict['router-id'] = spl[-1]

def _get_networks(attr_dict, line, spl):
	if spl[0] == 'network' and spl[2] == 'mask': 
		network = str(addressing(spl[1], spl[3]))
		networks_dict = add_blankdict_key(attr_dict, 'networks')
		network_dict = add_blankdict_key(networks_dict, network)
		if 'route-map' in spl:
			append_attribute(network_dict, 'route-map', spl[spl.index('route-map')+1])
		if 'backdoor' in spl:
			append_attribute(network_dict, 'backdoor-route', True)

def _get_aggregates(attr_dict, line, spl):
	if spl[0] == 'aggregate-address': 
		try:
			network = addressing(spl[1], spl[2])
		except:
			network = addressing(spl[1])
		networks_dict = add_blankdict_key(attr_dict, 'aggregates')
		if network.version == 4:
			networks_dict = add_blankdict_key(networks_dict, 'ipv4')
		elif network.version == 6:
			networks_dict = add_blankdict_key(networks_dict, 'ipv6')
		network_dict = add_blankdict_key(networks_dict, str(network))
		if len(spl) > 3:
			stub_items = ( 'as-set', 'summary-only')
			for item in stub_items:
				if item in spl: network_dict[item] = True
			nxt_items = ( 'attribute-map', 'route-map', 'suppress-map', )
			for item in nxt_items:
				if item in spl: network_dict[item] = next_index_item(spl, item)

def _get_timers(attr_dict, line, spl):
	if line.startswith("timers bgp "):
		d = { 'keepalive': spl[2], 'holdtime': spl[3] }
		append_attribute(attr_dict, 'timers', d)

def _get_redistributions(attr_dict, line, spl):
	if spl[0] != 'redistribute': return
	redistribute = spl[1]
	redis_dict = add_blankdict_key(attr_dict, 'redistribute')
	redis_dict_l1 = add_blankdict_key(redis_dict, redistribute)
	items = ('route-map', 'ospf', 'rip', 'eigrp', 'bgp', 'isis',)
	get_instance_parameter_for_items(redis_dict_l1, line, spl, items)

# ====================================================================================================
#  BGP Config extractor Class
# ====================================================================================================

@dataclass
class BGPConf(ProtocolsConfig):
	run_list: list[str] = field(default_factory=[])

	supported_af_types = ('ipv4', 'vpnv4', 'ipv6', 'vpnv6')
	attr_functions = [
		_get_router_id,
		_get_networks,
		_get_aggregates,
		_get_timers,
		_get_redistributions,
	]
	peer_attr_functions = [
		_get_peers,
		_get_str_next_items,
		_get_int_next_items,
		_get_stub_items,
		_get_description,
		_get_password,
		_get_max_prefix_attrs,
		_get_default_originate,
		_get_soft_reconfiguration,
		_get_route_map,
		_get_inherited_template,
	]

	def __post_init__(self):
		self.bgp_peer_dict = {}
		self.protocol_config_initialize(protocol='bgp')
		self._get_bgp_peer_informations()
		self._get_template_peer_sessions_attr_dict()
		self._iterate_vrfs()
		self.remove_empty_vrfs(self.bgp_peer_dict)

	def _get_bgp_peer_informations(self):
		self._get_peer_group_names()
		self._get_peer_group_attr_dict()
		self._get_template_peer_sessions()

	def _get_peer_group_names(self):
		for vrf, vrf_dict in self.vrfs.items():
			vrf_peer_grps = set()
			remove_eligibles = set()
			if not vrf_dict.get('lines'): continue
			for line in vrf_dict['lines']:
				if not line.startswith("neighbor"): continue
				spl = line.split()
				vrf_peer_grps.add(spl[1])
				if len(spl) > 3 and spl[2] == 'peer-group' and spl[3] in vrf_peer_grps:
					remove_eligibles.add(spl[1])
			vrf_dict['vrf_peer_grps'] = vrf_peer_grps - remove_eligibles

	def _get_peer_group_attr_dict(self):
		vrf_pg_dict = {}
		for vrf, vrf_dict in self.vrfs.items():
			vrf_pg_dict[vrf] = {}			
			if not vrf_dict.get('vrf_peer_grps'): continue
			for peer_grp in vrf_dict['vrf_peer_grps']:
				other = None
				if not vrf_pg_dict[vrf].get('peers'):
					vrf_pg_dict[vrf]['peers'] = {}
				vrf_pg_dict[vrf]['peers'][peer_grp] = {}
				pg_dict = vrf_pg_dict[vrf]['peers'][peer_grp]
				for line in vrf_dict['lines']:
					if not line.startswith("neighbor"): continue
					spl = line.split()
					valid_line = spl[1] == peer_grp or other in spl
					if not valid_line:
						if peer_grp in spl and spl[-1] == peer_grp:
							other = spl[1]
							valid_line = True
						else:
							other = None
							valid_line = False
					if not valid_line: continue
					for f in self.peer_attr_functions:
						f(peer_grp, pg_dict, line, spl)					

		self.bgp_peer_dict = vrf_pg_dict

	def _get_template_peer_sessions(self):
		stmp = {}
		for vrf, vrf_dict in self.vrfs.items():
			vrf_ps_dict = add_blankdict_key(stmp, vrf)
			start = False
			if not vrf_dict.get('lines'): continue
			for line in vrf_dict['lines']:
				if not start and line.startswith("template "):
					spl = line.strip().split()
					stmp_type, stmp_name, stmp_lines = spl[1], spl[2], []
					start = True
					continue
				if start and line.startswith("exit"):
					start = False
					x_dict = add_blankdict_key(vrf_ps_dict, stmp_type)
					x_dict[stmp_name] = stmp_lines
				if not start: continue
				stmp_lines.append(line)
		self.stmp_dict = stmp

	def _get_template_peer_sessions_attr_dict(self):
		ps_dict = {}
		for vrf, stmp_dict in self.stmp_dict.items():
			vrf_dict = add_blankdict_key(ps_dict, vrf)
			if not stmp_dict: continue
			x_pss_dict = add_blankdict_key(vrf_dict, 'template')
			for stmp_type, stmp_types_dict in stmp_dict.items():
				stmp_type_dict = add_blankdict_key(x_pss_dict, stmp_type)
				for stmp_name, stmplines in stmp_types_dict.items():
					vrf_ps_dict = add_blankdict_key(stmp_type_dict, stmp_name)
					for line in stmplines:
						spl = line.strip().split()
						if len(spl) == 2:
							vrf_ps_dict[spl[0]] = spl[1]
						elif len(spl) < 2:
							vrf_ps_dict[spl[0]] = True
						elif len(spl) > 2:
							x_dict = vrf_ps_dict
							for i in range(len(spl)):
								x_dict = add_blankdict_key(x_dict, spl[i])
		self.stmp_attr_dict = ps_dict


	# ---------------------------------------------------------------------- #

	def _iterate_vrfs(self):
		for vrf, vrf_dict in self.vrfs.items():
			if not vrf_dict.get('lines'): continue
			for line in vrf_dict['lines']:
				line = line.strip()
				spl = line.split()
				for f in self.attr_functions:
					f(self.bgp_peer_dict[vrf], line, spl)
			## Add session template attributes dict ## 
			if vrf in self.stmp_attr_dict:
				merge_dict( self.bgp_peer_dict[vrf], self.stmp_attr_dict[vrf] ) 

	# ---------------------------------------------------------------------- #


# ====================================================================================================
#  RIP Config extractor function
# ====================================================================================================

def get_bgp_running(command_output):
	"""parse output of : show running-config

	Args:
		command_output (list): command output

	Returns:
		dict: protocols bgp level parsed output dictionary
	"""    	
	BC = BGPConf(command_output)
	return get_protocol_instance_dict(protocol='bgp', instances_dic=BC.bgp_peer_dict)

# ====================================================================================================













