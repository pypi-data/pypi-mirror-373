"""cisco running-config - prefix list output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

class RunningPrefixLists():
	"""object for running config prefix list parser
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the running config output

		Args:
			cmd_op (list, str): running config output, either list of multiline string
		"""    		
		self.cmd_op = cmd_op
		self.obj_dict = {}

	def pl_read(self, func):
		"""directive function to get the various prefix list level output

		Args:
			func (method): method to be executed on prefix list config line

		Returns:
			dict: parsed output dictionary
		"""    		
		ports_dict = OrderedDict()
		for l in self.cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("!"): continue
			if not l.startswith("ip prefix-list ") and not l.startswith("ipv6 prefix-list "): continue
			#
			spl = l.strip().split()
			pl_name = spl[2]
			if not ports_dict.get(pl_name):
				ports_dict[pl_name] = {}
			rdict = ports_dict[pl_name]

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
		line_seq = int(spl[4])
		action = spl[5]
		pfx = spl[6]
		match_type = spl[7] if len(spl) > 7 else ""
		match_len = spl[8] if len(spl) > 8 else ""
		# #
		if not dic.get(line_seq):
			dic[line_seq] = {}
		pls_dic = dic[line_seq]

		pls_dic['version'] = version
		pls_dic['action'] = action
		pls_dic['prefix'] = pfx
		pls_dic['match_type'] = match_type
		pls_dic['match_len'] = match_len

		return dic

# ------------------------------------------------------------------------------

def get_system_running_prefix_lists(command_output):
	"""parse output of : show running-config

	Args:
		command_output (list): command output

	Returns:
		dict: prefix-lists level parsed output dictionary
	"""    	
	R  = RunningPrefixLists(command_output)
	R.pl_dict()

	return {'prefix-lists': R.obj_dict }

# ------------------------------------------------------------------------------
