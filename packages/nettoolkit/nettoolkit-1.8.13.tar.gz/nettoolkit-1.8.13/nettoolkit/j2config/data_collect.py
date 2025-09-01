

import pandas as pd
from abc import ABC, abstractmethod

# ---------------------------------------------------------

def read_worksheet(file, wks):
	"""read an excel worksheet 


	Args:
		file (str): excel file name
		wks (str): worksheet name

	Raises:
		Exception: Raised for file read fail, or worksheet missing

	Returns:
		DataFrame: Pandas DataFrame Object
	"""	
	try:
		df = pd.read_excel(file, sheet_name=wks).fillna("")
	except:
		raise Exception(f"[-] CRITICAL: {file} File Read failed. Expected Worksheet named '{wks}' missing")
	return df

def read_excel(file):
	"""read excel file, all worksheet

	Args:
		file (str): excel file name

	Returns:
		dict: dictionary of dataframes.
	"""	
	dfd = pd.read_excel(file, None)
	for k,v in dfd.items():
		dfd[k] = v.fillna("")
	return dfd

def to_int(item):
	"""try to converts item to integer

	Args:
		item (str): input string

	Returns:
		int, str: returns integer value if it is number, else same as input string
	"""	
	try:
		return int(item)
	except:
		return item


class DeviceDetails():
	""" Device details operations

	Args:
		device_file (str): Excel device database file 

	Raises:
		Exception: Raised for input error: if device filename missing
		Exception: Raised for input error: if provided device file missing or read fails.

	Returns:
		DeviceDetails: DeviceDetails object
	"""	

	def __init__(self, device_file):
		"""instance initializer
		"""		
		self.device_filename = device_file
		self.verify_input_dev_file()

	def verify_input_dev_file(self):
		"""check if provided input device file 

		Raises:
			Exception: Raised for input error: if device filename missing
			Exception: Raised for input error: if provided device file missing or read fails.
		"""		
		if not self.device_filename:
			raise Exception(f'[-] input error: input device file name {self.device_filename}')
		try:
			self.dev_details = self.read_device()								## require		
		except Exception as e:
			raise Exception(f'[-] input error: input device file either missing or missing with necessary sheets\n{e}')

	def read_device(self):
		"""reads device database

		Returns:
			dict: dictionary of dataframe
		"""		
		dr = {'var':{}, 'table':None}
		dr['var']['device'] = read_worksheet(self.device_filename, 'var') 		
		dr['table'] = self.merged_table_columns()
		self.device_details = dr['var']['device']
		return dr

	def merged_table_columns(self):
		"""merges all different type of interfaces/protocols details in to a single dataframe.

		Returns:
			DataFrame: Pandas DataFrame object collecting all interfaces/protocols details 
		"""		
		dfd = read_excel(self.device_filename)
		del(dfd['var'])
		df_table = pd.DataFrame({'key':[]})
		for k, df in dfd.items():
			df_table = pd.concat([df_table, df], ignore_index=True).fillna("")
		for c in df_table:
			try:		
				df_table[c] = df_table[c].apply(to_int)
				df_table[c] = df_table[c].apply(str)
			except:
				pass
		return df_table

	def merge_with_var_frames(self, regional_frames):
		"""merge device var details with provided custom regional DataFrame(s) 
		custom regional frame variables/values  overrides device var variables/values.

		Args:
			regional_frames (list): list of custom regional DataFrames to be added to var.
		"""		
		frames = [self.device_details,]
		if regional_frames:
			frames.extend(regional_frames)
		self.var = self.merge_vars(frames)

	def read_table(self):
		"""reads table dataframe and add var/table to dataframe dictionary
		"""
		self.table = self.dev_details['table'].T.to_dict()
		self.data = {'var': self.var, 'table': self.table}

	def merge_vars(self, frames):
		"""merges var details from two different dataframes ( region and device - databases )
		(support definition)

		Args:
			frames (list): list of DataFrame(s) to be merged

		Returns:
			DataFrame: merged DataFrame (`var`)
		"""		
		return pd.concat(frames, ignore_index=True).set_index('var').to_dict()['default']



# --------------------------------------------------------------------------------------------------------
# Regional DataFrame input template class
# --------------------------------------------------------------------------------------------------------

class ABSRegion(ABC):
	"""Abstract Base Class Template to define custom/regional dataframe

	Args:
		device_details (DataFrame): Pandas DataFrame with device `var` information
		custom_data_file (str): custom datafile.

	Inherits:
		ABC (ABC): abstract base class

	Abstract Properties:
		frames(list) : must be defined in custom class method, which should return a list of DataFrame(s) to override `var` attributes. 


	"""	

	def __init__(self, device_details, custom_data_file):
		"""instance initializer

		"""		
		self.device_details = device_details
		self.custom_data_file = custom_data_file

	@property
	@abstractmethod
	def frames(self):
		"""must be defined in custom class method, which should return a list of DataFrame(s) to override `var` attributes. 
		"""		
		pass
