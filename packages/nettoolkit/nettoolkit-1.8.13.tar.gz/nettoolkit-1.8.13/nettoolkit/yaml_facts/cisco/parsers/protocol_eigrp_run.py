"""cisco running-config parser for rip section output """

# ------------------------------------------------------------------------------
from .common import *
from .protocols import ProtocolsConfig, get_protocol_instance_dict
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
#  RIP ATTR FUNCS
# ------------------------------------------------------------------------------

def _get_eigrp_asn(attr_dict, l, spl):
	if spl[0] == 'address-family' and 'autonomous-system' in spl:
		instancedict = add_blankdict_key(attr_dict, 'instance')
		update_key_value(instancedict, 'process-id', next_index_item(spl, 'autonomous-system'))
	elif l.startswith("router eigrp") and spl[2].isnumeric():
		instancedict = add_blankdict_key(attr_dict, 'instance')
		update_key_value(instancedict, 'process-id', spl[2])

def _get_eigrp_routerid(attr_dict, l, spl):
	if not l.startswith('eigrp router-id ') : return
	update_key_value(attr_dict, 'router-id', spl[-1])

def _get_eigrp_neighbors(attr_dict, l, spl):
	if spl[0] != "neighbor": return
	dic = add_blankdict_key(attr_dict, 'neighbors')
	nbr_attrs = ('loopback', 'remote')
	nbr = spl[1]
	nbr_dic = add_blankdict_key(dic, nbr)
	for attr in nbr_attrs:
		if not attr in spl: continue
		update_key_value(nbr_dic, attr, next_index_item(spl, attr))

def _get_eigrp_networks(attr_dict, l, spl):
	if spl[0] != "network": return
	if len(spl) == 2:
		network = classful_subnet(spl[1])
	else:
		network = addressing(spl[1], spl[2])
	append_attribute(attr_dict, 'networks', str(network))

def _get_eigrp_summary_address(attr_dict, l, spl):
	if spl[0] != 'summary-address': return
	dic = add_blankdict_key(attr_dict, 'summaries')
	mask = None if "/" in spl[1] else spl[2]
	diff = 1 if "/" in spl[1] else 0
	network = addressing(spl[1], mask)
	dic = add_blankdict_key(dic, str(network))
	if len(spl) > 3-diff:
		try:
			append_attribute(dic, 'AD', spl[3-diff])
		except: pass
		if 'leak-map' in spl:
			update_key_value(dic, 'leak-map', next_index_item(spl, 'leak-map'))

def _get_eigrp_summary_metric(attr_dict, l, spl):
	if 'summary-metric' not in spl: return
	dic = add_blankdict_key(attr_dict, 'summaries')
	sm_idx = spl.index("summary-metric")
	mask = None if "/" in spl[sm_idx+1] else spl[sm_idx+2]
	diff = 1 if "/" in spl[sm_idx+1] else 0
	network = addressing(spl[sm_idx+1], mask)
	dic = add_blankdict_key(dic, str(network))
	dic = add_blankdict_key(dic, 'metric')
	for i in range(1, 6):
		append_attribute(dic, f"k{i}", spl[sm_idx+i+2-diff])

def _get_eigrp_authentication(attr_dict, l, spl):
	if 'authentication' not in spl: return
	dic = add_blankdict_key(attr_dict, 'authentication')
	if 'mode' in spl:
		update_key_value(dic, 'mode', next_index_item(spl, 'mode'))
	if 'key-chain' in spl:
		update_key_value(dic, 'key-chain', spl[ spl.index('key-chain') + 2 ])


def _get_eigrp_distance(attr_dict, l, spl):
	if 'distance' not in spl or 'eigrp' not in spl: return
	distindex = spl.index('distance')
	dic = add_blankdict_key(attr_dict, 'distance')
	append_attribute(dic, 'internal', spl[2+distindex])
	if len(spl) > 3+distindex:
		append_attribute(dic, 'external', spl[3+distindex])

def _get_eigrp_default_metrics(attr_dict, l, spl):
	if 'default-metric' not in spl: return
	metric_idx = {1: 'bandwidth', 2: 'load', 3:'delay', 4:'reliability', 5:'mtu'}
	dic = add_blankdict_key(attr_dict, 'default-metric')
	for i, s in metric_idx.items():
		append_attribute(dic, s, spl[i])

def _get_eigrp_metric_weights(attr_dict, l, spl):
	diff = None
	if l.startswith("metric weights"):
		diff = 0
	elif len(spl)>2 and 'metric' == spl[2] and 'weights' == spl[3]: 
		diff = 2
	if diff is None: return
	dic = add_blankdict_key(attr_dict, 'metric')
	dic = add_blankdict_key(dic, 'weights')
	append_attribute(dic, 'TOS', spl[2+diff])
	for i in range(1, 6):
		append_attribute(dic, f"k{i}", spl[i+2+diff])

def _get_eigrp_metric_rib_scale(attr_dict, l, spl):
	diff = None
	if l.startswith("metric rib-scale"):
		diff = 0
	elif len(spl)>2 and 'metric' == spl[2] and 'rib-scale' == spl[3]: 
		diff = 2
	if diff is None: return
	dic = add_blankdict_key(attr_dict, 'metric')
	append_attribute(dic, "rib-scale", spl[2+diff])

def _get_eigrp_dampening(attr_dict, l, spl):
	dampenings = {'dampening-change', 'dampening-interval'}
	for damp in dampenings:
		if damp not in spl: continue
		dic = add_blankdict_key(attr_dict, 'dampening')
		item = damp.split("-")[-1]
		update_key_value(dic, item, next_index_item(spl, damp))

def _get_eigrp_redistribution(attr_dict, l, spl):
	if 'redistribute' not in spl: return
	dic = add_blankdict_key(attr_dict, 'redistribute')
	dic = add_blankdict_key(dic, next_index_item(spl, 'redistribute') )    ## route-type
	if 'metric' in spl:
		wordidx = spl.index('metric')
		metric_idx = {1: 'bandwidth', 2: 'load', 3:'delay', 4:'reliability', 5:'mtu'}
		metricdic = add_blankdict_key(dic, 'metric')
		for i, s in metric_idx.items():
			append_attribute(metricdic, s, spl[wordidx+i])

def _get_eigrp_others(attr_dict, l, spl):
	others = ("traffic-share", "maximum-paths", "variance",
		"hello-interval", "hold-time", "bandwidth-percent",
	)
	for item in others:
		if item not in spl: continue
		append_attribute(attr_dict, item, next_index_item(spl, item))

def _get_eigrp_passive_intf(attr_dict, l, spl):
	if "passive-interface" not in spl: return
	pi_idx = spl.index("passive-interface")
	if len(spl) > 1 and "no" == spl[pi_idx-1] and pi_idx == 1:
		if "passive-interface" == spl[-1]: 
			append_attribute(attr_dict, "passive-interface", False)
		else:
			append_attribute(attr_dict, "no passive-interface", next_index_item(spl, "passive-interface"))
	elif "passive-interface" == spl[-1]:
		append_attribute(attr_dict, "passive-interface", True)
	else:
		append_attribute(attr_dict, "passive-interface", next_index_item(spl, "passive-interface"))


# ====================================================================================================
#  RIP Config extractor Class
# ====================================================================================================

@dataclass
class EIGRPConf(ProtocolsConfig):

	## RIP Supported AF types
	supported_af_types = ('ipv4', 'ipv6')

	attr_functions = [
		_get_eigrp_routerid,
		_get_eigrp_asn,  
		_get_eigrp_neighbors,
		_get_eigrp_networks,
		_get_eigrp_summary_address,
		_get_eigrp_summary_metric,
		_get_eigrp_authentication,
		_get_eigrp_distance,
		_get_eigrp_default_metrics,
		_get_eigrp_metric_weights,
		_get_eigrp_metric_rib_scale,
		_get_eigrp_dampening,
		_get_eigrp_redistribution,
		_get_eigrp_others,
		_get_eigrp_passive_intf,

	]

	group_by = { 'af-interface', 'topology',}

	def __post_init__(self):
		self.eigrp_vrf_dict = {}
		self.eigrp_lines_dict = self.get_eigrp_lines_dict()
		self.eigrp_af_lines_dict = self.get_eigrp_af_lines_dict(self.eigrp_lines_dict, "address-family ", "exit-address-family")
		self.eigrp_af_lines_dict = self.get_eigrp_sub_af_lines_dict(self.eigrp_af_lines_dict, "topology ", "exit-af-topology")
		self.eigrp_af_lines_dict = self.get_eigrp_sub_af_lines_dict(self.eigrp_af_lines_dict, "af-interface ", "exit-af-interface")
		self._iterate_vrfs()
		self.shirnk_None_vrf_dict()

	def shirnk_None_vrf_dict(self):
		for process_id in list(self.eigrp_vrf_dict.keys()):
			vrf_dict = self.eigrp_vrf_dict[process_id]
			if None in vrf_dict:
				merge_dict(vrf_dict, vrf_dict[None])
				del(vrf_dict[None])


	def _iterate_vrfs(self):
		for process_id, vrf_dict in self.eigrp_af_lines_dict.items():
			if not vrf_dict: continue
			process_dic = add_blankdict_key(self.eigrp_vrf_dict, process_id)
			for key, lines in vrf_dict.items():
				if not lines: continue
				if key:
					splKey = key.strip().split()
					if 'vrf' in splKey:
						key = next_index_item(splKey, 'vrf') 
				vrf_dic = add_blankdict_key(process_dic, key)
				vrf_dic.update( self._get_attributes(lines))
				instancedict = add_blankdict_key(vrf_dic, 'instance')
				instancedict['vrf'] = key
				if not instancedict.get('process-id'):
					instancedict['process-id'] = process_id

	def _get_attributes(self, lines):
		attr_dict = {}
		for line in lines:
			line = line.strip()
			spl  = line.split()
			if spl[0] in self.group_by:
				grp_dict = add_blankdict_key(attr_dict, spl[1]) 
				for f in self.attr_functions:
					f(grp_dict, line, spl)
			else:
				for f in self.attr_functions:
					f(attr_dict, line, spl)
		return attr_dict		

	def get_eigrp_lines_dict(self):
		dic, start = {}, False
		for line in self.run_list:
			if not line.strip() : continue
			if line.startswith(f"router eigrp "):
				spl = line.split()
				process_id, lst = spl[2], []
				start = True
			if start and line[0] == "!": 
				dic[process_id] = lst
				start = False
				continue
			if not start: continue
			if line.strip().startswith("!"): continue
			lst.append(line.strip())
		return dic

	def get_eigrp_af_lines_dict(self, source_dict, starter, stopper):
		dic = {}
		additives = ('topology ', 'af-interface ')
		###- lines with vrf
		for key, lines in source_dict.items():
			x_dic = add_blankdict_key(dic, key)
			start = False
			if not lines: continue
			for line in lines:
				if not line: continue
				if not line.strip(): continue 
				if line.startswith(starter):
					spl = line.split()
					key, lst = line, []
					start = True
				if start and line.startswith(stopper): 
					x_dic[key] = lst
					start = False
					continue
				if not start: continue
				if starter in additives:
					line = key.strip() + " " + line
				lst.append(line)
		if starter in additives:
			return dic
		###- lines without vrf
		for key, lines in source_dict.items():
			x_dic = add_blankdict_key(dic, key)
			start, NullKey, lst = False, None, []
			for line in lines:
				if line.startswith(starter):
					start = True
					continue
				if start and line.startswith(stopper): 
					start = False
					continue
				if start: continue
				lst.append(line)
			x_dic[NullKey] = lst
		return dic

	def get_eigrp_sub_af_lines_dict(self, source_dict, starter, stopper):
		dic = {}
		for asn, asn_dict in source_dict.items():
			y_dic = add_blankdict_key(dic, asn)
			for key, lines in asn_dict.items():
				lst = add_blanklist_key(y_dic, key)
				start = False
				if not lines: continue
				for line in lines:
					if not line: continue
					if not line.strip(): continue 
					if line.startswith(starter):
						start = True
					if start and line.startswith(stopper): 
						start = False
						continue
					if start: 
						line = key.strip() + " " + line
					lst.append(line)
		return dic





# ====================================================================================================
#  RIP Config extractor function
# ====================================================================================================

def get_eigrp_running(command_output):
	"""parse output of : show running-config

	Args:
		command_output (list): command output

	Returns:
		dict: protocols eigrp level parsed output dictionary
	"""    	
	EC = EIGRPConf(command_output)
	return get_protocol_instance_dict(protocol='eigrp', instances_dic=EC.eigrp_vrf_dict)

# ====================================================================================================













