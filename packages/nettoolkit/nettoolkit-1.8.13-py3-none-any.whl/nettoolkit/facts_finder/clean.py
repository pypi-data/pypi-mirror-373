"""Device Facts cleanup
"""


import os
from nettoolkit.nettoolkit_common import *
from nettoolkit.nettoolkit_db import *
from nettoolkit.pyJuniper import *
from pathlib import *

from .generators import FactsGen
from .generators.cisco_parser import get_op_cisco
from .mergers import CiscoMerge, JuniperMerge
from .inputlog import to_cit

# ========================================================================================

class CleanFacts:
	"""cleans the captured parsed file and writes out the modified facts in new clean file
	using additional information provided from capture log file.
	Also can get a few additional properties to process futher. A new clean file will be 
	generated upon instance calling.

	Args:
		capture_log_file (str): configuration capture log file name
		capture_parsed_file (str): configuration parsed excel file name
		convert_to_cit(bool, optional): convert normal capture log file to capture_it output format (useful if capture was taken manually). Defaults to False.
		remove_cit_bkp(bool, optional): remove duplicated log file (capture_it output format). Defaults to True.
		skip_txtfsm(bool, optional): skip evaluation of capture excel file (textfsm parsed file), and use native facts-finder parsers. Defaults to False.
		new_suffix (str, optional): file suffix. Defaults to '-clean'.
		use_cdp (bool, optional): use cdp neighbor (overrides lldp neighbor) . Defaults to False.
		debug (bool, optional): for trouble shooting purpose only. Defaults to False.

	"""

	def __init__(self,
		capture_log_file, 
		capture_parsed_file=None,
		convert_to_cit=False,
		remove_cit_bkp=True,
		skip_txtfsm=False,
		new_suffix='-clean',
		use_cdp=False,
		debug=False,
		output_folder=".",
		):
		"""Instance Initializer
		"""		
		self.capture_log_file = capture_log_file
		self.capture_parsed_file = capture_parsed_file
		self.convert_to_cit = convert_to_cit
		self.remove_cit_bkp = remove_cit_bkp
		self.skip_txtfsm = skip_txtfsm
		self.new_suffix = new_suffix
		self.use_cdp = use_cdp
		self.debug = debug
		self.output_folder = output_folder
		try:
			if convert_to_cit: 
				self.capture_log_file = to_cit(self.capture_log_file)
		except Exception as e:
			print(f'[-] log file convert to Capture-it failed..\n{e}')
		#
		self._clean_file = get_clean_filename(self.output_folder, self.capture_log_file, self.new_suffix)
		if debug:
			self._fg_data_file = get_clean_filename(self.output_folder, self.capture_log_file, "-fg")
			self._fm_data_file = get_clean_filename(self.output_folder, self.capture_log_file, "-fm")

	def __call__(self):
		self.get_facts_gen()
		self.set_config()
		if not self.skip_txtfsm:
			self.call(self.merge_class())
		remove_file(self.clean_file)
		if self.skip_txtfsm:
			write_to_xl(self.clean_file, self.Fg.df_dict, overwrite=True, index=True)
		else:
			write_to_xl(self.clean_file, self.Mc.merged_dict, overwrite=True)
			if self.debug:
				write_to_xl(self._fg_data_file, self.Mc.fg_merged_dict, overwrite=True)
				write_to_xl(self._fm_data_file, self.Mc.pdf_dict, overwrite=True)
		self.remove_bkp_log()

	def get_facts_gen(self):
		"""gets Facts from generators 
		"""
		self.Fg = FactsGen(self.capture_log_file)
		self.Fg.verify_capture_existance()
		self.Fg()

	def set_config(self):
		"""set the appropriate configuration for device types.

		Raises:
			Exception: undetected device type
		"""		
		if self.Fg.dev_type == 'cisco':
			self._config = cisco_config(self.capture_log_file)
		elif self.Fg.dev_type == 'juniper':
			self._config = juniper_config(self.capture_log_file)
		else:
			raise Exception(f"[-] undetected device type {self.Fg.dev_type}, cannot proceed")

	def merge_class(self):
		""" returns Modifier Merge Class from the generated Facts 
		"""
		if self.Fg.dev_type == 'cisco':
			MergeClass = CiscoMerge
		elif self.Fg.dev_type == 'juniper':
			MergeClass = JuniperMerge
		else:
			raise Exception(f"[-] undetected device type {self.Fg.dev_type}, cannot proceed")
		return MergeClass

	def call(self, MergeClass):
		""" calls the modifier merge class 

		Args:
			MergeClass (cls): MergeClass
		"""		
		self.Mc = MergeClass(self.Fg, self.capture_parsed_file, self.use_cdp)
		self.Mc()

	@property
	def clean_file(self):
		"""new output clean filename 
		"""
		return self._clean_file

	@property
	def hostname(self):
		"""device hostname
		"""
		try:
			return self.Mc.hostname
		except:
			return get_hostname_from_logfile(self.capture_log_file)

	@property
	def config(self):
		"""device configuration.  for cisco show running, for juniper show configuration - set output
		"""
		return self._config

	@property
	def dev_type(self):
		"""device type string either(cisco/juniper)
		"""
		return self.Fg.dev_type		

	def remove_bkp_log(self):
		"""removes the backup file created during normal caprure read
		"""    		
		if self.remove_cit_bkp and self.convert_to_cit:
			try:
				os.remove(f'{self.capture_log_file[:-4]}-bkp.log')
			except FileNotFoundError:
				pass
			except Exception as e:
				if not self.Fg.dev_type == 'juniper':
					print(f"[-] Error Removing duplicate file\n{e}")



# ========================================================================================

def get_clean_filename(path, file, suffix):
	"""get a new clened filename appended with suffix string

	Args:
		path (str): full path with output file name
		file (str): capture file name
		suffix (str): suffix to be appened

	Returns:
		str: updated file name
	"""	
	p = Path(file)
	filename_wo_ext = str(p.stem)
	file_ext = ".xlsx"
	if not path or path == ".":
		folder = str(p.resolve().parents[0])
	else:
		folder = path
	return folder+"/"+filename_wo_ext+suffix+file_ext

def get_hostname_from_logfile(file):
	"""get device hostname from log file name

	Args:
		file (str): full path with output file name

	Returns:
		str: updated file name
	"""	
	return str(Path(file).stem)

def remove_file(xl):
	"""try to delete file if available, skip else

	Args:
		xl (str): file to be deleted
	"""	
	try: os.remove(xl)			# remove old file if any
	except: pass


def cisco_config(capture_log_file):
	"""returns cisco running configuration 

	Args:
		capture_log_file (str): device captured log 

	Returns:
		list: configuration output in list
	"""	
	config = get_op_cisco(capture_log_file, 'show running-config')
	return config


def juniper_config(capture_log_file):
	"""returns juniper configuration in set commnand output format

	Args:
		capture_log_file (str): device captured log 

	Returns:
		list: configuration output in list
	"""	
	cmd_op = get_op(capture_log_file, 'show configuration')
	JS = JSet(input_list=cmd_op)
	JS.to_set
	config = verifid_output(JS.output)
	return config

# ========================================================================================
