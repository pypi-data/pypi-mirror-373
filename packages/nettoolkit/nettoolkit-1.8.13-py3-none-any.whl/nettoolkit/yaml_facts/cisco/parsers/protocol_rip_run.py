"""cisco running-config parser for rip section output """

# ------------------------------------------------------------------------------
from .common import *
from .protocols import ProtocolsConfig, get_protocol_instance_dict
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
#  RIP ATTR FUNCS
# ------------------------------------------------------------------------------

def _get_rip_version(attr_dict, line, spl):
	if spl[0] == 'version':
		available_versions = spl[1:]
		append_attribute(attr_dict, 'version', available_versions)

def _get_auto_summary(attr_dict, line, spl):
	if line.strip() == 'no auto summary':
		append_attribute(attr_dict, 'auto-summary', False)

def _get_source_validation(attr_dict, line, spl):
	if 'validate-update-source' in spl:
		append_attribute(attr_dict, 'validate-update-source', spl[0] != 'no')

def _get_networks(attr_dict, line, spl):
	if spl[0] == 'network':
		if len(spl)>2:
			network = str(addressing(spl[1], spl[2]))
		else:
			network = str(classful_subnet(spl[1]))
		append_attribute(attr_dict, 'networks', network)

def _get_neighbors(attr_dict, line, spl):
	if spl[0] == 'neighbor':
		append_attribute(attr_dict, 'neighbor', spl[1])

def _get_redistributions(attr_dict, line, spl):
	if spl[0] == 'redistribute':
		append_attribute(attr_dict, 'redistribute', " ".join(spl[1:]))

def _get_default_metric(attr_dict, line, spl):
	if spl[0] == 'default-metric':
		append_attribute(attr_dict, 'default-metric', spl[1])

def _get_offset_list(attr_dict, line, spl):
	if spl[0] == 'offset-list':
		offset_list = spl[1]
		direction = spl[2]
		offset_number = spl[3]
		if not attr_dict.get('offset-list'):
			attr_dict['offset-list']= {}
		offset_dict = attr_dict['offset-list']
		if not offset_dict.get(offset_list):
			offset_dict[offset_list] = {}
		offset_list_dict = offset_dict[offset_list]
		append_attribute(offset_list_dict, 'direction', direction)
		append_attribute(offset_list_dict, 'offset_number', offset_number)
		if len(spl)>3: 
			offset_interface = spl[4]
			append_attribute(offset_list_dict, 'offset_interface', offset_interface)

# ====================================================================================================
#  RIP Config extractor Class
# ====================================================================================================

@dataclass
class RIPConf(ProtocolsConfig):

	## RIP Supported AF types
	supported_af_types = ('ipv4', 'ipv6')

	attr_functions = [
		_get_rip_version,
		_get_auto_summary,
		_get_source_validation,
		_get_networks,
		_get_neighbors,
		_get_redistributions,
		_get_default_metric,
		_get_offset_list,
	]

	def __post_init__(self):
		self.rip_vrf_dict = {}
		self.protocol_config_initialize(protocol='rip')
		self._iterate_vrfs()
		self.remove_empty_vrfs(self.rip_vrf_dict)

	def _iterate_vrfs(self):
		for vrf, vrf_dict in self.vrfs.items():
			if not vrf_dict.get('lines'): continue
			self.rip_vrf_dict[vrf] = self._get_attributes(vrf_dict['lines'])

# ====================================================================================================
#  RIP Config extractor function
# ====================================================================================================

def get_rip_running(command_output):
	"""parse output of : show running-config

	Args:
		command_output (list): command output

	Returns:
		dict: protocols rip level parsed output dictionary
	"""    	
	RC = RIPConf(command_output)
	return get_protocol_instance_dict(protocol='rip', instances_dic=RC.rip_vrf_dict)

# ====================================================================================================













