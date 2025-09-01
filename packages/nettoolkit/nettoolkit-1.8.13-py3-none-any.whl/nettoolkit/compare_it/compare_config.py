
# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from nettoolkit.facts_finder.generators.cisco_parser import CMD_LINE_START_WITH
from nettoolkit.compare_it import CompareText, get_string_diffs
from nettoolkit.nettoolkit_common import IO


# ----------------------------------------------------------------------------------
# Internal Common Functions
# ----------------------------------------------------------------------------------

def is_captureit_config(lines):
	capture_it_config = False
	for _ in lines:
		if _[2:].startswith(CMD_LINE_START_WITH):
			capture_it_config = True	
			break
	return capture_it_config

def get_config_type(lines):
	for _ in lines:
		if _.startswith("#"): return 'juniper_junos'
		if _.startswith("!"): return 'cisco_ios'
	return None

def get_configuration(file):
	with open(file, 'r') as f:
		lines = f.readlines()
	if not lines: 
		print(f"Missing config for {file}")
		quit()
	capture_it_config = is_captureit_config(lines)
	if not capture_it_config: 
		print("Non capture it captures not supported for now..")
		quit()
	#
	config_type = get_config_type(lines)
	cmd_starter = 'show running-config' if config_type == 'cisco_ios' else 'show configuration'
	config_start = False
	config = []
	for line in lines:
		if line[2:].startswith(CMD_LINE_START_WITH + cmd_starter ):
			config_start = True
			continue
		if config_start and line[2:].startswith(CMD_LINE_START_WITH): break
		if not config_start: continue
		config.append(line)
	config = [_.rstrip() for _ in config ]	
	return config


# ----------------------------------------------------------------------------------
# Main Config comarator class
# ----------------------------------------------------------------------------------
class CompareConfig():

	def __init__(self, file1, file2):
		self.file1 = file1
		self.file2 = file2


	def get_config(self):
		self.config1 = get_configuration(self.file1)
		self.config2 = get_configuration(self.file2)
		self.tmp1 = IO.to_file(self.file1+'.tmp', self.config1)
		self.tmp2 = IO.to_file(self.file2+'.tmp', self.config2)

	def get_differeces(self, on_screen_display=False):
		diff_files = self.file1 + ' v/s ' + self.file2

		# Define output headers
		header = f"\n# {'-'*80} #\n" + f"#  Difference : [{diff_files}]" + f"\n# {'-'*80} #\n"
		removal_header = f"\n# {'- '*20} #\n" + f"# {' '*15} REMOVALS"  + f"\n# {'- '*20} #\n"
		addition_header = f"\n# {'+ '*20} #\n" + f"# {' '*15} ADDITIONS" + f"\n# {'+ '*20} #\n"

		# Compare two files for adds/removals usng "CompareText"
		diff = {}
		removals = CompareText(self.tmp1, self.tmp2, "- ")
		adds = CompareText(self.tmp2, self.tmp1, "+ ")
		diff[removal_header] = removals.CTObj.diff
		diff[addition_header] = adds.CTObj.diff

		# Convert  dictionary to string format using "get_string_diffs"
		self.diff_str = get_string_diffs(diff, header=header)
		if on_screen_display:
			print("".join(self.diff_str))

		return self.diff_str		

	def write_diff(self, file):
		IO.to_file(file, self.diff_str)

# ----------------------------------------------------------------------------------
