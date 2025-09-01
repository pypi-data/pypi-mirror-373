# """Common Definitions used across project"""
# ------------------------------------------------------------------------------
from dataclasses import dataclass, field
import yaml
from yaml import UnsafeLoader
import subprocess as sp
import pandas as pd
import os
from  pathlib import Path

# ------------------------------------------------------------------------------

### IDENTIFER OF COMMAND LINE ### >
CMD_LINE_START_WITH = "output for command: "
CISCO_ABS_COMMANDS = {
	'show lldp neighbors',
	'show cdp neighbors',
	'show interfaces status',
	'show interfaces description',
	'show mac address-table',
	'show ip arp',
	'show running-config',
	'show version',
}

JUNIPER_ABS_COMMANDS = {
	'show interfaces descriptions',
	'show lldp neighbors',
	'show configuration',
	'show version',
	'show chassis hardware',
	'show interfaces terse',
	'show arp',
	'show bgp summary',
}

# ------------------------------------------------------------------------------

def get_file_path(file):
	"""returns folder of given file path

	Args:
		file (str): full string length file path

	Returns:
		str: folder location of file
	"""    	
	p = Path(file)	
	return p.parent

def get_file_name(file, ext=False):
	"""returns file name of given file path

	Args:
		file (str): full string length file path
		ext (bool, optional): include extension or not. Defaults to False.

	Returns:
		str: file name
	"""    	
	p = Path(file)	
	return p.name if ext else p.stem



def create_folders(folders, *, silent=True):
	"""Creates Folders

	Args:
		folders (list,str): folder(s)
		silent (bool, optional): Create without prompt. Defaults to True.

	Returns:
		bool: Success/Fail
	"""    	
	cf = 1
	if isinstance(folders, str):
		folders = [folders,]
	for folder in folders:
		if not os.path.exists(folder):
			if not silent: print(f"[+] Creating: {folder}", end="\t")
			try:
				os.makedirs(folder)
				print("OK.")
			except:
				print("Failed.")
				cf = 0
	return bool(cf)

# ------------------------------------------------------------------------------

def remove_domain(hn):
	"""Removes domain suffix from provided hostname string

	Args:
		hn (str): fully qualified dns hostname

	Returns:
		str: hostname left by removing domain suffix
	"""
	return hn.split(".")[0]

def read_file(file):
	"""read the provided text file and retuns output in list format

	Args:
		file (str): text file name

	Returns:
		list: output converted to list (separated by lines)
	"""    	
	with open(file, 'r') as f:
		file_lines = f.readlines()
	return file_lines

def read_yaml_mode_us(file):
	try:
		with open(file, 'r') as f:
			return  yaml.load(f, Loader=UnsafeLoader)
	except Exception as e:
		raise Exception(f"[-] Unable to Read the file, or invalid data \n{e}")


# ------------------------------------------------------------------------------

def get_op(file, cmd):
	"""filter the command output from given captured file.  
	Note: output should be taken from capture_it utility or it should be in the format
	derived by it.

	Args:
		file (str): capture file
		cmd (str): show command for which output to capture

	Returns:
		list: filtered command output in list format
	"""    	
	file_lines = read_file(file)
	toggle, op_lst = False, []
	for l in file_lines:
		if l.find(CMD_LINE_START_WITH)>0:
			toggle = l.find(cmd)>0
			continue
		if toggle:
			op_lst.append(l.strip())
	return op_lst

def get_ops(file, cmd_startswith):
	"""filter the command outputs from given captured file.  
	Note: output should be taken from capture_it utility or it should be in the format
	derived by it.

	Args:
		file (str): capture file
		cmd_startswith (str): show command start string

	Returns:
		dict: filtered command output in dict format
	"""    	
	file_lines = read_file(file)
	toggle, op_lst, op_dict = False, [], {}
	for l in file_lines:
		if toggle and l.find(CMD_LINE_START_WITH)>0:
			op_dict[cmd] = op_lst
			op_lst = []
			toggle=False
		if l.find(CMD_LINE_START_WITH)>0:
			toggle = l.find(cmd_startswith)>0
			cmd = l[l.find(cmd_startswith):].strip()
			continue
		if toggle:
			op_lst.append(l.rstrip())
	return op_dict
# ------------------------------------------------------------------------------

def blank_line(line): 
	"""checks if provided line is blank line or not.

	Args:
		line (str): input line

	Returns:
		bool: is line blank or not
	"""	
	return not line.strip()

def get_device_manufacturar(file):
	"""finds out manufacturer (cisco/juniper) from given capture file.
	in case if not found, it will return as Unidentified.

	Args:
		file (str): input capture file

	Returns:
		str: Either one from - Cisco, Juniper, Unidentified
	"""    	
	file_lines = read_file(file)
	return detect_device_type(file_lines)	

def detect_device_type(config_log_list):
	for line in config_log_list:
		if line[0] == "!":
			return 'Cisco'
		elif line[0] == "#":
			return "Juniper"
	return "Unidentified"

def verifid_output(cmd_op):
	"""vefifies if command output is in valid state.  Multiline string are splits with
	CR. and retuns as list. if input is a list, it will be returned as is.
	any other input will throw error.

	Args:
		cmd_op (list, str): Either list or Multiline string of output

	Raises:
		TypeError: Raise error if input is other than string or list.

	Returns:
		list: output in list format
	"""    	
	if isinstance(cmd_op, str):
		cmd_op = cmd_op.split("\n")
	if not isinstance(cmd_op, list):
		raise TypeError("Invalid Command Output Received.\n"
			f"Expected either multiline-string or list, received {type(cmd_op)}.")
	return cmd_op
# ------------------------------------------------------------------------------

def get_string_part(line, begin, end):
	"""get the sub-string out of provided long string(line)

	Args:
		line (str): string line
		begin (int): sub-str start point
		end (int): sub-str end point

	Raises:
		TypeError: Raise error if input is invalid or sub-string falls outside

	Returns:
		str: sub-string
	"""    	
	try: return line[begin: end].strip()
	except: raise TypeError("Unrecognized Input")

def get_string_trailing(line, begin_at):
	"""get the training part of sub-string starting from provided index

	Args:
		line (str): string line
		begin_at (int): sub-str start point

	Raises:
		TypeError: Raise error if input is invalid or sub-string falls outside

	Returns:
		str: sub-string
	"""    	
	try: return line[begin_at:].strip()
	except: raise TypeError("Unrecognized Input")
# ------------------------------------------------------------------------------

def standardize_mac(mac):
	"""removes . or : from mac address and make it a standard

	Args:
		mac (str): mac address

	Returns:
		str: standard format of mac address
	"""    	
	return mac.replace(":","").replace(".","")

def mac_2digit_separated(mac):
	"""converts input mac to 2 digit separated mac format, separator=`:`

	Args:
		mac (str): mac address

	Returns:
		str: 2 digit separated format of mac address
	"""    	
	mac = standardize_mac(mac)
	for x in range(6):
		if x == 0:  s = mac[:2]
		else: s += ":" + mac[x*2:(x*2)+2]
	return s

def mac_4digit_separated(mac):
	"""converts input mac to 4 digit separated mac format, separator=`.`

	Args:
		mac (str): mac address

	Returns:
		str: 4 digit separated format of mac address
	"""    	
	mac = standardize_mac(mac)
	for x in range(3):
		if x == 0:   s  =       mac[:4]
		elif x == 1: s += "." + mac[4:8]
		elif x == 2: s += "." + mac[8:]
	return s

# ------------------------------------------------------------------------------
try:
	from collections import MutableMapping
except:
	from collections.abc import MutableMapping

def flatten(d, parent_key='', sep='_'):
	"""flattens the dictionary

	Args:
		d (dict): input can be multi-nested dictionary.
		parent_key (str, optional): key from previous dictionary to be prefixed with current keys. Defaults to ''.
		sep (str, optional): keys separator. Defaults to '_'.

	Returns:
		dict, list: dictionary of lists if input is dictinoary,  list with input dictionary if input is anything else
	"""    	
	items = []
	if isinstance(d, dict):
		for k, v in d.items():
			new_key = parent_key + sep + k if parent_key else k
			if isinstance(v, MutableMapping):
				items.extend(flatten(v, new_key, sep=sep).items())
			else:
				items.append((new_key, v))
		return dict(items)
	else: return [d]

def dataframe_generate(d):
	"""convert dicationary to dataframe. multi-level dictionary will be converted flattened first 
	inorder to convert to DataFrame.

	Args:
		d (dict): input can be multi-nested dictionary.

	Returns:
		DataFrame: pandas DataFrame
	"""    	
	new_d = {}
	for k, v in d.items():
		new_d[k] = flatten(v, "")
	return pd.DataFrame(new_d).fillna("").T
# ------------------------------------------------------------------------------

def deprycation_warning(fn):
	print(f"{'-'*80}\nDEPRYCATION WARNING:\n{fn} usage is getting deprycated. kindly refer documentation for alternate option.\n{'-'*80}")

# ------------------------------------------------------------------------
def printmsg(pre=None, *, post=None, pre_ends="\n", justify_pre=True, justification_len=80):
	def outer(func):
		def inner(*args, **kwargs):
			if pre: 
				if justify_pre:
					print(pre.ljust(justification_len), end=pre_ends)
				else:
					print(pre, end=pre_ends)
			#
			fo = func(*args, **kwargs)
			#
			if post: 
				print(post)
			return fo
		return inner
	return outer

# ------------------------------------------------------------------------


def open_text_file(file):
	"""Open Text file in Notepad.exe

	Args:
		file (str): file name
	"""    	
	sp.Popen(["notepad.exe", file])

def open_excel_file(file):
	"""Open Excel file in MS-Excel (excel.exe)

	Args:
		file (str): file

	Raises:
		Exception: Raise exception if unable to open excel.
	"""    	
	try:
		sp.Popen(["C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE", file])
	except:
		try:
			sp.Popen(["C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE", file])
		except Exception as e:
			raise Exception(f"[-] Unable to Open file {file} in excel\n{e}")


def open_folder(folder):
	"""Open folder

	Args:
		file (str): file name
	"""    	
	path = os.path.realpath(folder)
	os.startfile(path)


#  =======


def abs_command_cisco(cmd):
	"""returns absolute full command for shorteened cmd

	Args:
		cmd (str): executed/ captured command ( can be trunked or full )

	Returns:
		str: cisco command - full untrunked
	"""
	spl_cmd = cmd.split()
	for c_cmd in CISCO_ABS_COMMANDS:
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

def abs_command_juniper(cmd):
	"""returns absolute truked command if any filter applied

	Args:
		cmd (str): executed/ captured command ( can be trunked or full )

	Returns:
		str: juniper command - trunked
	"""    	
	abs_cmd = cmd.split("|")[0].strip()
	for j_cmd in JUNIPER_ABS_COMMANDS:
		match = abs_cmd == j_cmd
		if match: return abs_cmd
	return cmd


# ==========================================================================================

@dataclass
class CapturesOut():
	"""Class define common methods and properties on captured output file.

	Args:
		capture_log_file (str): Output capture file

	Raises:
		Exception: _description_

	"""    	
	# capture_log_file: list[str] = field(default_factory=[])
	capture_log_file: str     #### To be verify earlier it was given list which seems a typo

	abs_cmd_function_map = {
		'Cisco': abs_command_cisco,
		'Juniper': abs_command_juniper,
	}
	abs_cmd_map = {
		'Cisco': CISCO_ABS_COMMANDS,
		'Juniper': JUNIPER_ABS_COMMANDS,
	}

	def __post_init__(self):
		self._read_capture_log_file()
		self._get_hostname_from_file_name()
		self._set_device_type()
		self._device_parameters()
		self._gen_output_list_dict()

	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	def cmd_output(self, cmd):
		"""provides filtered output of provided command

		Args:
			cmd (str): command string

		Returns:
			list: list of outout for provided command
		"""    		
		op_list = self._has(cmd)
		return op_list if op_list else []

	def has(self, cmd):
		"""Checks if outout has provided command output or not.

		Args:
			cmd (str): command string

		Returns:
			bool: True / False based on match.
		"""    		
		return self._has(cmd) != None

	@property
	def name(self):
		"""Returns device hostname from capture output.

		Returns:
			str: hostname of device
		"""    		
		return self.hostname

	@property
	def device_manufacturar(self):
		"""Returns device manufacturer from capture output.

		Returns:
			str: manufacturer of device
		"""    		
		return self.device_type

	# Absolute commands map 
	@property
	def abs_commands(self):
		"""Returns absolute commands

		Returns:
			dict: absolute command map
		"""		
		return self.abs_cmd_map[self.device_type]

	@property
	def outputs(self):
		"""returns dictionary of commands: output-list.

		Returns:
			dict: outputs splitted in dictionary by its command as key
		"""    		
		return self.output_list_dict


	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

	# read capture log file and store as full list
	def _read_capture_log_file(self):
		self.capture_log_list = read_file(self.capture_log_file)

	# extract hostname from list
	def _get_hostname_from_file_name(self):
		self.hostname = get_file_name(self.capture_log_file, ext=False)

	# extract device type from list
	def _set_device_type(self):
		self.device_type = detect_device_type(self.capture_log_list)

	# extract other device parameters from list
	def _device_parameters(self):
		if self.abs_cmd_function_map.get(self.device_type):
			self.abs_cmd_fn = self.abs_cmd_function_map[self.device_type] 
		else:
			raise Exception(f"[-] Invalid configuration, Unable to determine Device type. {self.device_type} for provided capture log file")

	# generate dictionary by outputs splitted by its command as key 
	def _gen_output_list_dict(self):
		toggle = 0
		self.output_list_dict, op_lst = {}, []
		for l in self.capture_log_list:
			if toggle and l.find(CMD_LINE_START_WITH)>0:
				self.output_list_dict[abs_cmd] = op_lst
				op_lst = []
				toggle=0
			#
			if l.find(CMD_LINE_START_WITH)>0:
				toggle = True
				if self.device_type == 'Juniper':
					cmd_line_trunked = l[l.find(CMD_LINE_START_WITH)+20:].split("|")[0].strip()
				else:
					cmd_line_trunked = l[l.find(CMD_LINE_START_WITH)+20:].strip()
				abs_cmd = self.abs_cmd_fn( cmd_line_trunked )
				continue
			#
			if toggle:
				op_lst.append(l.rstrip())
		if toggle:
			self.output_list_dict[abs_cmd] = op_lst
			
	# verify if output has provided command output or not.
	def _has(self, cmd):
		if self.device_type == 'Juniper':
			cmd = cmd.split("|")[0].strip()
		return self.output_list_dict.get(self.abs_cmd_fn(cmd))


# ==========================================================================================

		
