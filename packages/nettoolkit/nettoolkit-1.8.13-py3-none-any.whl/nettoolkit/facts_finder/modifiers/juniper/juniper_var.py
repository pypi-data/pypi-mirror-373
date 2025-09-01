"""Juniper var modifiers
"""


from nettoolkit.facts_finder.modifiers.commons import *
from .commands.cmd_dict import *
# ================================================================================================
# Juniper  Var  DB
# ================================================================================================
class VarJuniper(DataFrameInit, Var):
	"""Juniper  Var  DataBase

	Args:
		capture (str): configuration capture log file
		cmd_lst (list, optional): capture commands list. Defaults to None.

	Inherits:
		DataFrameInit (cls): DataFrameInit
		Var (cls): Var
	"""	
	
	def __init__(self, capture, cmd_lst=None):
		"""object initializer
		"""		
		self.var = {}
		self.cmd_lst=cmd_lst
		if not self.cmd_lst:
			self.cmd_lst = cmd_lst_var
		super().__init__(capture)

	def __call__(self):
		self.update_device('show version')
		self.convert_to_dataframe()

	## Calls




# ================================================================================================
