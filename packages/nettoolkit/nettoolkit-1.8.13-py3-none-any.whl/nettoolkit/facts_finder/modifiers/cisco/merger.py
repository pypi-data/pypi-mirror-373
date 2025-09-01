"""merger in steps
"""

from pathlib import *
import os

from nettoolkit.facts_finder.modifiers.commons import KeyExchanger

from .commands.cmd_dict import *
from .cisco_var import VarCisco
from .cisco_tables import TableInterfaceCisco
from .cisco_vrfs import TableVrfsCisco

# ================================================================================================

def get_cmd_list_cisco(
	var_column_mapper_file=None,
	int_column_mapper_file=None,
	):
	"""create commands list for each tab (var/interface/vrf) from the column mapper

	Args:
		var_column_mapper_file (str, optional): var column mapper file. Defaults to None.
		int_column_mapper_file (str, optional): interfaces column mapper file. Defaults to None.

	Returns:
		dict: dictionary of commands list
	"""	
	cmd_lst = {
		'cmd_lst_var': None,
		'cmd_lst_int': None,
		'cmd_lst_vrf': None,
	}
	#
	if var_column_mapper_file is not None:
		for k,v in cmd_lst_var.copy().items():
			cmd_lst_var[k] = {}
		KEC_VAR = KeyExchanger(var_column_mapper_file, cmd_lst_var)
		cmd_lst['cmd_lst_var'] = KEC_VAR.cmd_lst
	#
	if int_column_mapper_file is not None:
		for k,v in cmd_lst_int.copy().items():
			cmd_lst_int[k] = {}
		KEC_INT = KeyExchanger(int_column_mapper_file, cmd_lst_int)
		cmd_lst['cmd_lst_int'] = KEC_INT.cmd_lst
		#
		for k,v in cmd_lst_vrf.copy().items():
			cmd_lst_vrf[k] = {}
		KEC_VRF = KeyExchanger(int_column_mapper_file, cmd_lst_vrf)
		cmd_lst['cmd_lst_vrf'] = KEC_VRF.cmd_lst

	return cmd_lst

# ================================================================================================

def cisco_modifier(capture_tfsm_file, 
	cmd_lst=None,
	var_column_mapper_file=None,
	int_column_mapper_file=None,
	use_cdp=False,
	):
	"""Club var/interface/vrf data from various commands parsed excel outputs.

	Args:
		capture_tfsm_file (str): device capture file
		cmd_lst (_type_, optional): manually provide commands list, or it will take a few default commands ie. Defaults to None.
		var_column_mapper_file (str, optional): var column mapper file. Defaults to None.
		int_column_mapper_file (str, optional): interfaces column mapper file. Defaults to None.
		use_cdp (bool, optional): inspect cdp neighbors or not. Defaults to False.

	Returns:
		dict: dictionary of pandas dataframes
	"""	
	ntc_modifier = {}
	if cmd_lst is None:
		cmd_lst=get_cmd_list_cisco(var_column_mapper_file, int_column_mapper_file)

	## 1. ---  `var` Tab 
	vc = VarCisco(capture_tfsm_file, cmd_lst['cmd_lst_var'])
	vc()
	ntc_modifier.update( vc.pdf_dict )

	## 2. ---  `table` Tab 
	tic = TableInterfaceCisco(capture_tfsm_file, cmd_lst['cmd_lst_int'], use_cdp)
	tic()
	ntc_modifier.update( tic.pdf_dict )

	## 3. ---  `vrf` Tab 
	tvc = TableVrfsCisco(capture_tfsm_file, cmd_lst['cmd_lst_vrf'])
	tvc()
	ntc_modifier.update( tvc.pdf_dict )

	return ntc_modifier

	# ================================================================================================
