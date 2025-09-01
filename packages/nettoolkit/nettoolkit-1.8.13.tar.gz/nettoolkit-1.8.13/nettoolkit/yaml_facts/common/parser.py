"""Description: 
"""

# ==============================================================================================
#  Imports
# ==============================================================================================
from dataclasses import dataclass, field
from pathlib import Path
import sys, os
import textfsm
from nettoolkit.nettoolkit_common import get_file_name, get_file_path, DIC
from nettoolkit.nettoolkit_db import dict_to_yaml

merge_dict = DIC.merge_dict

# ==============================================================================================
#  Local Statics
# ==============================================================================================


# ==============================================================================================
#  Local Functions
# ==============================================================================================
def parse_to_list_cmd(abs_cmd, data_list, cmd_parser_file_map):
	"""parse the output 

	Args:
		abs_cmd (str): absolute command
		data_list (list): list of output
		cmd_parser_file_map (dict): command parser map

	Returns:
		list: parsed data in list format
	"""    	
	template_file = get_template_file(abs_cmd, cmd_parser_file_map)
	return parse_to_list(template_file, data_list)

def parse_to_dict_cmd(abs_cmd, data_list, cmd_parser_file_map):
	"""parse the output 

	Args:
		abs_cmd (str): absolute command
		data_list (list): list of output
		cmd_parser_file_map (dict): command parser map

	Returns:
		list: parsed data in dictionary format
	"""    	
	template_file = get_template_file(abs_cmd, cmd_parser_file_map)
	return parse_to_dict(template_file, data_list)

def parse_to_list(template_file, data_list):
	"""Parse the data_list using template file. And returns data as list

	Args:
		template_file (str): template file
		data_list (list): output in list formate

	Returns:
		list: parsed data in list format
	"""    	
	data = "\n".join(data_list)
	with open(template_file) as f:
		textfsm_parser = textfsm.TextFSM(f)
		parsed_data = textfsm_parser.ParseText(data)
	return parsed_data

def parse_to_dict(template_file, data_list):
	"""Parse the data_list using template file. And returns data as dictionary

	Args:
		template_file (str): template file
		data_list (list): output in list formate

	Returns:
		dict: parsed data in dictionary format
	"""    	
	data = "\n".join(data_list)
	with open(template_file) as f:
		textfsm_parser = textfsm.TextFSM(f)
		parsed_data = textfsm_parser.ParseTextToDicts(data)
	return parsed_data



def get_template_dir(template_path):
	"""returns template directory

	Args:
		template_path (str): source of template path

	Returns:
		Path: Path where templates are stored.
	"""    	
	folder = ""
	for path in sys.path:
		p = Path(path)
		if not p.is_dir(): continue
		if p.name == "site-packages" :
			folder = p
			break
	if not folder:
		print(f"[-] Could not locate ntc template directory...")
	# template_dir = os.path.join(p, "templates")
	template_dir = p.resolve().parents[0].joinpath(template_path)
	return template_dir

def get_template_file(abs_cmd, cmd_parser_file_map):
	"""returns template file with full path for provided command.

	Args:
		abs_cmd (str): absolute command
		cmd_parser_file_map (dict): parser map to select the template file based on absolute command

	Raises:
		Exception: if template file not found or unable to read template.

	Returns:
		str: template file
	"""    	
	if not cmd_parser_file_map.get(abs_cmd): return ""
	#
	file = get_ntc_template_file(abs_cmd, cmd_parser_file_map)
	if is_exist(file): 
		return file
	#
	file = get_self_template_file(abs_cmd, cmd_parser_file_map)
	if is_exist(file): 
		return file
	else:
		raise Exception(f"[-] Unable to read file {file}, check file does exist..")

def get_ntc_template_file(abs_cmd, cmd_parser_file_map):
	"""returns ntc template file.

	Args:
		abs_cmd (str): absolute command
		cmd_parser_file_map (dict): parser map to select the template file based on absolute command

	Returns:
		str: template file
	"""    	
	p = get_template_dir("site-packages/ntc_templates/templates")
	return str(p.joinpath(cmd_parser_file_map[abs_cmd]))

def get_self_template_file(abs_cmd, cmd_parser_file_map):
	"""returns nettoolkit template file.

	Args:
		abs_cmd (str): absolute command
		cmd_parser_file_map (dict): parser map to select the template file based on absolute command

	Returns:
		str: template file
	"""    	
	p = get_template_dir("site-packages/nettoolkit/yaml_facts/templates")
	return str(p.joinpath(cmd_parser_file_map[abs_cmd]))

def is_exist(file):
	"""check if template file exist or not

	Args:
		file (str): file name with full path

	Returns:
		bool: True if found else False
	"""    	
	try:
		with open(file, 'r') as f: pass
		return True
	except:
		return False

# ==============================================================================================
#  Classes
# ==============================================================================================
@dataclass
class CommonParser():
	"""Common parser methods class. Provide captures, and output_folder to begin.

	Raises:
		Exception: for invalid inputs
	"""    	
	captures: any
	output_folder: str=''

	def __post_init__(self):
		self.device_dict = {}
		self.parse()
		self.set_output_yaml_filename()
		self.write_yaml()

	@property
	def output_yaml(self):
		"""output yaml file name with full path

		Returns:
			str: yaml output file
		"""    		
		return self._yaml_file

	# sets output yaml file name
	def set_output_yaml_filename(self):
		try:
			if not self.output_folder:
				self.output_folder = get_file_path(self.captures.capture_log_file)
			else:
				self.output_folder = Path(self.output_folder)
			hostname = get_file_name(self.captures.capture_log_file)
			self._yaml_file = self.output_folder.joinpath(hostname + ".yaml")
		except:
			raise Exception(f"[-] Error determining output yaml file, either input is invalid.")

	# writes out yaml file (owerright)
	def write_yaml(self):
		dict_to_yaml(self.device_dict, file=self.output_yaml, mode='w')

	# start parsing the outputs
	def parse(self):
		self.unavailable_cmds = set()
		for cmd, funcs in self.cmd_fn_parser_map.items():
			cmd_output = self.captures.cmd_output(cmd)
			if not cmd_output:
				self.unavailable_cmds.add(cmd) 
				continue
			for fn in funcs:
				self.parse_func(fn, cmd_output)

	# parse a command output using a single function
	def parse_func(self, fn, cmd_output):
		parsed_fields = fn(cmd_output)
		self.add_parsed_fields_to_device_dict(parsed_fields)

	# merge parsed field with device dictionary
	def add_parsed_fields_to_device_dict(self, parsed_fields):
		merge_dict(self.device_dict, parsed_fields)


# ==============================================================================================
#  Main
# ==============================================================================================
if __name__ == '__main__':
	pass

# ==============================================================================================
