"""cisco running-config - prefix list output parser """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *

merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningPrefixLists():
	"""object for running config prefix list parser
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the running config output

		Args:
			cmd_op (list, str): running config output, either list of multiline string
		"""    		
		self.cmd_op = verifid_output(cmd_op)
		self.obj_dict = {}

	def pl_read(self, func):
		"""directive function to get the various prefix list level output

		Args:
			func (method): method to be executed on prefix list config line

		Returns:
			dict: parsed output dictionary
		"""    		
		n = 0
		ports_dict = OrderedDict()
		for l in self.cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("!"): continue
			if not l.startswith("ip prefix-list ") and not l.startswith("ipv6 prefix-list "): continue
			#
			spl = l.strip().split()
			n += 1
			ports_dict[n] = {}
			rdict = ports_dict[n]
			rdict['filter'] = 'prefix_list'
			func(rdict,  l, spl)
		return ports_dict

	def pl_dict(self):
		"""update the prefix-list details
		"""   
		func = self.get_obj_dict
		merge_dict(self.obj_dict, self.pl_read(func))

	@staticmethod
	def get_obj_dict(dic, l, spl):
		"""parser function to update prefix-list details

		Args:
			dic (dict): blank dictionary to update a prefix-list info
			l (str): line to parse

		Returns:
			None: None
		"""
		version = 'unknown'		
		if spl[0] == 'ip': version = 4
		if spl[0] == 'ipv6': version = 6
		if version not in (4,6): return None
		idx_update = 0
		#
		pl_name = spl[2]
		line_seq = spl[4]
		action = spl[5]
		pfx = spl[6]
		match_type = spl[7] if len(spl) > 7 else ""
		match_len = spl[8] if len(spl) > 8 else ""
		#
		dic['pl_version'] = version
		dic['pl_name'] = pl_name
		dic['pl_seq'] = line_seq
		dic['pl_action'] = action
		dic['pl_prefix'] = pfx
		dic['pl_match_type'] = match_type
		dic['pl_match_len'] = match_len

		return dic

# ------------------------------------------------------------------------------

def get_system_running_prefix_lists(cmd_op, *args):
	"""defines set of methods executions. to get various ip prefix-list parameters.
	uses RunningPrefixLists in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""
	R  = RunningPrefixLists(cmd_op)
	R.pl_dict()


	# # update more interface related methods as needed.
	if not R.obj_dict:
		R.obj_dict['dummy_pl'] = ""

	return {'op_dict': R.obj_dict }

# ------------------------------------------------------------------------------
