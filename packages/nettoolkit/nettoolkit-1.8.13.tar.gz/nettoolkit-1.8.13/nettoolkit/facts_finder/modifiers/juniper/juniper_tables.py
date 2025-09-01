"""Juniper table modifiers
"""

import pandas as pd

from nettoolkit.facts_finder.modifiers.commons import *
from .commands.cmd_dict import *
# ================================================================================================
# Functions for DataFrame Modification Apply
# ================================================================================================



# ================================================================================================
# Juniper Database Tables Object
# ================================================================================================
class TableInterfaceJuniper(DataFrameInit, TableInterfaces):
	"""Juniper Database Tables Object

	Args:
		capture (str): configuration capture log file
		cmd_lst (list): capture commands list

	Inherits:
		DataFrameInit (cls): DataFrameInit
		TableInterfaces (cls): TableInterfaces
	"""	

	def __init__(self, capture, cmd_lst):
		"""object initializer
		"""		
		self.cmd_lst=cmd_lst
		if not self.cmd_lst:
			self.cmd_lst = cmd_lst_int
		super().__init__(capture)

	def __call__(self):
		self.merge_interface_data()
		self.remove_duplicates()

	## Calls

	def merge_interface_data(self):
		"""merges interface related data frames from the parsed excel sheet command output 
		which was originated from capture_it along with ntctemplate.
		A single pandas dataframe clubbed with all interface related details. 
		"""
		pdf = pd.DataFrame({'interface':[]})
		for sheet, df in self.dfd.items():
			if sheet not in self.cmd_lst: continue
			if sheet == "show lldp neighbors":
				df.rename(columns={'local_interface': 'interface', })
			ndf = df[ self.cmd_lst[sheet].keys() ]
			ndf = ndf.rename(columns=self.cmd_lst[sheet])
			# ndf['interface'] = ndf['interface'].apply(lambda x: standardize_if(x, True))
			pdf = pd.merge( ndf, pdf, on=['interface',], how='outer').fillna("")
		self.pdf = pdf

	def remove_duplicates(self):
		"""drop a few duplicate columns
		"""
		drop_cols = {
			'//subnet', '//subnet1', '//nbr_hostname', 
		}
		for c in drop_cols:
			try:
				self.pdf.drop([c], axis=1, inplace=True)
			except:
				pass


# ================================================================================================
