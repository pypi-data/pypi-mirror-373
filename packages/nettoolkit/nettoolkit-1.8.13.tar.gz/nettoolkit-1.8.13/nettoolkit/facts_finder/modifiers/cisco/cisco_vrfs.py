"""cisco vrf table modifiers 
"""

import pandas as pd

from .commands.cmd_dict import *
from nettoolkit.facts_finder.modifiers.commons import *

# ================================================================================================
# Functions for DataFrame Modification Apply
# ================================================================================================



# ================================================================================================
# Cisco Database VRF Object
# ================================================================================================
class TableVrfsCisco(DataFrameInit, TableVrfs):
	"""Cisco Database VRF Object

	Args:
		capture (str): configuration capture file
		cmd_lst (list, optional): capture commands list . Defaults to None.

	"""	
	
	def __init__(self, capture, cmd_lst=None):
		self.cmd_lst=cmd_lst
		if not self.cmd_lst:
			self.cmd_lst = cmd_lst_vrf
		super().__init__(capture)
		self.vrf_df = pd.DataFrame({"interface":[]})

	def __call__(self):
		sht = 'show vrf'
		sht_df = self._is_sheet_data_available(self.dfd, sht)
		if sht_df is None or sht_df is False : return None
		#
		self.vrf_df = sht_df
		self.add_filter_col()
		self.update_column_names()
		self.drop_mtmt_vrf()
		self.update_rt()


# ================================================================================================