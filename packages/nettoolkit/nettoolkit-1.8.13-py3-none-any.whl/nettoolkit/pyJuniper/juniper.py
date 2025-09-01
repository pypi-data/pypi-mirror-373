
# ------------------------------------------------------------------------------
from dataclasses import dataclass, field
from nettoolkit.nettoolkit_common.gpl import STR, IO
import os
from .hierarchy import Hierarchy 
from .jset import JSet
# ------------------------------------------------------------------------------

@dataclass
class Juniper():
	"""Juniper configuration file related class

	Args:
		input_file (str): _description_
		output_file (str, optional): output file name. Defaults to None.
	"""    	
	input_file: str
	output_file: str = ''

	def _set_output_file(self, filt):
		_spl = self.input_file.split(".")
		if not self.output_file:
			self.output_file = ".".join(_spl[:-1]) + filt + _spl[-1]
		self.conversion_log_file = ".".join(_spl[:-1]) + '-conversion_log.log'

	def _get_clean_output_file_lst(self):
		output_file_lst = []
		for line in self.input_file_lst:
			if len(line.lstrip()) > 0:
				if line.lstrip()[0] == "#": continue
				output_file_lst.append(line.rstrip("\n"))
		return output_file_lst

	def remove_remarks(self, to_file=True, config_only=True):
		"""remove all remark lines from config

		Args:
			to_file (bool, optional): save output to file if True. Defaults to True.

		Returns:
			lst: list of output
		"""    		
		self._set_output_file("-remark.")

		if config_only:
			J = JSet(self.input_file)
			output_file_lst = J.remove_remarks_from_config()
		else:
			self.input_file_lst = IO.file_to_list(self.input_file)
			output_file_lst = self._get_clean_output_file_lst()

		if to_file:
			IO.to_file(self.output_file, output_file_lst)
		return output_file_lst

	def convert_to_set(self, to_file=True, conversion_log_file=False):
		"""convert configuration to set mode

		Args:
			to_file (bool, optional): save output to file if True. Defaults to True.

		Returns:
			lst: list of output
		"""    		
		self._set_output_file("-set.")
		J = JSet(self.input_file)
		J()
		if to_file:
			IO.to_file(self.output_file, J.output)
		if conversion_log_file:
			IO.to_file(self.conversion_log_file, J.conversion_log)
		return J.output

	def convert_to_hierarchy(self, to_file=True):
		"""convert set configuration to hiearchical configuration

		Args:
			to_file (bool, optional): save output to file if True. Defaults to True.

		Returns:
			lst: list of output
		"""    		
		H = Hierarchy(self.input_file, self.output_file)
		H.convert()
		if to_file and self.output_file:
			IO.to_file(self.output_file, H.output)
		return H.output


def convert_to_set_from_captures(conf_file, output_file=None):
	"""jset conversion, 

	Args:
		conf_file (str): configuration capture file, using capture-it
		output_file (str, optional): output file name. Defaults to None.

	Returns:
		list: list of set commands configuration.
	"""	
	J = Juniper(conf_file, output_file)
	set_list = J.convert_to_set(to_file=output_file)
	return set_list

# ------------------------------------------------------------------------------
if __name__ == '__main__':
	pass
# ------------------------------------------------------------------------------
