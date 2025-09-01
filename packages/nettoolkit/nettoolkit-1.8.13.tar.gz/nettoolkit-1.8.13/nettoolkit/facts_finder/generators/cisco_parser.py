"""Cisco devices (Switch/Router) configuration parser directive. 
"""
# ------------------------------------------------------------------------------
from collections import OrderedDict
from nettoolkit.nettoolkit_common import *

from .cisco import *
from .device import DevicePapa, CMD_LINE_START_WITH
# ------------------------------------------------------------------------------

LEN_CMD_LINE = len(CMD_LINE_START_WITH)

# ------------------------------------------------------------------------------
# // Cisco //
# Since lot of stuff offloaded to ntc many of the functionality are remarked/disabled.
# ------------------------------------------------------------------------------
# COMMANDS LIST DICTIONARY, DEFINE **kwargs as dictionary in command value     #
# ``cisco_cmds_list``
# ------------------------------------------------------------------------------
cisco_cmds_list = OrderedDict([
	('sh lldp nei', {'dsr': True}),			# dsr = domain suffix removal
	('sh cdp nei', {'dsr': True}),			# dsr = domain suffix removal
	('sh int status', {}),
	('sh int desc', {}),           # N/R - part of running interface config 
	# ('show mac address-table', {}),  # N/W - as expected
	# ('sh ip arp', {}),  # N/W - as expected
	('sh run', {}),
	('sh ver', {}),
	## ADD More as grow ##
])
# ------------------------------------------------------------------------------
# COMMAND OUTPUT HIERARCHY LEVEL ( key need to match with 'cisco_cmds_list' )
# ``cisco_cmds_op_hierachy_level``
# ------------------------------------------------------------------------------
cisco_cmds_op_hierachy_level = OrderedDict([
	('sh lldp nei', 'Interfaces'),
	('sh cdp nei', 'Interfaces'),
	('sh int status', 'Interfaces'),
	('sh int desc', 'Interfaces'),
	# 'show mac address-table': 'arp',
	# 'sh ip arp': 'arp',
	('sh run', (
			'var', 
			'bgp', 
			'Interfaces', 
			'vrf',
			'ospf',
			'static',
			'prefix_list'
			)),
	('sh ver', 'var'),
	## ADD More as grow ##
])
# ------------------------------------------------------------------------------
# Dict of cisco commands, %full commands in keys mapped with parser func.
# ``cisco_commands_parser_map``
# ------------------------------------------------------------------------------
cisco_commands_parser_map = OrderedDict([
	('show lldp neighbors', get_lldp_neighbour),
	('show cdp neighbors', get_cdp_neighbour),
	('show interfaces status', get_interface_status),
	('show interfaces description', get_interface_description),
	# 'show mac address-table': get_mac_address_table,
	# 'show ip arp': get_arp_table,
	('show running-config', (
			get_system_running, 
			get_bgp_running, 
			get_interfaces_running, 
			get_vrfs_running,
			get_ospf_running,
			get_system_running_routes,
			get_system_running_prefix_lists,
			)),
	('show version', get_version),
])
# cisco_yaml_parser_map = OrderedDict([
# 	('show lldp neighbors', get_lldp_neighbour_yml),
# 	('show cdp neighbors', get_cdp_neighbour_yml),
# 	('show interfaces status', get_interface_status_yml),
# 	('show interfaces description', get_interface_description_yml),
# 	# 'show mac address-table': get_mac_address_table,
# 	# 'show ip arp': get_arp_table,
# 	('show running-config', (
# 			get_system_running_yml, 
# 			get_bgp_running_yml, 
# 			get_interfaces_running_yml, 
# 			get_vrfs_running_yml,
# 			get_ospf_running_yml,
# 			get_system_running_routes_yml,
# 			get_system_running_prefix_lists_yml,
# 			)),
# 	('show version', get_version_yml),
# ])


# ------------------------------------------------------------------------------

def absolute_command(cmd, cmd_parser_map):
	"""returns absolute full command for shorteened cmd
	if founds an entry in cmd_parser_map keys.

	Args:
		cmd (str): executed/ captured command ( can be trunked or full )
		cmd_parser_map (dict, set): containing cisco standard full length (absolute command) equivalent command

	Returns:
		str: cisco command - full untrunked
	"""
	spl_cmd = cmd.split()
	for c_cmd in cmd_parser_map:
		spl_c_cmd = c_cmd.split()
		if len(spl_cmd) == len(spl_c_cmd):
			for i, word in enumerate(spl_cmd):
				try:
					word_match = spl_c_cmd[i].startswith(word)
					if not word_match: break
				except:
					word_match = False
					break
			if word_match: break
		else:
			word_match = False
	if word_match:  return c_cmd
	return cmd


def get_op_cisco(file, abs_cmd, cmd_parser_map=cisco_commands_parser_map):
	"""returns output of a command in list format found from capture file.
	this is differ from general get_op() in a way that it has to get absolute command
	in case if provided trunked while capture. Juniper does auto-complete at terminal
	so it does not require that step.

	Either cisco output should either be captured thru package/utility - capture_it, 
	or output should be in below format.

	! ========================================

	! output for command: <show command>

	! ========================================

	<< output of show command >>


	Args:
		file (str): capture file name
		abs_cmd (str): cisco absolute command string
		cmd_parser_map (dict, set): containing cisco standard full length (absolute command) equivalent command

	Returns:
		list: capture of the output in list format
	"""    	
	file_lines = read_file(file)
	toggle, op_lst = False, []
	for l in file_lines:
		if l.find(CMD_LINE_START_WITH)>0:
			cmd_line_cmd = absolute_command(l[LEN_CMD_LINE+1:].strip(), cmd_parser_map)
			toggle = abs_cmd == cmd_line_cmd
			continue
		if toggle:
			op_lst.append(l.rstrip())
	return op_lst

# ------------------------------------------------------------------------------
class Cisco(DevicePapa):
	"""class defining cisco parser directives.

	Args:
		file (str): capture file
	"""    	
	dev_type = 'cisco_ios'
	
	def __init__(self, file):
		"""Initialize the object by providing the capture file
		"""    		
		super().__init__(file)

	def parse(self, cmd, *arg, **kwarg):
		"""start command output parsing from provided capture.
		provide any additional arg, kwargs for dynamic filter purpose.

		Args:
			cmd (str): cisco command for which output to be parsed

		Returns:
			dict: dictionary with the details captured from the output
		"""    		
		abs_cmd = absolute_command(cmd, cisco_commands_parser_map)
		parse_func = cisco_commands_parser_map[abs_cmd]
		if isinstance(parse_func, tuple):
			parsed_op = [self.run_parser(pf, abs_cmd, *arg, **kwarg) for pf in parse_func]
		else:
			parsed_op = self.run_parser(parse_func, abs_cmd, *arg, **kwarg)
		return parsed_op

	def run_parser(self, parse_func, abs_cmd, *arg, **kwarg):
		"""derives the command output list for the provided absolute command.
		and runs provided parser function on to it to get the necessary details.
		provide any additional arg, kwargs for dynamic filter purpose.

		Args:
			parse_func (func): function
			abs_cmd (str): cisco absolute command for which output to be parsed

		Returns:
			dict: dictionary with the details captured from the output
		"""   
		op_list = get_op_cisco(self.file, abs_cmd, cisco_commands_parser_map)
		parsed_output = self._run_parser(parse_func, op_list, *arg, **kwarg)
		po_for_xl = parsed_output['op_dict']

		return po_for_xl

	def verify(self):
		"""verification in capture for existance of cisco command in output

		Raises:
			Exception: If missing any mandatory captures
		"""		
		mandatory_cmds = set(cisco_commands_parser_map.keys())
		found_cmds = set()
		with open(self.file, 'r') as f:
			lines = f.readlines()
		for line in lines:
			if line.startswith(f"! {CMD_LINE_START_WITH}"):
				cmd = line.split(CMD_LINE_START_WITH)[-1]
				abs_cmd = absolute_command(cmd, cisco_commands_parser_map)
				found_cmds.add(abs_cmd)
		missing_op_cmds = mandatory_cmds.difference(found_cmds)
		if missing_op_cmds:
			for moc in missing_op_cmds:
				print(f'[-] Missing capture for command: {moc}, in file {self.file}')
			raise Exception(f'[-] Cannot Continue due to missing mandatory capture(s)')




# ------------------------------------------------------------------------------
