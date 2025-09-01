"""cisco running-config parser for isis section output """

# ------------------------------------------------------------------------------
from .common import *
from .protocols import ProtocolsConfig, get_protocol_instance_dict
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
#  ISIS ATTR FUNCS
# ------------------------------------------------------------------------------

def _get_isis_default_info_originate(attr_dict, l, spl):
	if not l.startswith("default-information originate"): return
	if "route-map" in spl:
		dic = add_blankdict_key(attr_dict, 'default-information')
		dic = add_blankdict_key(dic, 'originate')
		append_attribute(dic, "route-map", spl[-1])
	else:
		append_attribute(attr_dict, 'default-information', spl[-1])


def _get_isis_psasive_intf(attr_dict, l, spl):
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


def _get_isis_spf_interval(attr_dict, l, spl):
	if 'spf-interval' != spl[0]: return
	dic = add_blankdict_key(attr_dict, 'spf-interval')
	d = {1: 'level', 2: 'seconds', 3: 'initial-wait', 4: 'secondary-wait'}
	diff = 1 if spl[1].isnumeric() else 0
	for idx in range(1, len(spl)):
		append_attribute(dic, d[idx+diff], spl[idx])

def _get_isis_prc_interval(attr_dict, l, spl):
	interval_candidates = ("lsp-gen-interval", 'prc-interval')
	if spl[0] not in interval_candidates: return
	dic = add_blankdict_key(attr_dict, spl[0])
	d = {1: 'seconds', 2: 'initial-wait' ,3: 'secondary-wait'}
	for idx in range(1, len(spl)):
		append_attribute(dic, d[idx], spl[idx])


def _get_isis_metric(attr_dict, l, spl):
	if 'metric' != spl[0]: return
	if len(spl) > 2:
		dic = add_blankdict_key(attr_dict, 'metric')
		append_attribute(dic, spl[2], spl[1])
	elif len(spl) == 2:
		append_attribute(attr_dict, 'metric', spl[1])

def _get_isis_metric_style(attr_dict, l, spl):
	if 'metric-style' != spl[0]: return
	dic = add_blankdict_key(attr_dict, 'metric')
	dic = add_blankdict_key(dic, 'style')
	for idx in range(1, len(spl)):
		dic = add_blankdict_key(dic, spl[idx])

def _get_isis_redistribution(attr_dict, l, spl):
	if 'redistribute' != spl[0]: return
	dic = add_blankdict_key(attr_dict, 'redistribute')
	if spl[1] == 'maximum-prefix':
		dic = add_blankdict_key(dic, 'maximum-prefix' )
		append_attribute(dic, 'maximum', spl[2])
		if spl[3].isnumeric: append_attribute(dic, 'percentage', spl[3])
		if spl[-1] in ('withdraw', 'warning-only'):
			append_attribute(dic, spl[-1], True)
		return
	# --- #
	attrs = ('metric', 'metric-type', 'match', 'tag', 'route-map', 'distribute-list')
	protocol = spl[1]
	dic = add_blankdict_key(dic, protocol)
	attr_idx = {attr:spl.index(attr) for attr in attrs if attr in spl}
	min_idx = min(attr_idx.values())
	for idx in range(2, min_idx):
		dic = add_blankdict_key(dic, spl[idx])
	for item, idx in attr_idx.items():
		append_attribute(dic, item, spl[idx+1])

def _get_isis_summary_address(attr_dict, l, spl):
	summary_candidates = ("summary-address", "summary-prefix")
	if spl[0] not in summary_candidates: return
	dic = add_blankdict_key(attr_dict, 'summaries')
	mask = None if "/" in spl[1] else spl[2]
	diff = 1 if "/" in spl[1] else 0
	network = addressing(spl[1], mask).NetworkIP()
	level = spl[3-diff]
	dic = add_blankdict_key(dic, str(network))
	append_attribute(dic, 'level', level)
	attrs = ('tag', 'metric')
	for item in attrs:
		if item not in spl: continue
		append_attribute(dic, item, next_index_item(spl, item))

def _get_isis_auth(attr_dict, l, spl):
	if 'authentication' not in spl or 'password' not in spl: return
	password_candidates = ('area-password', 'domain-password')
	if spl[0] in password_candidates:
		dic = add_blankdict_key(attr_dict, "password")
		update_key_value(dic, spl[0], next_index_item(spl, "password"))
		if len(spl) > 2:
			for i in range(2, len(spl)):
				dic = update_key_value(dic, spl[i], spl[i+1])
	elif 'authentication' in spl:
		dic = add_blankdict_key(attr_dict, 'authentication')
		if 'mode' in spl:
			update_key_value(dic, 'mode', next_index_item(spl, 'mode'))
		if 'key-chain' in spl:
			update_key_value(dic, 'key-chain', spl[ spl.index('key-chain') + 2 ])




def _get_isis_next_item(attr_dict, l, spl):
	attrs = (
		"net", "is-type", "vrf", "multi-topology", "maximum-paths", "protocol", "segment-routing",
		"max-lsp-lifetime", "lsp-refresh-interval", "fast-flood",
	)
	for item in attrs:
		if item != spl[0]: continue
		append_attribute(attr_dict, item, next_index_item(spl, item))



# ====================================================================================================
#  ISIS Config extractor Class
# ====================================================================================================

@dataclass
class ISISConf(ProtocolsConfig):

	## ISIS Supported AF types
	supported_af_types = ('ipv4', 'ipv6')

	attr_functions = [
		_get_isis_spf_interval,
		_get_isis_prc_interval,
		_get_isis_metric,
		_get_isis_metric_style,
		_get_isis_redistribution,
		_get_isis_summary_address,
		_get_isis_auth,
		_get_isis_next_item,
		_get_isis_psasive_intf,
		_get_isis_default_info_originate,

	]

	def __post_init__(self):
		self.isis_vrf_dict = {}
		isis_lines_dict = self.get_isis_lines_dict()
		self.isis_af_lines_dict = self.get_isis_af_lines_dict(isis_lines_dict, 'address-family ', "exit-address-family")
		self._iterate_vrfs()
		self.shirnk_None_vrf_dict()

	def shirnk_None_vrf_dict(self):
		for area_id in list(self.isis_vrf_dict.keys()):
			vrf_dict = self.isis_vrf_dict[area_id]
			if None in vrf_dict:
				merge_dict(vrf_dict, vrf_dict[None])
				del(vrf_dict[None])


	def get_isis_lines_dict(self):
		dic, start = {}, False
		for line in self.run_list:
			if not line.strip() : continue
			if line.startswith(f"router isis"):
				spl = line.split()
				area_id = spl[2] if len(spl)>2 else 0
				lst = []
				start = True
			if start and line[0] == "!": 
				dic[area_id] = lst
				start = False
				continue
			if not start: continue
			if line.strip().startswith("!"): continue
			lst.append(line.strip())
		return dic

	def get_isis_af_lines_dict(self, source_dict, starter, stopper):
		dic = {}
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
				lst.append(line)
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

	def _iterate_vrfs(self):
		for area_id, vrf_dict in self.isis_af_lines_dict.items():
			if not vrf_dict: continue
			process_dic = add_blankdict_key(self.isis_vrf_dict, area_id)
			for key, lines in vrf_dict.items():
				if not lines: continue
				vrf_dic = add_blankdict_key(process_dic, key)
				vrf_dic.update( self._get_attributes(lines) )


# ====================================================================================================
#  ISIS Config extractor function
# ====================================================================================================

def get_isis_running(command_output):
	"""parse output of : show running-config

	Args:
		command_output (list): command output

	Returns:
		dict: protocols isis and isis-instance level parsed output dictionary
	"""    	
	RC = ISISConf(command_output)
	return get_protocol_instance_dict(protocol='isis', instances_dic=RC.isis_vrf_dict)

# ====================================================================================================








