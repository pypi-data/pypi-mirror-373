"""juniper  protocol routing instances parsing from set config  """

# ------------------------------------------------------------------------------
from .common import *
from .run import ProtocolObject
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#   parser functions
# ------------------------------------------------------------------------------

#### //// INSTANCE FUNCTIONS //// ####

def get_isis_options(instance_dict, spl):
	true_attr = {
		'backup-spf-options': ('node-link-degradation', 'per-prefix-calculation', 'remote-backup-calculation',
			'use-source-packet-routing', ),
		'export': ('export-isis-metro-a', 'export-isis-metro-b', 'l2_l1_leak', 'leakl2tol1', 'prefix-sid'),
	}
	next_attr = {
		'graceful-restart': ('restart-duration', )
	}
	get_nest_attributes(instance_dict, '', spl, true_attr, next_attr=False, unique=False)
	get_nest_attributes(instance_dict, '', spl, next_attr, next_attr=True, unique=False)

def get_isis_int_options(int_dict, spl):
	int_true_attr = {'node-link-protection', 'ldp-synchronization', 'node-link-protection', 'link-protection',
		'point-to-point', 'disable', 'passive', 'checksum', 
	}
	int_next_attr = { 'level', 'metric', 'cluster-id', 'family',  'hello-authentication-key-chain', 
		'ipv4-adjacency-segment', 'label', 'priority', 
	}
	int_nest_next_attr = {
		'authentication': ('algorithm', 'key-chain'), 
	}
	get_nest_attributes(int_dict, '', spl, int_true_attr, next_attr=False, unique=False)
	get_nest_attributes(int_dict, '', spl, int_next_attr, next_attr=True, unique=True)
	get_nest_attributes(int_dict, '', spl, int_nest_next_attr, next_attr=True, unique=False)

def get_isis_lvl_options(lvl_dict, spl):
	lvl_true_attr = { 'wide-metrics-only', 'disable', }
	lvl_next_attr = { 'authentication-key-chain', 'flood-reflector' }
	get_nest_attributes(lvl_dict, '', spl, lvl_true_attr, next_attr=False, unique=False)
	get_nest_attributes(lvl_dict, '', spl, lvl_next_attr, next_attr=True, unique=False)


# ------------------------------------------------------------------------------
#   extractor class
# ------------------------------------------------------------------------------

@dataclass
class ISIS(ProtocolObject):
	cmd_op: list[str,] = field(default_factory=[])
	protocol: str

	isis_attr_functions = [
		get_isis_options,
	]
	isis_intf_attr_functions = [
		get_isis_int_options,
	]
	isis_lvl_attr_functions = [
		get_isis_lvl_options,
	]
	isis_nested_attr_functions = {
		'interface': isis_intf_attr_functions, 
		'level': isis_lvl_attr_functions,
	}

	def __post_init__(self):
		super().initialize(self.protocol)

	def __call__(self):
		self.iterate_logical_systems(hierarchy='protocols')

	def start(self):
		self.protocol_isis_dict = {}
		self.get_protocol_isis_instance_lines()
		self.iterate_for_isis_instances()
		isis_dict = self.iterate_for_isis_instances()
		isis_dict = self.remove_parent_vrf_if_standalone(isis_dict)
		self.protocol_isis_dict = {self.protocol: isis_dict}
		return self.protocol_isis_dict

	def get_protocol_isis_instance_lines(self):
		self.protocol_lines = {}
		for vrf in self.jPtObj.VRFs.keys():
			VRF = self.jPtObj.VRFs[vrf]
			if not VRF.protocol_vrf_lines: continue
			VRF.instance_dict = self.get_isis_instances_dict(VRF.protocol_vrf_lines)

			self.protocol_lines[vrf] = VRF

	def get_isis_instances_dict(self, lines):
		instance_dict = {}
		for line in lines:
			spl = line.strip().split(" protocols isis")[-1].split()
			vrf = spl[1] if spl[0] == '-instance' else None
			vrf_list = add_blanklist_key(instance_dict, vrf)
			if vrf: spl = spl[2:]
			vrf_list.append(spl)
		return instance_dict

	def iterate_for_isis_instances(self):
		protocol_isis_dict = {}
		for vrf, VRF in self.protocol_lines.items():
			for instance, instance_lines in VRF.instance_dict.items():
				if not instance_lines: continue
				instance_dict = add_blankdict_key(protocol_isis_dict, instance)
				self.iterate_isis_lines(instance_dict, instance_lines)
		return protocol_isis_dict

	def iterate_isis_lines(self, instance_dict, instance_lines):
		segments = ( 'interface', 'level', )
		for spl in instance_lines:
			self.iterate_isis_attr_funcs(instance_dict, spl, segments)
			for segment in segments:
				self.iterate_isis_intf_attr_funcs(instance_dict, spl, segment)

	def iterate_isis_attr_funcs(self, instance_dict, spl, segments):
		if spl[0] in segments: return
		for f in self.isis_attr_functions:
			f(instance_dict, spl)

	def iterate_isis_intf_attr_funcs(self, instance_dict, spl, segment):
		if spl[0] != segment: return
		spl = spl[spl.index(segment)+1:]
		_segment_dict = add_blankdict_key(instance_dict, segment)		
		segment_dict = add_blankdict_key(_segment_dict, spl[0])		
		for f in self.isis_nested_attr_functions[segment]:
			f(segment_dict, spl)


# ------------------------------------------------------------------------------
#   parser calling function
# ------------------------------------------------------------------------------
def get_isis_running(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: protocols isis and isis-instance level parsed output dictionary
	"""    	
	parent_dict = get_isis_parent_running(cmd_op)
	instance_dict = get_isis_instance_running(cmd_op)
	merge_dict(parent_dict, instance_dict)
	return parent_dict


def get_isis_parent_running(cmd_op):
	I = ISIS(cmd_op, 'isis')
	I()
	return I.logical_systems_dict

def get_isis_instance_running(cmd_op):
	I = ISIS(cmd_op, 'isis-instance')
	I()
	return I.logical_systems_dict

# ------------------------------------------------------------------------------

