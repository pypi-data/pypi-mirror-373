"""juniper prefix list parsing from set config  """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from nettoolkit.addressing import addressing
from .common import *
from ._cmd_parse_running import Running

merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningPrefixLists(Running):
	"""object for prefix list level config parser
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the  config output

		Args:
			cmd_op (list, str): config output, either list of multiline string
		""" 
		self.n = 0   		    		
		super().__init__(cmd_op)
		self.pl_dict = OrderedDict()

	# ----------------------------------------------------------------------------- #
	def pl_read(self, func, v=4):
		"""directive function to get the various static prefix list level output

		Args:
			func (method): method to be executed on set commands

		Returns:
			dict: parsed output dictionary
		"""
		_str = 'set policy-options prefix-list '
		ports_dict = OrderedDict()
		n= 0
		for l in self.set_cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("#"): continue
			if not l.startswith(_str): continue
			spl = l.split()
			ports_dict[n] = {} 
			rdict = ports_dict[n]
			retu = func(rdict,  l, spl)
			if retu: n+=1
		return ports_dict

	# ----------------------------------------------------------------------------- #

	def pfxlst_dict(self):
		"""update the prefix list details
		"""
		func = self.get_pl_dict
		merge_dict(self.pl_dict, self.pl_read(func, 4))

	@staticmethod
	def get_pl_dict(dic, l, spl):
		"""parser function to update prefix list details

		Args:
			dic (dict): blank dictionary to update a prefix list info
			l (str): line to parse

		Returns:
			None: None
		"""
		pl_name = spl[3]
		if len(spl) > 4: pfx = spl[4]
		try:
			if pfx: p = addressing(pfx)
			version = p.version
		except:
			return None
		dic['filter'] = 'prefix_list'
		dic['pl_name'] = pl_name
		dic['pl_prefix'] = pfx
		dic['pl_version'] = version
		### -- below are not valid for juniper -- ###
		dic['pl_seq'] = ''
		dic['pl_action'] = ''
		dic['pl_match_type'] = ''
		dic['pl_match_len'] = ''

		return dic




	# # Add more static route related methods as needed.


# ------------------------------------------------------------------------------


def get_system_running_prefix_lists(cmd_op, *args):
	"""defines set of methods executions. to get various instance of prefix list parameters.
	uses RunningPrefixLists in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""    	
	R  = RunningPrefixLists(cmd_op)
	R.pfxlst_dict()


	# # update more interface related methods as needed.
	if not R.pl_dict:
		R.pl_dict['dummy_pl'] = ""

	return {'op_dict': R.pl_dict}



# ------------------------------------------------------------------------------

