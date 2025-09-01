"""Boiler plate code for the facts generation.
fg_dict: attribute will provide the output dictionary with pandas dataframe as values to be readily available to write it to excel.
dev_type: attribute returns the device type of configuraton provided
"""

from .merger import device, DeviceDB, get_cmd_hierachylevels
from .cisco_parser import Cisco, cisco_commands_parser_map
from .juniper_parser import Juniper, juniper_commands_parser_map
from .cisco_parser import absolute_command as cisco_absolute_command
from .juniper_parser import absolute_command as juniper_absolute_command
from nettoolkit.facts_finder.commons.common import generate_int_number
# ==============================================================================


class FactsGen:
	"""Facts Generator class (boiler plate code)

	Args:
		capture_file (str): configuration capture file
	"""	

	def __init__(self, capture_file):
		"""object initializer
		"""		
		self.capture_file = capture_file

	def __call__(self):
		device_database = DeviceDB()    				 # create a new device database object
		df_dict = device_database.evaluate(self.model)   # evaluate object by providing necessary model, and return dictionary	
		df_dict['var'] = df_dict['var'].reset_index().rename(columns={0:'default'})
		self.reset_interfaces_index(df_dict)
		generate_int_number(df_dict['Interfaces'])
		self.split_interfaces(df_dict)
		self.df_dict = df_dict
		return df_dict

	def __iter__(self):
		for k, v in self.fg_dict.items():
			yield (k, v)

	def __getitem__(self, key):
		return self.fg_dict[key]

	@property
	def dev_type(self):
		"""detected device type for the given configuration capture

		Raises:
			Exception: for Invalid device type
			Exception: for Missing FactsGen call

		Returns:
			str: returns device type in string
		"""		
		try:
			if isinstance(self.model, Cisco):
				return 'cisco'
			elif isinstance(self.model, Juniper):
				return 'juniper'
			else:
				raise Exception(f'[-] Invalid device type ``{type(self.model)}``. verify config')
		except Exception as e:
			raise Exception(f"[-] FactsGen needs to be called in order to get the device type."
				f"\n\tEither it is not called or invalid config present in device capture."
				f"\n\t{e}")

	@property
	def fg_dict(self):
		"""facts generator dictionary

		Returns:
			dict: dataframe dictionary
		"""
		return self.df_dict

	def verify_capture_existance(self):
		"""verifications of all mandatory commands existance in output
		"""		
		self.model = device(self.capture_file)           # select the model based on input file
		self.model.verify()

	def reset_interfaces_index(self, df_dict):
		"""reset Interfaces to interface and remove it from index 

		Args:
			df_dict (dict): dataframe dictionary
		"""		
		df_dict['Interfaces'] = df_dict['Interfaces'].reset_index()
		df_dict['Interfaces'].rename(columns={'Interfaces': 'interface'}, inplace=True)				## update column name to match key/index between two dataframes. 


	def split_interfaces(self, df_dict):
		"""splits different types of interfaces

		Args:
			df_dict (dict): dataframe dictionary
		"""		
		int_types = set(df_dict['Interfaces']['filter'])
		for int_type in int_types:
			df = df_dict['Interfaces']
			df_dict[int_type] = df[df['filter'] == int_type]
		del(df_dict['Interfaces'])


# ==============================================================================


def get_necessary_cmds(dev_type):
	"""retrive necessary/mandatory commands for the given device type (cisco_ios, juniper_junos)

	Args:
		dev_type (str): device type

	Returns:
		set: set of mandatory commands
	"""	
	if dev_type == 'cisco_ios':
		necessary_cmds = set(cisco_commands_parser_map.keys())
	elif dev_type == 'juniper_junos':
		necessary_cmds = set(juniper_commands_parser_map.keys())
	## 
	## add more as need
	else:
		necessary_cmds = set()
	return necessary_cmds


def get_absolute_command(dev_type, cmd):
	"""retrive absolute command for given command of device type.

	Args:
		dev_type (str): device type (cisco_ios, juniper_junos)
		cmd (str): full/shortened command

	Returns:
		str: full length absolute command
	"""	
	if dev_type == 'cisco_ios':
		abs_cmd = cisco_absolute_command(cmd, cisco_commands_parser_map)
	elif dev_type == 'juniper_junos':
		abs_cmd = juniper_absolute_command(cmd, juniper_commands_parser_map)
	## add more as need
	else:
		abs_cmd = cmd 
	return abs_cmd
