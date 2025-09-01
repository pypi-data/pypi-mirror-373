"""juniper ospf protocol routing instances parsing from set config  """

# ------------------------------------------------------------------------------
from .common import *
from .run import ProtocolObject
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  ospf parser functions
# ------------------------------------------------------------------------------

#### //// INSTANCE FUNCTIONS //// ####

def get_instance_attributes(vrf_dict, line, spl):
	nxt_value_attrs = ('export', 'import', 'rib-group', 'preference', 'external-preference', 'reference-bandwidth')
	get_instance_parameter_for_items(vrf_dict, line, spl, nxt_value_attrs)

def get_instance_attribute_spf_options(vrf_dict, line, spl):
	if 'spf-options' not in spl: return
	spf_dict = add_blankdict_key(vrf_dict, 'spf-options')
	nxt_value_attrs = ('delay', 'holddown')
	get_instance_parameter_for_items(spf_dict, line, spl, nxt_value_attrs)


#### //// AREA FUNCTIONS //// ####

def get_area_interface_attributes(vrf_dict, line, spl):
	if 'interface' not in spl: return
	_int_dict = add_blankdict_key(vrf_dict, 'interfaces')
	int_dict = add_blankdict_key(_int_dict, spl[spl.index('interface')+1])
	get_area_interface_next_item_attributes(int_dict, line, spl)
	get_area_interface_true_item_attributes(int_dict, line, spl)
	get_area_interface_auth_attributes(int_dict, line, spl)

def get_area_interface_next_item_attributes(int_dict, line, spl):
	nxt_value_attrs = ('interface-type', 'metric', 'neighbor', 'poll-interval', 'hello-interval','dead-interval',
		'retransmit-interval', 'transit-delay', 'priority')
	get_instance_parameter_for_items(int_dict, line, spl, nxt_value_attrs)

def get_area_interface_true_item_attributes(int_dict, line, spl):
	true_value_attrs = ('passive', 'disable', 'secondary', 'flood-reduction')
	update_true_instance_items(int_dict, line, spl, items=true_value_attrs)

def get_area_interface_auth_attributes(int_dict, line, spl):
	if 'authentication' not in spl: return
	if 'simple-password' in spl:
		pw = get_pw(spl, key="simple-password")
		append_attribute(int_dict, attribute='simple-password', value=pw)
	if 'md5' in spl:
		md5_dict = add_blankdict_key(int_dict, 'md5')
		if 'key' in spl:
			md5_dict = add_blankdict_key(md5_dict, spl[spl.index('md5')+1])
		pw = get_pw(spl, key="key")
		append_attribute(md5_dict, attribute='key', value=pw)
		append_attribute(md5_dict, attribute='start-time', value=spl[spl.index('start-time')+1])

def get_area_stub_attributes(vrf_dict, line, spl):
	if spl[2] not in ('stub', 'nssa'): return
	stub_dict = add_blankdict_key(vrf_dict, spl[2])
	get_area_stub_next_item_attributes(stub_dict, line, spl)
	get_area_stub_true_item_attributes(stub_dict, line, spl)
	get_area_stub_def_lsa_item_attributes(stub_dict, line, spl)


def get_area_stub_next_item_attributes(stub_dict, line, spl):
	nxt_value_attrs = ('default-metric', 'area-range')
	get_instance_parameter_for_items(stub_dict, line, spl, nxt_value_attrs)

def get_area_stub_true_item_attributes(stub_dict, line, spl):
	true_value_attrs = ('no-summaries',)
	update_true_instance_items(stub_dict, line, spl, items=true_value_attrs)

def get_area_stub_def_lsa_item_attributes(stub_dict, line, spl):
	if 'default-lsa' not in spl: return
	def_lsa_dict = add_blankdict_key(stub_dict, 'default-lsa')
	nxt_value_attrs = ('default-metric', 'metric-type')
	true_value_attrs = ('type-7',)
	get_instance_parameter_for_items(def_lsa_dict, line, spl, nxt_value_attrs)
	update_true_instance_items(def_lsa_dict, line, spl, true_value_attrs)


def get_area_range_attributes(vrf_dict, line, spl):
	if spl[2] != 'area-range': return
	nxt_value_attrs = ('area-range',)
	get_instance_parameter_for_items(vrf_dict, line, spl, nxt_value_attrs)

def get_area_virtuallink_attributes(vrf_dict, line, spl):
	if 'virtual-link' not in spl: return
	vl_dict = add_blankdict_key(vrf_dict, 'virtual-link')
	nxt_value_attrs = ('neighbor-id', 'transit-area', 'ipsec-sa')
	get_instance_parameter_for_items(vl_dict, line, spl, nxt_value_attrs)

def get_area_shamlink_attributes(vrf_dict, line, spl):
	if 'sham-link' not in spl and 'sham-link-remote' not in spl : return	
	shm_dict = add_blankdict_key(vrf_dict, 'sham-link')
	nxt_value_attrs = ('sham-link-remote', 'metric', 'local')
	get_instance_parameter_for_items(shm_dict, line, spl, nxt_value_attrs)




# ------------------------------------------------------------------------------
#  ospf extractor class
# ------------------------------------------------------------------------------

@dataclass
class OSPF(ProtocolObject):
	cmd_op: list[str,] = field(default_factory=[])
	protocol: str

	ospf_instance_attr_functions = [
		get_instance_attributes,
		get_instance_attribute_spf_options,
		get_area_shamlink_attributes,
	]
	ospf_area_attr_functions = [
		get_area_interface_attributes,
		get_area_stub_attributes,
		get_area_range_attributes,
		get_area_virtuallink_attributes,
		get_area_shamlink_attributes,
	]

	def __post_init__(self):
		super().initialize(self.protocol)

	def __call__(self):
		self.iterate_logical_systems(hierarchy='protocols')

	def start(self):
		self.get_protocol_ospf_instance_lines()
		_dict = self.iterate_for_ospf()
		_dict = self.remove_parent_vrf_if_standalone(_dict)
		self.protocol_ospf_dict = {self.protocol: _dict}
		return self.protocol_ospf_dict
			

	def get_protocol_ospf_instance_lines(self):
		self.protocol_lines = {}
		for vrf in self.jPtObj.VRFs.keys():
			VRF = self.jPtObj.VRFs[vrf]
			if not VRF.protocol_vrf_lines: continue
			VRF.ospf_area_ids_lines = self.get_ospf_area_ids_lines(VRF.protocol_vrf_lines)
			VRF.ospf_other_lines = self.get_ospf_other_lines(VRF.protocol_vrf_lines)
			VRF.area_ids = self.get_area_ids(VRF.ospf_area_ids_lines)
			self.protocol_lines[vrf] = VRF

	def get_area_ids(self, ospf_area_ids_lines):
		area_ids = set()
		for line in ospf_area_ids_lines:
			area_ids.add( line.split(f" protocols {self.protocol} area ")[-1].split()[0] )
		return area_ids

	def get_ospf_area_ids_lines(self, lines):
		ospf_area_ids_lines = [ line for line in lines if line.find(f" protocols {self.protocol} area ") > 0 ]
		return ospf_area_ids_lines

	def get_ospf_other_lines(self, lines):
		ospf_other_lines = [ line for line in lines if line.find(f" protocols {self.protocol} area ") == -1 ]
		return ospf_other_lines

	def iterate_for_ospf(self):
		protocol_ospf_dict = {}
		for vrf, VRF in self.protocol_lines.items():
			if not VRF.protocol_vrf_lines: continue
			vrf_dict = add_blankdict_key(protocol_ospf_dict, vrf)
			self.iterate_instance_funcs(VRF, vrf_dict)
			self.iterate_area_funcs(VRF, vrf_dict)
		return protocol_ospf_dict

	def iterate_instance_funcs(self, VRF, vrf_dict):
		for line  in VRF.ospf_other_lines:
			line = line.strip().split(f"protocols {self.protocol}")[-1]			
			spl = line.strip().split()
			for f in self.ospf_instance_attr_functions:
				f(vrf_dict, line, spl)

	def iterate_area_funcs(self, VRF, vrf_dict):
		for area in VRF.area_ids:
			for line in VRF.ospf_area_ids_lines:
				if line.find(f" protocols {self.protocol} area {area}") == -1: continue
				line = line.strip().split(f"protocols {self.protocol}")[-1]			
				_area_dict = add_blankdict_key(vrf_dict, 'area')
				area_dict = add_blankdict_key(_area_dict, area)
				spl = line.strip().split()
				for f in self.ospf_area_attr_functions:
					f(area_dict, line, spl)


# ------------------------------------------------------------------------------
#  ospf parser calling function
# ------------------------------------------------------------------------------
def get_ospf_running(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: protocols ospf level parsed output dictionary
	"""    	
	O = OSPF(cmd_op, 'ospf')
	O()
	return O.logical_systems_dict

def get_ospf3_running(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: protocols ospf3 level parsed output dictionary
	"""    	
	O = OSPF(cmd_op, 'ospf3')
	O()
	return O.logical_systems_dict
# ------------------------------------------------------------------------------

