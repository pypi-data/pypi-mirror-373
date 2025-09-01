
import pandas as pd
from .general import *



# ----------------------------------------------------------------------------------------------------
# A single device cabling details.
# ----------------------------------------------------------------------------------------------------
class ADevCablings():
	"""A single Device Cabling details

	Args:
		self_device (str): device hostname (self)
	"""	

	def __init__(self, self_device, **kwargs):
		"""Object Initializer for A single device cabling details.
		"""		
		self.self_device = self_device
		self.cablings = {}
		self.cablings['a_device'] = []
		self.cablings['b_device'] = []
		self.cablings['aport'] = []
		self.cablings['bport'] = []
		self.cablings['a_media_type'] = []
		self.cablings['b_media_type'] = []
		self.cabling_mandatory_columns = set(self.cablings.keys())
		self.cabling_optional_columns = {'connector_type', 'color', 'weight', 'pattern',}
		self.connector_type, self.color, self.weight, self.pattern = DEFAULT_CONNECTOR_TYPE, DEFAULT_LINE_COLOR, DEFAULT_LINE_WT, DEFAULT_LINE_PATTERN 
		self.update_attrib(**kwargs)

	def update_attrib(self, **kwargs):
		"""update object attributes
		"""
		for k, v in kwargs.items():
			if v is not None:
				self.__dict__[k] = v

	def add_to_cablings(self, **kwargs):
		"""add provided keyword arguments to cablings (dictionary)
		"""
		mandatory_col_maps = {
			'b_device': 'nbr_hostname' ,
			'aport': 'interface',
			'bport': 'nbr_interface',
			'a_media_type': 'media_type',
		}
		#
		for k in self.cablings:
			if k == 'a_device':
				self.cablings[k].append(self.self_device)
			elif k in ( 'b_media_type'):
				self.cablings[k].append("")
			elif k in self.cabling_mandatory_columns:
				try:
					self.cablings[k].append(kwargs[mandatory_col_maps[k]])
				except:
					self.cablings[k].append("")
					if k != 'b_device' and k != 'a_media_type':
						print(f"[-] Mandatory requirement missing, df gen may fails {k}")

		for k in self.cabling_optional_columns:
			try:
				if k in kwargs:
					if k not in self.cablings:
						self.cablings[k] = []
					self.cablings[k].append(kwargs[k])
				# else set detaults ------
				elif k == 'connector_type':
					self.cablings[k].append(self.connector_type)
				elif k == 'color':
					self.cablings[k].append(self.color)
				elif k == 'weight':
					self.cablings[k].append(self.weight)
				elif k == 'pattern':
					self.cablings[k].append(self.pattern)
			except:
				if k not in self.cablings:
					self.cablings[k] = []
				self.cablings[k].append("")

	def cabling_dataframe(self):
		"""generate the dataframe for the cablings details captured in cablings dictionary of self.

		Returns:
			DataFrame: Pandas DataFrame object
		"""
		df =  pd.DataFrame(self.cablings)
		df = drop_empty(df, column='b_device')
		self.merged_df = df
		return df

# --------------------------------------------- 

