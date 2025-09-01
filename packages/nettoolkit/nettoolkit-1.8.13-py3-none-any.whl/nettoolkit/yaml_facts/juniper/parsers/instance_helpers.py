"""juniper bgp protocol routing instances parsing from set config  """

# ------------------------------------------------------------------------------
from .common import *
from .run import Running
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  helper parser functions
# ------------------------------------------------------------------------------
def get_helper(op_dict, spl):
	try:
		ipadd = addressing(spl[-1])
	except:
		return
	if ipadd.version == 4:
		section = 'dhcp_helpers_v4'
	elif ipadd.version == 6:
		section = 'dhcp_helpers_v6'
	helper_list = add_blanklist_key(op_dict, section)
	helper_list.append(spl[-1])

# ------------------------------------------------------------------------------
#  helper extractor class
# ------------------------------------------------------------------------------

@dataclass
class HelperAddresses(Running):
	cmd_op: list[str, ] = field(default_factory=[])

	attr_functions = [
		get_helper,
	]

	def __post_init__(self):
		super().__post_init__()
		self.helper_dict = {}
		self.get_system_helpers_lines_dict()
		self.iterate_to_get_helpers()

	def get_system_helpers_lines_dict(self):
		self.system_helpers_lines_dict = {}
		for line in self.set_cmd_op:
			line = line.strip()
			if not line: continue
			spl = line.split()
			if "dhcp-relay" not in spl and "server-group" not in spl: continue 
			vrf = spl[2] if spl[1] == 'routing-instances' else None
			vrf_lines = add_blanklist_key(self.system_helpers_lines_dict, vrf)
			vrf_lines.append(spl)				

	def iterate_to_get_helpers(self):
		for vrf, vrf_lines in self.system_helpers_lines_dict.items():
			vrf_dict = add_blankdict_key(self.helper_dict, vrf)
			for spl in vrf_lines:
				for f in self.attr_functions:
					f(vrf_dict, spl)
			if not vrf_dict:
				del(self.helper_dict[vrf])


# ------------------------------------------------------------------------------
#  helper parser calling function
# ------------------------------------------------------------------------------
def get_helper_running(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: vrf level parsed output dictionary for dhcp helper recognition 
	"""    	
	HA = HelperAddresses(cmd_op)
	return {'vrf': HA.helper_dict}
# ------------------------------------------------------------------------------

