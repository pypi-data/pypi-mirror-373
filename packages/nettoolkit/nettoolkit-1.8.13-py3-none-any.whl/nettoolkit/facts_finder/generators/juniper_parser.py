"""Juniper devices (Switch/Router) configuration parser directive. 
"""
# ------------------------------------------------------------------------------
from collections import OrderedDict
from nettoolkit.nettoolkit_common import *

from .juniper import *
from .device import DevicePapa, CMD_LINE_START_WITH
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# // Juniper //
# ------------------------------------------------------------------------------
# COMMANDS LIST DICTIONARY, DEFINE **kwargs as dictionary in command value     #
# ``juniper_cmds_list``
# ------------------------------------------------------------------------------
juniper_cmds_list = OrderedDict([
	('show interfaces descriptions', {}),
	('show lldp neighbors', {'dsr': True}),		# dsr = domain-suffix removal, default=True
	('show configuration', {}),
	('show version', {}),
	('show chassis hardware', {}),
	# ('show arp', {}),


	## ADD More as grow ##
])
# ------------------------------------------------------------------------------
# COMMAND OUTPUT HIERARCHY LEVEL
# ``juniper_cmds_op_hierachy_level``
# ------------------------------------------------------------------------------
juniper_cmds_op_hierachy_level = OrderedDict([
	('show interfaces descriptions', 'Interfaces'),
	('show lldp neighbors', 'Interfaces'),
	('show configuration', (
			'Interfaces', 
			'var', 
			'vrf', 
			'bgp', 
			'ospf', 
			'static', 
			'prefix_list' 
		)
	),
	('show version', 'var'),
	('show chassis hardware', ('Interfaces', 'var')),
	# 'show arp': 'arp',


	## ADD More as grow ##
])
# ------------------------------------------------------------------------------
# Dict of Juniper commands, %trunked commands mapped with parser func.
# ``juniper_commands_parser_map``
# ------------------------------------------------------------------------------
juniper_commands_parser_map = OrderedDict([

    # ---- ADD PARSER FUNCTIONS IN BELOW FORMAT ONLY ----
    # 'juniper show command' : function_name,                               ## if single hierarchy details from output
    # 'juniper show command' : (function_name1, function_name2, ... ),      ## if multiple hierarchies details from output
    # ---------------------------------------------------

	('show interfaces descriptions', get_int_description),
	('show lldp neighbors', get_lldp_neighbour),
	('show configuration', (
			get_interfaces_running, 
			get_running_system, 
			get_instances_running, 
			get_instances_bgps, 
			get_instances_ospfs, 
			get_system_running_routes, 
			get_system_running_prefix_lists
		)
	),
	('show version', get_version),
	('show chassis hardware', (get_chassis_hardware, get_chassis_serial)),
	# 'show interfaces terse': None,
	# 'show arp': get_arp_table,
	# 'show bgp summary': None,
    
    # ... ADD MORE AS NECESSARY ... 
])
# ------------------------------------------------------------------------------

def absolute_command(cmd, cmd_parser_map, op_filter=False):
	"""returns absolute truked command if any filter applied
	if founds an entry in juniper_commands_parser_map keys.

	Args:
		cmd (str): executed/ captured command ( can be trunked or full )
		cmd_parser_map (dict, set): containing juniper standard trunked command
		op_filter (bool, optional): to be remove any additional filter from command or not. Defaults to False.

	Returns:
		str: juniper command - trunked
	"""    	
	if op_filter:
		abs_cmd = cmd.split("|")[0].strip()
	else:
		abs_cmd = cmd.replace("| no-more", "").strip()
	for c_cmd in cmd_parser_map:
		word_match = abs_cmd == c_cmd
		if word_match: break
	if word_match:  return abs_cmd
	return cmd

# ------------------------------------------------------------------------------
class Juniper(DevicePapa):
	"""class defining juniper parser directives.

	Args:
		file (str): capture file
	"""    	
	dev_type = 'juniper_junos'
	
	def __init__(self, file):
		"""Initialize the object by providing the capture file
		"""    		
		super().__init__(file)

	def parse(self, cmd, *arg, **kwarg):
		"""start command output parsing from provided capture.
		provide any additional arg, kwargs for dynamic filtering purpose.

		Args:
			cmd (str): juniper command for which output to be parsed

		Returns:
			dict: dictionary with the details captured from the output
		""" 
		abs_cmd = absolute_command(cmd, juniper_commands_parser_map)
		parse_func = juniper_commands_parser_map[abs_cmd]
		if isinstance(parse_func, tuple):
			parsed_op = [self.run_parser(pf, abs_cmd, *arg, **kwarg) for pf in parse_func]
		else:
			parsed_op = self.run_parser(parse_func, abs_cmd, *arg, **kwarg)
		return parsed_op

	def run_parser(self, parse_func, abs_cmd, *arg, **kwarg):
		"""derives the command output list for the provided trunked command.
		and runs provided parser function on to it to get the necessary details.
		provide any additional arg, kwargs for dynamic filtering purpose.

		Args:
			parse_func (func): function
			abs_cmd (str): juniper trunked command for which output to be parsed

		Returns:
			dict: dictionary with the details captured from the output
		"""   
		op_list = get_op(self.file, abs_cmd)		
		parsed_output = self._run_parser(parse_func, op_list, *arg, **kwarg)
		po_for_xl = parsed_output['op_dict']
		return po_for_xl

	def verify(self):
		"""verifications of existance of mandatory commands in output captures

		Raises:
			Exception: Raises if a mandatory command is missing in output  
		"""		
		mandatory_cmds = set(juniper_commands_parser_map.keys())
		found_cmds = set()
		with open(self.file, 'r') as f:
			lines = f.readlines()
		for line in lines:
			if line.startswith(f"# {CMD_LINE_START_WITH}"):
				cmd = line.split(CMD_LINE_START_WITH)[-1]
				abs_cmd = absolute_command(cmd, juniper_commands_parser_map)
				found_cmds.add(abs_cmd.split("|")[0])
		missing_op_cmds = mandatory_cmds.difference(found_cmds)
		if missing_op_cmds:
			for moc in missing_op_cmds:
				print(f'[-] Missing capture for command: {moc}, in file {self.file}')
			raise Exception(f'[-] Cannot Continue due to missing mandatory capture(s)')


# ------------------------------------------------------------------------------
