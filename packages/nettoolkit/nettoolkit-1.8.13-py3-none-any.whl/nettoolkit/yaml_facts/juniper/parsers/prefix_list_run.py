"""juniper prefix list parsing from set config  """

# ------------------------------------------------------------------------------
from .common import *
from .run import Running
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  prefix-list parser functions
# ------------------------------------------------------------------------------

def get_pfx_list_prefix(pfx_list, spl):
	try:
		pfx = addressing(spl[4])
	except:
		return
	pfx = shrink(spl[4]) if pfx.version == 6 else spl[4]
	pfx_list.append(pfx)

# ------------------------------------------------------------------------------
#  prefix-list extractor class
# ------------------------------------------------------------------------------

@dataclass
class RunningPrefixLists(Running):
	cmd_op: list[str, ] = field(default_factory=[])

	attr_functions = (
		get_pfx_list_prefix,
	)

	pfx_str_begin_with = 'set policy-options prefix-list '

	def __post_init__(self):
		super().__post_init__()

	def __call__(self):
		self.iterate_logical_systems(hierarchy='prefix-lists')

	def start(self):
		self.pl_dict = {}
		self.filter_prefixlist_lines()
		self.spl_prefix_list_lines = [ line.strip().split() for line in self.prefix_list_lines ]
		self.get_pfx_lines_dict()
		self.get_attributes()
		return self.pl_dict

	def filter_prefixlist_lines(self):
		self.prefix_list_lines = [line.strip() for line in self.set_cmd_op if line.find(self.pfx_str_begin_with) > -1]

	def get_pfx_lines_dict(self):
		self.pfx_list_dict = {}
		for line, spl in  zip(self.prefix_list_lines, self.spl_prefix_list_lines):
			pl_name = spl[3]
			pl_name_list = add_blanklist_key(self.pfx_list_dict, pl_name)
			pl_name_list.append(spl)

	### /// attributes /// ###

	def get_attributes(self):
		for pfx, pfx_spl_lines in self.pfx_list_dict.items():
			pl_name_list = add_blanklist_key(self.pl_dict, pfx)
			for spl in pfx_spl_lines:
				for f in self.attr_functions:
					# try:
						f(pl_name_list, spl)
					# except IndexError: pass


# ------------------------------------------------------------------------------
#  prefix-list parser calling function
# ------------------------------------------------------------------------------
def get_system_running_prefix_lists(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: prefix-list level parsed output dictionary
	"""    	
	R  = RunningPrefixLists(cmd_op)
	R()
	return R.logical_systems_dict
# ------------------------------------------------------------------------------

