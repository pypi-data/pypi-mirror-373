"""juniper bgp protocol routing instances parsing from set config  """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *
from ._cmd_parse_running import Running


merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningIntanceBGP(Running):
	"""object for instance level config parser

	Args:
		cmd_op (list, str): config output, either list of multiline string
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the  config output
		"""    		    		
		super().__init__(cmd_op)
		self.instance_dict = OrderedDict()

	# ----------------------------------------------------------------------------- #
	def instance_read(self, func):
		"""directive function to get the various instance level output

		Args:
			func (method): method to be executed on interface config line

		Returns:
			dict: parsed output dictionary
		"""    		
		ports_dict = OrderedDict()
		for l in self.set_cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("#"): continue
			spl = l.split()
			if 'protocols' not in spl: continue
			proto_idx = spl.index('protocols')
			if "prefix-list" in spl and spl.index('prefix-list') < proto_idx: continue
			if spl[proto_idx+1] != 'bgp' or spl[proto_idx+2] != 'group': continue
			p = spl[proto_idx+3]
			if not p: continue
			if not ports_dict.get(p): ports_dict[p] = {}
			port_dict = ports_dict[p]
			port_dict['filter'] = 'bgp'
			func(port_dict, l, spl, proto_idx)
		return ports_dict

	# ----------------------------------------------------------------------------- #
	def instance_bgp_nbr_read(self, func):
		"""directive function to get the various instance level output for bgp neighbours only

		Args:
			func (method): method to be executed on interface config line

		Returns:
			dict: parsed output dictionary
		"""    		
		ports_dict = OrderedDict()
		for l in self.set_cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("#"): continue
			spl = l.split()
			if 'protocols' not in spl: continue
			proto_idx = spl.index('protocols')
			if "prefix-list" in spl and spl.index('prefix-list') < proto_idx: continue
			if spl[proto_idx+1] != 'bgp' or spl[proto_idx+2] != 'group' or spl[proto_idx+4] != 'neighbor': continue
			p = spl[proto_idx+5]
			if not p: continue
			if not ports_dict.get(p): ports_dict[p] = {}
			port_dict = ports_dict[p]
			port_dict['filter'] = 'bgp'
			func(port_dict, l, spl, proto_idx)
		return ports_dict

	# ----------------------------------------------------------------------------- #

	def bgp_grp_info(self):
		"""update the bgp group detail - description, peer group, peer ip, auth-key, vrf, peer as
		"""    		
		func = self.get_bgp_grp_info
		merge_dict(self.instance_dict, self.instance_read(func))

	@staticmethod
	def get_bgp_grp_info(port_dict, l, spl, proto_idx):
		"""parser function to update bgp group detail - description, peer group, peer ip, auth-key, vrf, peer as

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse
			proto_idx (int): index value from where protocol bgp starts in provided list

		Returns:
			None: None
		""" 
		port_dict['bgp_peergrp'] = spl[proto_idx+3]
		## --- description and vrf ---
		if len(spl)>proto_idx+4 and spl[proto_idx+4] == 'description':
			desc = " ".join(spl[proto_idx+5:]).strip()
			if desc[0] == '"': desc = desc[1:]
			if desc[-1] == '"': desc = desc[:-1]
			port_dict['bgp_peer_description'] = desc
			if proto_idx>1:
				port_dict['bgp_vrf'] = spl[proto_idx-1]
			else:
				port_dict['bgp_vrf'] = ""
		## --- auth key ---
		if len(spl)>proto_idx+4 and spl[proto_idx+4] == 'authentication-key':
			pw = " ".join(spl[proto_idx+5:]).strip().split("##")[0].strip()
			if pw[0] == '"': pw = pw[1:]
			if pw[-1] == '"': pw = pw[:-1]
			try:
				pw = juniper_decrypt(pw)
			except: pass
			port_dict['bgp_peer_password'] = pw
		## --- peer-as ---
		if len(spl)>proto_idx+4 and spl[proto_idx+4] == 'peer-as':
			port_dict['bgp_peer_as'] = spl[proto_idx+5]
		## --- local-as ---
		if len(spl)>proto_idx+4 and spl[proto_idx+4] == 'local-as':
			port_dict['bgp_local_as'] = spl[proto_idx+5]
		## --- ebgp multihops ---
		if len(spl)>proto_idx+5 and spl[proto_idx+4] == 'multihop':
			port_dict['bgp_peer_multihops'] = spl[-1]

	# ----------------------------------------------------------------------------- #

	def bgp_nbr_info(self):
		"""update the bgp neighbor detail - description, peer group, peer ip, auth-key, vrf, peer as
		"""    		
		func = self.get_bgp_nbr_info
		merge_dict(self.instance_dict, self.instance_bgp_nbr_read(func))

	@staticmethod
	def get_bgp_nbr_info(port_dict, l, spl, proto_idx):
		"""parser function to update bgp neighbor detail - description, peer group, peer ip, auth-key, vrf, peer as

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse
			proto_idx (int): index value from where protocol bgp starts in provided list

		Returns:
			None: None
		"""
		port_dict['bgp_peergrp'] = spl[proto_idx+3]
		## --- description and vrf ---
		if len(spl)>proto_idx+6 and spl[proto_idx+6] == 'description':
			desc = " ".join(spl[proto_idx+7:]).strip()
			if desc[0] == '"': desc = desc[1:]
			if desc[-1] == '"': desc = desc[:-1]
			port_dict['bgp_peer_description'] = desc
		if proto_idx > 1:
			port_dict['bgp_vrf'] = spl[proto_idx-1]
		else:
			port_dict['bgp_vrf'] = ""
		port_dict['bgp_peer_ip'] = spl[proto_idx+5]
		## --- auth key ---
		if len(spl)>proto_idx+6 and spl[proto_idx+6] == 'authentication-key':
			pw = " ".join(spl[proto_idx+7:]).strip().split("##")[0].strip()
			if pw[0] == '"': pw = pw[1:]
			if pw[-1] == '"': pw = pw[:-1]
			try:
				pw = juniper_decrypt(pw)
			except: pass
			port_dict['bgp_peer_password'] = pw
		## --- peer-as ---
		if len(spl)>proto_idx+6 and spl[proto_idx+6] == 'peer-as':
			port_dict['bgp_peer_as'] = spl[proto_idx+7]
		## --- local-as ---
		if len(spl)>proto_idx+6 and spl[proto_idx+6] == 'local-as':
			port_dict['bgp_local_as'] = spl[proto_idx+7]





	# # Add more interface related methods as needed.


# ------------------------------------------------------------------------------


def get_instances_bgps(cmd_op, *args):
	"""defines set of methods executions. to get various instance parameters.
	uses RunningIntanceBGP in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""    	
	R  = RunningIntanceBGP(cmd_op)
	R.bgp_grp_info()
	R.bgp_nbr_info()

	# # update more instance related methods as needed.
	if not R.instance_dict:
		R.instance_dict['dummy_bgp'] = ""

	return {'op_dict': R.instance_dict}



# ------------------------------------------------------------------------------

