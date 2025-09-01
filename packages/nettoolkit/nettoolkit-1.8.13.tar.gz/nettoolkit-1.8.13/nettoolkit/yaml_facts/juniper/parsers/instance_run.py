"""juniper bgp protocol routing instances parsing from set config  """

# ------------------------------------------------------------------------------
from .common import *
from .run import ProtocolObject
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  instance parser functions
# ------------------------------------------------------------------------------
def get_vrf_rd(vrf_dict, spl):
	if spl[3] != 'route-distinguisher': return
	vrf_dict['rd'] = spl[-1].strip().split(":")[-1]

def get_vrf_rt(vrf_dict, spl):
	if spl[3] != 'vrf-target': return
	rd = ":".join(spl[-1].split(":")[-2:])
	append_attribute(vrf_dict, attribute=f"{spl[4]} target", value=rd)

def get_vrf_desc(vrf_dict, spl):
	if spl[3] != 'description': return
	desc = " ".join(spl[4:]).strip()
	if desc[0] == '"': desc = desc[1:]
	if desc[-1] == '"': desc = desc[:-1]
	vrf_dict['description'] = desc


# ------------------------------------------------------------------------------
#  instance extractor class
# ------------------------------------------------------------------------------
@dataclass
class Instances(ProtocolObject):
	cmd_op: list[str,] = field(default_factory=[])

	instance_attr_functions = [
		get_vrf_rd,
		get_vrf_rt,
		get_vrf_desc,
	]

	def __post_init__(self):
		super().initialize('bgp')

	def __call__(self):
		self.iterate_logical_systems(hierarchy='vrf')

	def start(self):
		self.protocol_instances = {}
		self.get_instance_lines()
		self.add_protocol_instance_info()
		return self.protocol_instances

	def get_instance_lines(self):
		self.instances_line_dict = {}
		for l in self.set_cmd_op:
			if not l.startswith(f"set routing-instances "): continue
			spl = l.strip().split()
			vrf_dict = add_blankdict_key(self.instances_line_dict, spl[2])
			VRF = self.jPtObj.VRFs[spl[2]]
			if l in VRF.bgp_peer_group_lines: continue
			if l in VRF.bgp_other_lines: continue

			vrf_spl = add_blankset_key(vrf_dict, 'spl')
			vrf_spl.add(tuple(spl))

	def add_protocol_instance_info(self):
		for vrf, vrf_dict in self.instances_line_dict.items():
			instance_dict = add_blankdict_key(self.protocol_instances, vrf)
			for spl in vrf_dict['spl']:
				self.iterate_instance_funcs(instance_dict, spl)

	def iterate_instance_funcs(self, instance_dict, spl):
		for f in self.instance_attr_functions:
			f(instance_dict, spl)

# ------------------------------------------------------------------------------
#  instance parser calling function
# ------------------------------------------------------------------------------
def get_instance_running(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: vrf level parsed output dictionary
	"""    	
	I = Instances(cmd_op)
	I()
	return I.logical_systems_dict

# ------------------------------------------------------------------------------

