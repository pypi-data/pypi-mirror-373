
from collections import OrderedDict
from nettoolkit.nettoolkit_common import *


from .cisco_parser import *
from .juniper_parser import *

merge_dict = DIC.merge_dict

class DeviceDB():
	"""class defining collection of devices database
	"""    	

	def __init__(self):
		"""initialize object by creating a blank database
		"""    		
		self.config = OrderedDict()

	def __getitem__(self, k): return self.config[k]
	def __setitem__(self, k, v): self.config[k] = v
	def __iter__(self):
		for k, v in self.config.items(): yield k,v
	def keys(self): 
		"""keys, sections of configuration

		Returns:
			list: list of keys/sections
		"""		
		return self.config.keys()

	def evaluate(self, device):
		"""evaluate for each command, and update hierarcy for each parsed output
		and converts dictionary to dataframe.

		Args:
			device (Cisco, Juniper): Cisco or Juniper objects from parsers

		Returns:
			DataFrame: DataFrame with all parsed output
		"""    		
		cl_hl = get_cmd_hierachylevels(device)
		cmds_list = cl_hl['cmds_list']
		hierachy_levels = cl_hl['hierachy_levels']
		for cmd, kwargs in cmds_list.items():
			parsed_op = device.parse(cmd, self, **kwargs)
			if isinstance(hierachy_levels[cmd], str):
				self.update_hierarcy(hierachy_levels[cmd], parsed_op)
			elif isinstance(hierachy_levels[cmd], tuple):
				for i, hierachy_level in enumerate(hierachy_levels[cmd]):
					self.update_hierarcy(hierachy_level, parsed_op[i])
		return self.convert_dict_to_df()

	def update_hierarcy(self, hierarchy, content=None):
		"""update the content to device config at given hierarcy/level

		Args:
			hierarchy (hashable): hierarchy where content to be updated
			content (dict, optional): details to be updated. Defaults to None.

		Returns:
			dict: merged dictionary by adding the content at given hierarchy level
		"""    		
		if not content: return None
		if not self.config.get(hierarchy):
			self[hierarchy] = OrderedDict()
		merge_dict(self.config[hierarchy], content)

	def convert_dict_to_df(self):
		"""convert the dictionary to dataframe

		Returns:
			dict: dictionary of dataframe
		"""    		
		df_dict = {}
		for k, v in self:
			df = dataframe_generate(v)
			df.index.name = k
			df_dict[k] = df
		return df_dict


def device(file):
	"""get the device dynamically based on captured file.

	Args:
		file (file): captured file

	Raises:
		TypeError: unrecognized file type will throw exception

	Returns:
		Cisco, Juniper: detected Cisco or Juniper objects from parsers
	"""    	
	dev_manu = get_device_manufacturar(file)
	if dev_manu == "Cisco":  return Cisco(file)
	if dev_manu == "Juniper": return Juniper(file)
	raise TypeError("[-] Device configuration Unidentified, please re-check")

def get_cmd_hierachylevels(device):
	"""get the dictionary of hierarcy levels  and commands list based on device type

	Args:
		device (Cisco, Juniper): Cisco or Juniper objects from parsers

	Raises:
		TypeError: unrecognized device type will throw exception

	Returns:
		dict: dictionary of hierarcy levels  and commands list
	"""    	
	if isinstance(device, Cisco):
		cmds_list = cisco_cmds_list
		hierachy_levels = cisco_cmds_op_hierachy_level
	elif isinstance(device, Juniper):
		cmds_list = juniper_cmds_list
		hierachy_levels = juniper_cmds_op_hierachy_level
	else:
		raise TypeError("[-] Device configuration Unidentified, please re-check")
	return {'cmds_list': cmds_list, 'hierachy_levels': hierachy_levels}

