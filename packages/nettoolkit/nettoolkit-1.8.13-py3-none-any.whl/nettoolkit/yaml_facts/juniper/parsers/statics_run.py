"""juniper routes parsing from set config  """

# ------------------------------------------------------------------------------
from .common import *
from .run import Running
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  static parser functions
# ------------------------------------------------------------------------------

def get_static_next_hop(op_dict, spl):
	if spl[1] != 'next-hop': return 
	append_attribute(op_dict, attribute='next_hop', value=spl[2])

def get_static_preferance(op_dict, spl):
	if spl[1] != 'preference': return 
	append_attribute(op_dict, attribute='adminisrative_distance', value=spl[2])

def get_static_tag(op_dict, spl):
	if spl[1] != 'tag': return 
	append_attribute(op_dict, attribute='tag_value', value=spl[2])

def get_static_remark(op_dict, spl):
	if "comment:" not in spl: return 
	remark = " ".join(spl[spl.index("comment:")+1:])
	append_attribute(op_dict, attribute='remark', value=remark)

def get_static_resolve(op_dict, spl):
	if "resolve" not in spl: return 
	append_attribute(op_dict, attribute='resolve', value=True)

def get_static_retain(op_dict, spl):
	if "retain" not in spl: return 
	append_attribute(op_dict, attribute='retain', value=True)

# ------------------------------------------------------------------------------
#  statics extractor class
# ------------------------------------------------------------------------------

@dataclass
class RunningRoutes(Running):
	cmd_op: list[str,] = field(default_factory=[])

	route_spl_str = {
		4: ' routing-options static route ',
		6: ' routing-options rib blue.inet6.0 static route ',
	}

	attr_functions = [
		get_static_next_hop,
		get_static_preferance,
		get_static_tag,
		get_static_remark,
		get_static_resolve,
		get_static_retain,

	]

	def __post_init__(self):
		super().__post_init__()

	def __call__(self):
		self.iterate_logical_systems(hierarchy='statics')

	def start(self):
		self.route_dict = {}
		for v, spl_str in self.route_spl_str.items():
			self.filter_n_merge(v, spl_str)
		return self.route_dict

	def filter_n_merge(self, v, spl_str):
		routes_lines = self.filter_routes_lines(spl_str)
		vrf_and_route_tuple = self.split_vrf_and_route_portions(routes_lines, spl_str)
		vrfs = self.get_vrf_list(vrf_and_route_tuple)
		vrf_pfx_lines = self.get_vrf_pfx_lines(vrf_and_route_tuple, vrfs)
		attr_dict = self.get_attributes(vrf_pfx_lines, version=v)
		merge_dict( self.route_dict, attr_dict )

	def filter_routes_lines(self, route_spl_str):
		return [line.strip() for line in self.set_cmd_op if line.find(route_spl_str) > -1]

	def split_vrf_and_route_portions(self, routes_lines, route_spl_str):
		return [ [item.strip().split() for item in line.split(route_spl_str)] for line in routes_lines]

	def get_vrf_list(self, vrf_and_route_tuple):
		vrfs = set()
		for vrf_l, route_l in  vrf_and_route_tuple:
			# spl_vrf_l = vrf_l.strip().split()
			if len(vrf_l)>2:
				vrfs.add(vrf_l[2])
			else:
				vrfs.add(None)
		return vrfs

	def get_vrf_pfx_lines(self, vrf_and_route_tuple, vrfs):
		vrf_pfx_lines = {}		
		for vrf in vrfs:
			vrf_dict = add_blankdict_key(vrf_pfx_lines, vrf)
			for vrf_l, route_l in vrf_and_route_tuple:
				if (len(vrf_l)>2 and vrf != vrf_l[2]) or (len(vrf_l) < 2 and vrf is not None): continue
				pfx = route_l[0]
				pfx_list = add_blanklist_key(vrf_dict, pfx)
				pfx_list.append(route_l)
		return vrf_pfx_lines

	def get_attributes(self, vrf_pfx_lines, version):
		attr_dict = {}
		for vrf, vrf_dict in vrf_pfx_lines.items():
			vrf_attr_dict = add_blankdict_key(attr_dict, vrf)
			ip_vrf_attr_dict = add_blankdict_key(vrf_attr_dict, f"ipv{version}")
			for pfx, lines in vrf_dict.items():
				vrf_pfx_attr_dict = add_blankdict_key(ip_vrf_attr_dict, pfx)
				for spl in lines:
					for f in self.attr_functions:
						# try:
							f(vrf_pfx_attr_dict, spl)
						# except IndexError: pass
		return attr_dict


# ------------------------------------------------------------------------------
#  system parser calling function
# ------------------------------------------------------------------------------
def get_system_running_routes(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: statics level parsed output dictionary
	"""    	
	R  = RunningRoutes(cmd_op)
	R()
	return R.logical_systems_dict
# ------------------------------------------------------------------------------

