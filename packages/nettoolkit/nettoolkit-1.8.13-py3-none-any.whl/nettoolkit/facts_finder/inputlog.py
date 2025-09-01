# ------------------------------------------------------------------------------------------------
from pathlib import *

# ------------------------------------------------------------------------------------------------

CISCO_BANNER = """!================================================================================
! output for command: COMMAND 
!================================================================================
"""
JUNIPER_BANNER = """#================================================================================
# output for command: COMMAND 
#================================================================================
"""

# ------------------------------------------------------------------------------------------------

def get_hostname(lines):
	"""get hostname from provided list of lines/configuration 

	It watches for one of these commands:

		'show configuration', 'show version', 'show interfaces terse',
		'sh ver', 'sh run', 'sh int status', 'sh int desc',


	Args:
		lines (list): list of lines/configuration

	Returns:
		str: hostname
	"""	
	cmds = {
		'show configuration', 'show version', 'show interfaces terse',
		'sh ver', 'sh run', 'sh int status', 'sh int desc',
	}
	for line in lines:		
		if line.strip().startswith('hostname') or line.strip().startswith('host-nmae'):
			return line.strip().split('name')[-1].strip()

		elif line.find("#") > -1 or line.find(">") > -1:
			for cmd in cmds:
				if line.find(cmd) > 1:
					return line.split(cmd)[0].split("@")[-1].strip()[:-1]


def get_model(lines):
	"""get the device model from list of lines/configuration

	Args:
		lines (list): list of lines/configuration

	Returns:
		str: device model (cisco, juniper, None)
	"""	
	for line in lines:
		if line.strip().startswith("!"): return 'cisco'
		if line.strip().startswith("#"): return 'juniper'


def get_cmd_lines_cisco(lines, hostname, model):
	"""get the command lines for cisco output

	Args:
		lines (list): list of lines/configuration
		hostname (str): hostname of device
		model (str): model of device (optional: not in use)

	Returns:
		dict: dictionary of command lines, with its index as key
	"""	
	cmd_dict = {}
	for i, line in enumerate(lines):
		if not line.find(hostname)>-1: continue
		si = line.find(hostname)
		cmd_begin_i = si + len(hostname)
		cmd = line[cmd_begin_i:].strip()
		if cmd[1:] and cmd[0] in(">", "#"):# and not cmd.endswith("?"):
			cmd_dict[i] = cmd[1:].strip()

	return cmd_dict

def get_output_lines_list(lines, startidx, endidx):
	"""get the section of lines from provided list of lines

	Args:
		lines (list): list of lines/configuration
		startidx (int): lines starting from index
		endidx (int): lines ending at index

	Returns:
		list: section of list
	"""	
	return lines[startidx:endidx]

def is_valid_op(lines):
	"""checks if provided output/lines are valid output

	Args:
		lines (list): list of lines/show output

	Returns:
		bool: valid or not
	"""	
	return lines and not lines[0].strip().startswith("^")


def get_banner(model, cmd):
	"""get the standard banner for provided device type

	Args:
		model (str): device model (cisco, juniper)
		cmd (str): show command

	Returns:
		str: respective banner
	"""	
	banner = ""
	if model == 'cisco': 
		banner = CISCO_BANNER.replace("COMMAND", cmd)
	if model == 'juniper': 
		banner = JUNIPER_BANNER.replace("COMMAND", cmd)
	return banner

def trim_hostname_lines(cmd_output_lines_list, hostname):
	"""trim hostname lines from output lines list

	Args:
		cmd_output_lines_list (list): list of lines of show output
		hostname (str): hostname of device

	Returns:
		list: updated list
	"""	
	return [ line
		for line in cmd_output_lines_list
			if not (line.find(hostname+"#")>-1 
				 or line.find(hostname+">")>-1 
				 or line.startswith('{master:')
				)
	]


def create_new_file(op_file):
	"""create a new blank file

	Args:
		op_file (str): output file name
	"""	
	with open(op_file, 'w') as f:
		f.write("")

def get_idx_tuples(sorted_idx, cmd_lines_idx):
	"""get indexes tuples list

	Args:
		sorted_idx (list): list of all index values
		cmd_lines_idx (list): list of command lines index values ( not in use )

	Returns:
		list: list of tuples
	"""	
	idx_tuples = []
	for i, endidx in enumerate(sorted_idx):
		if i == 0: 
			startidx = endidx+1
			continue
		# cmd = cmd_lines_idx[sorted_idx[i-1]]
		idx_tuples.append((startidx, endidx))
		startidx = endidx+1
	return idx_tuples

def convert_and_write(op_file, lines, hostname, model):
	"""converts lines to string and write to output file 

	Args:
		op_file (str): output file
		lines (list): list of lines/output
		hostname (str): hostname
		model (str): device model
	"""	
	cmd_lines_idx = get_cmd_lines_cisco(lines, hostname, model)
	sorted_idx = sorted(cmd_lines_idx)
	sorted_idx.append(len(lines))
	create_new_file(op_file)
	idx_tuples = get_idx_tuples(sorted_idx, cmd_lines_idx)
	for s, e in idx_tuples:
		cmd = cmd_lines_idx[s-1]
		if cmd.endswith("?"): continue
		banner = get_banner(model, cmd)
		cmd_output_lines_list = get_output_lines_list(lines, s, e)
		cmd_output_lines_list = trim_hostname_lines(cmd_output_lines_list, hostname)
		valid_op = is_valid_op(cmd_output_lines_list)
		s = ""
		if valid_op:
			s += banner
			s += "".join(cmd_output_lines_list)
			with open(op_file, 'a') as f:
				f.write(s)


def is_cit_file(lines):
	"""checks if provided output lines are capture it configuration generated.

	Args:
		lines (list): list of lines output

	Returns:
		bool: check for capture-it generated file or not
	"""	
	for line in lines:
		if line[1:].startswith(" output for command:"):
			return True
	return False

def to_cit(input_log):
	"""converts normal capture to capture-it type output

	Args:
		input_log (str): input capture file

	Returns:
		str: output capture file
	"""	
	p = Path(input_log)
	previous_path = p.resolve().parents[0]
	with open(input_log, 'r') as f:
		lines = f.readlines()
	hostname = get_hostname(lines)
	output_log = f"{previous_path}/{hostname}.log"
	output_bkp_log = f"{previous_path}/{hostname}-bkp.log"
	if input_log == output_log:
		with open(output_bkp_log, 'w') as f:
			f.write("".join(lines))
	model = get_model(lines)
	if is_cit_file(lines):
		return input_log
	convert_and_write(output_log, lines, hostname, model)
	return output_log


# ------------------------------------------------------------------------------------------------
#   MAIN
# ------------------------------------------------------------------------------------------------
if __name__ == "__main__":
	pass
	#
# ------------------------------------------------------------------------------------------------


