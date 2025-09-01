"""cisco var modifiers 
"""

import pandas as pd

from .commands.cmd_dict import *
from nettoolkit.facts_finder.modifiers.commons import *


# ================================================================================================
# Cisco  Var  DB
# ================================================================================================
class VarCisco(DataFrameInit, Var):
	"""Cisco  Var  Databse

	Args:
		capture (str): configuration capture file
		cmd_lst (list, optional): capture commands list . Defaults to None.

	Inherits:
		DataFrameInit (cls): DataFrameInit
		Var (cls): Var
	"""	
	
	def __init__(self, capture, cmd_lst=None):
		"""instance initializer

		"""		
		self.var = {}
		self.cmd_lst=cmd_lst
		if not self.cmd_lst:
			self.cmd_lst = cmd_lst_var
		super().__init__(capture)
		self.var_df = pd.DataFrame({"interface":[]})

	def __call__(self):
		self.update_device('show version')
		self.update_ipv6_hext2_3()
		self.convert_to_dataframe()

	## Calls

	def update_ipv6_hext2_3(self):
		"""updates the hextate 2 and hextate 3 value from an ipv6 interface.  
		first interface match will be considered.
		"""
		sht = 'show ipv6 interface brief'
		sht_df = self._is_sheet_data_available(self.dfd, sht)
		if sht_df is None or sht_df is False: return None
		#
		self.create_a_temp_v6_hext2_3_column(sht_df)
		tmp_hxb_list = [_ for _ in sht_df['temp'].dropna().drop_duplicates() if _ != ""]
		if len(tmp_hxb_list) > 0:
			hxb = tmp_hxb_list[0]
			self.update_var('hext2', hxb[0])
			self.update_var('hext3', hxb[1])


# ================================================================================================
