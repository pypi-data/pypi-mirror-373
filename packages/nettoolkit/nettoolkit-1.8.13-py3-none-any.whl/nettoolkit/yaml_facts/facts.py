"""Description: 
"""
from pprint import pprint
# ==============================================================================================
#  Imports
# ==============================================================================================
from dataclasses import dataclass, field
from nettoolkit.nettoolkit_common import CapturesOut
from nettoolkit.facts_finder.inputlog import to_cit
from nettoolkit.yaml_facts.cisco import CiscoParser
from nettoolkit.yaml_facts.juniper import JuniperParser

# ==============================================================================================
#  Local Statics
# ==============================================================================================



# ==============================================================================================
#  Local Functions
# ==============================================================================================



# ==============================================================================================
#  Classes
# ==============================================================================================

@dataclass
class YamlFacts():
	"""Base class generates the yaml facts file from provided capture_log_file at given output_folder.
	"""    	
	capture_log_file: str
	output_folder: str=''

	parser_cls_map = {
		'Cisco': CiscoParser,
		'Juniper': JuniperParser,
	}

	def __post_init__(self):
		self.capture_log_file = to_cit(self.capture_log_file)
		self.captures = CapturesOut(self.capture_log_file)
		self.CP = self.parser_cls_map[self.captures.device_manufacturar](self.captures, self.output_folder)
		self.unavailable_cmds = self.CP.unavailable_cmds



# ==============================================================================================
#  Main
# ==============================================================================================
if __name__ == '__main__':
	pass
# ==============================================================================================
