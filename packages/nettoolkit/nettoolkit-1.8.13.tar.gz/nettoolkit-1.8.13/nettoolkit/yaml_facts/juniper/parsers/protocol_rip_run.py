"""juniper rip protocol routing instances parsing from set config  """

# ------------------------------------------------------------------------------
from .common import *
from .run import ProtocolObject
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  rip parser functions
# ------------------------------------------------------------------------------

def get_rip_instance_attributes(vrf_dict, spl):
	if 'import' not in spl and 'export' not in spl: return
	nxt_value_attrs = ('export', 'import',)
	get_instance_parameter_for_items(vrf_dict, '', spl, nxt_value_attrs)

def get_rip_nbr_attributes(vrf_dict, spl):
	if 'neighbor' not in spl: return
	nbr_dict = add_blankdict_key(vrf_dict, 'neighbors')
	nbr_dict = add_blankdict_key(nbr_dict, spl[spl.index ('neighbor') + 1])
	nxt_value_attrs = ('update-interval', 'interface-type', 'peer', 'receive', 'max-retrans-time', 'protocols', 'metric-in')
	get_instance_parameter_for_items(nbr_dict, '', spl, nxt_value_attrs)
	get_authentication_attributes(nbr_dict, spl)

def get_authentication_attributes(nbr_dict, spl):
	if 'authentication' not in spl: return
	auth_dict = add_blankdict_key(nbr_dict, 'authentication')
	nxt_value_attrs = ('key-chain', 'algorithm', 'authentication-type', )
	get_instance_parameter_for_items(auth_dict, '', spl, nxt_value_attrs)

def get_rip_bfdld_attributes(vrf_dict, spl):
	if 'bfd-liveness-detection' not in spl: return
	bfd_dict = add_blankdict_key(vrf_dict, 'bfd-liveness-detection')
	nxt_value_attrs = ('minimum-interval', )
	get_instance_parameter_for_items(bfd_dict, '', spl, nxt_value_attrs)
	get_authentication_attributes(bfd_dict, spl)

def get_rip_auth_attributes(vrf_dict, spl):
	if not spl[0].startswith("authentication"): return
	auth_dict = add_blankdict_key(vrf_dict, 'authentication')
	if 'authentication-selective-md5' in spl:
		md5_dict = add_blankdict_key(auth_dict, 'md5')
		if 'key' in spl:
			md5_dict = add_blankdict_key(md5_dict, spl[spl.index('authentication-selective-md5')+1])
		pw = get_pw(spl, key="key")
		append_attribute(md5_dict, attribute='key', value=pw)
		append_attribute(md5_dict, attribute='start-time', value=spl[spl.index('start-time')+1])



# ------------------------------------------------------------------------------
#  rip extractor class
# ------------------------------------------------------------------------------

@dataclass
class RIP(ProtocolObject):
	cmd_op: list[str,] = field(default_factory=[])
	protocol: str

	rip_attr_functions = [
		get_rip_instance_attributes,
		get_rip_auth_attributes,
	]
	rip_grp_attr_functions = [
		get_rip_instance_attributes,
		get_rip_nbr_attributes,
		get_rip_bfdld_attributes,
	]

	def __post_init__(self):
		super().initialize(self.protocol)

	def __call__(self):
		self.iterate_logical_systems(hierarchy='protocols')

	def start(self):
		self.get_protocol_rip_instance_lines()
		rip_dict = self.iterate_for_rip()
		rip_dict = self.remove_parent_vrf_if_standalone(rip_dict)
		self.protocol_rip_dict = {self.protocol: rip_dict}
		return self.protocol_rip_dict
			

	def get_protocol_rip_instance_lines(self):
		self.protocol_lines = {}
		for vrf in self.jPtObj.VRFs.keys():
			VRF = self.jPtObj.VRFs[vrf]
			if not VRF.protocol_vrf_lines: continue
			VRF.rip_group_lines = self.get_rip_group_lines(VRF.protocol_vrf_lines)
			VRF.rip_other_lines = self.get_rip_other_lines(VRF.protocol_vrf_lines)
			VRF.rip_group_dict = self.get_rip_group_dict(VRF.rip_group_lines)

			# from pprint import pprint
			# pprint(VRF.rip_group_lines)

			self.protocol_lines[vrf] = VRF


	def get_rip_group_lines(self, lines):
		rip_group_lines = [ line for line in lines if line.find(f" protocols {self.protocol} group ") > 0 ]
		return rip_group_lines

	def get_rip_other_lines(self, lines):
		rip_other_lines = [ line for line in lines if line.find(f" protocols {self.protocol} group ") == -1 ]
		return rip_other_lines

	def get_rip_group_dict(self, group_lines):
		dic = {}
		for line in group_lines:
			# print(line)
			spl = line.strip().split(f" protocols {self.protocol} group ")[-1].split()
			grp_dict = add_blanklist_key(dic, spl[0])
			grp_dict.append(spl)
		return dic

	def iterate_for_rip(self):
		protocol_rip_dict = {}
		for vrf, VRF in self.protocol_lines.items():
			if VRF.rip_group_dict:
				vrf_dict = add_blankdict_key(protocol_rip_dict, vrf)
				for grp, lines in VRF.rip_group_dict.items():
					
					grp_dict = add_blankdict_key(vrf_dict, grp)	
					self.iterarte_group_lines(grp_dict, lines)
			if VRF.rip_other_lines:
				vrf_dict = add_blankdict_key(protocol_rip_dict, vrf)
				self.iterarte_other_lines(vrf_dict, VRF.rip_other_lines)
		return protocol_rip_dict


	def iterarte_group_lines(self, vrf_dict, lines):
		for spl in lines:
			# print(spl)
			for f in self.rip_grp_attr_functions:
				f(vrf_dict, spl)

	def iterarte_other_lines(self, vrf_dict, lines):
		for line in lines:
			line = line.strip().split(f" protocols {self.protocol} ")[-1]
			spl = line.split()
			for f in self.rip_attr_functions:
				f(vrf_dict, spl)


# ------------------------------------------------------------------------------
#  rip parser calling function
# ------------------------------------------------------------------------------
def get_rip_running(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: protocols rip level parsed output dictionary
	"""    	
	R = RIP(cmd_op, 'rip')
	R()
	return R.logical_systems_dict

# ------------------------------------------------------------------------------

