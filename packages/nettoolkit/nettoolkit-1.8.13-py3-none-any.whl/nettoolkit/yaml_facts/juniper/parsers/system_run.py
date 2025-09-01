"""juniper system config parser from set config """

# ------------------------------------------------------------------------------
from .common import *
from .run import Running
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  system parser functions
# ------------------------------------------------------------------------------

def get_system_common_attrs(op_dict, l, spl):
	## Ex: set system host-name [abcd]
	attrs = {
		'host-name': ('host-name', 'hostname'),
		'name-server': ('name-server', 'dns_server', ),
		'domain-name': ('domain-name', )
	}
	for item, keys in attrs.items():
		if spl[2] != item: continue
		for key in keys:
			append_attribute(op_dict, key, spl[-1], remove_duplicate=True)

def get_system_syslog_servers(op_dict, l, spl):
	if not l.startswith("set system syslog host"): return
	_dict = add_blankdict_key(op_dict, 'syslog')
	append_attribute(_dict, 'servers', spl[4], remove_duplicate=True)

def get_system_ntp_servers(op_dict, l, spl):
	if not l.startswith("set system ntp server"): return 
	_dict = add_blankdict_key(op_dict, 'ntp')
	append_attribute(_dict, 'servers', spl[4], remove_duplicate=True)

def get_system_gtac_servers(op_dict, l, spl):
	if spl[2] != "tacplus-server": return
	tacacs_dict = add_blankdict_key(op_dict, 'tacacs')
	append_attribute(tacacs_dict, 'servers', spl[3], remove_duplicate=True)
	if 'secret' in spl:
		append_attribute(tacacs_dict, 'key', get_juniper_pw_string(spl, 5), remove_duplicate=True)
	if 'port' in spl:
		append_attribute(tacacs_dict, 'tcp-port', next_index_item(spl, 'port'), remove_duplicate=True)
	if 'source-address' in spl:
		append_attribute(tacacs_dict, 'source-address', next_index_item(spl, 'source-address'), remove_duplicate=True)

def get_system_mgmt_ip(op_dict, l, spl):
	if spl[-2] != "source-address": return
	update_key_value(op_dict, 'management_ip', spl[-1])

def get_system_banner(op_dict, l, spl):
	if not l.startswith("set system login announcement"): return
	update_key_value(op_dict, 'banner', " ".join(spl[4:]))

def get_system_as_number(op_dict, l, spl):
	if not l.startswith("set routing-options autonomous-system "):  return
	update_key_value(op_dict, 'as-number', spl[3])

# ------------------------------------------------------------------------------
#  system extractor class
# ------------------------------------------------------------------------------
@dataclass
class RunningSystem(Running):
	cmd_op: list[str,] = field(default_factory=[])

	attr_functions = [
		get_system_common_attrs,
		get_system_syslog_servers,
		get_system_ntp_servers,
		get_system_gtac_servers,
		get_system_mgmt_ip,
		get_system_banner,
		get_system_as_number,

	]

	def __post_init__(self):
		super().__post_init__()

	def __call__(self):
		self.iterate_logical_systems(hierarchy='system')

	def start(self):
		system_lines = self.filter_system_lines()
		system_dict = self._get_attributes(system_lines)
		return system_dict

	def filter_system_lines(self):
		system_lines = []
		for line in self.set_cmd_op:
			if blank_line(line): continue
			if line.startswith("#"): continue 
			if line.startswith("set system "):
				system_lines.append(line)
			if line.startswith("set routing-options autonomous-system "):
				system_lines.append(line)
		return system_lines

	def _get_attributes(self, lines):
		attr_dict = {}
		for line in lines:
			line = line.strip()
			spl  = line.split()
			for f in self.attr_functions:
				# try: 
					f(attr_dict, line, spl)
				# except IndexError: pass
		return attr_dict

# ------------------------------------------------------------------------------
#  system parser calling function
# ------------------------------------------------------------------------------
def get_system_running(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: system level parsed output dictionary
	"""    	
	R  = RunningSystem(cmd_op)
	R()
	return R.logical_systems_dict
# ------------------------------------------------------------------------------

