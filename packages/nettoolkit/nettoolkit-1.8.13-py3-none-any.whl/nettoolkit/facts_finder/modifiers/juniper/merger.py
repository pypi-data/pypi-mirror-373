"""Juniper mergers
"""

from pathlib import *
import os

from nettoolkit.facts_finder.modifiers.commons import KeyExchanger

from .commands.cmd_dict import *
from .juniper_var import VarJuniper
from .juniper_tables import TableInterfaceJuniper

# ================================================================================================

def get_cmd_list_juniper(
	column_mapper_file=None,
	):
	"""create commands list for each tab (var/interface/vrf) from the column mapper

	Args:
		column_mapper_file (_type_, optional): column mapper file. Defaults to None.

	Returns:
		dict: dictionary of commands list
	"""	
	cmd_lst = {
		'cmd_lst_var': None,
		'cmd_lst_int': None,
	}
	#
	if column_mapper_file is not None:
		for k,v in cmd_lst_var.copy().items():
			cmd_lst_var[k] = {}
		KEC_VAR = KeyExchanger(column_mapper_file, cmd_lst_var)
		cmd_lst['cmd_lst_var'] = KEC_VAR.cmd_lst
	#
	if column_mapper_file is not None:
		for k,v in cmd_lst_int.copy().items():
			cmd_lst_int[k] = {}
		KEC_INT = KeyExchanger(column_mapper_file, cmd_lst_int)
		cmd_lst['cmd_lst_int'] = KEC_INT.cmd_lst
	
	return cmd_lst

# ================================================================================================

def juniper_modifier(capture_tfsm_file, 
	cmd_lst=None,
	column_mapper_file=None,
	):
	"""Club var/interface data from various commands parsed excel outputs.

	Args:
		capture_tfsm_file (_type_): device capture output file
		cmd_lst (_type_, optional): manual commands list. Defaults to None.
		column_mapper_file (_type_, optional): column mapper file. Defaults to None.

	Returns:
		dict: dictionary of pandas DataFrame
	"""	
	ntc_modifier = {}
	if cmd_lst is None:
		cmd_lst=get_cmd_list_juniper(column_mapper_file)

	## 1. ---  `var` Tab 
	vj = VarJuniper(capture_tfsm_file, cmd_lst['cmd_lst_var'])
	vj()
	ntc_modifier.update( vj.pdf_dict )

	## 2. ---  `table` Tab 
	tij = TableInterfaceJuniper(capture_tfsm_file, cmd_lst['cmd_lst_int'])
	tij()
	ntc_modifier.update( tij.pdf_dict )

	return ntc_modifier

# ================================================================================================
