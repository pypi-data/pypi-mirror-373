"""cisco show running-config command parser for vrf level outputs """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *

merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningVRFs():
	"""object for VRF level running config parser

	Args:
		cmd_op (list, str): running config output, either list of multiline string
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the running config output
		"""    		    		
		self.cmd_op = verifid_output(cmd_op)
		self.vrf_dict = OrderedDict()

	def vrf_read(self, func):
		"""directive function to get the various VRF level output

		Args:
			func (method): method to be executed on VRF config line

		Returns:
			dict: parsed output dictionary
		"""    		
		int_toggle = False
		vrfs_dict = OrderedDict()
		for l in self.cmd_op:
			if blank_line(l): continue
			if l.startswith("!"): 
				int_toggle = False
				continue
			if l.startswith("vrf ") or l.startswith("ip vrf "):
				p = get_vrf_cisco(l)
				if not p: continue
				if not vrfs_dict.get(p): vrfs_dict[p] = {}
				port_dict = vrfs_dict[p]
				int_toggle = True
				continue
			if int_toggle:
				port_dict['filter'] = 'vrf'
				func(port_dict, l)
		return vrfs_dict

	@staticmethod
	def get_vrf_description(port_dict, l):
		"""parser function to update vrf description details

		Args:
			port_dict (dict): dictionary with a vrf info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		desc = None
		if l.strip().startswith("description "):
			desc = l.strip().split(" ", 1)[-1]
			port_dict['vrf_description'] = desc
		if not desc: return None

	def vrf_description(self):
		"""update the vrf description details
		"""    		
		func = self.get_vrf_description
		merge_dict(self.vrf_dict, self.vrf_read(func))

	@staticmethod
	def get_vrf_rd(port_dict, l):
		"""parser function to update vrf rd details

		Args:
			port_dict (dict): dictionary with a vrf info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		rd = None
		if l.strip().startswith("rd "):
			rd = l.strip().split(" ", 1)[-1]
			port_dict['default_rd'] = rd
		if not rd: return None

	def vrf_rd(self):
		"""update the vrf rd details
		"""    		
		func = self.get_vrf_rd
		merge_dict(self.vrf_dict, self.vrf_read(func))

	@staticmethod
	def get_vrf_rt(port_dict, l):
		"""parser function to update vrf rt details

		Args:
			port_dict (dict): dictionary with a vrf info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		rt = None
		if l.strip().startswith("route-target export "):
			rt = l.strip().split(":")[-1]
			port_dict['vrf_route_target'] = rt
		if not rt: return None

	def vrf_rt(self):
		"""update the vrf rt details
		"""    		
		func = self.get_vrf_rt
		merge_dict(self.vrf_dict, self.vrf_read(func))

	@staticmethod
	def get_vrf_af(port_dict, l):
		"""parser function to update vrf address-family details

		Args:
			port_dict (dict): dictionary with a vrf info
			l (str): string line to parse

		Returns:
			None: None
		"""    	
		if l.strip().startswith("address-family "):
			af = l.strip().split()[-1]
			if port_dict.get('protocols'):
				port_dict['protocols'] += "," + af
			else:
				port_dict['protocols'] = af

	def vrf_af(self):
		"""update the vrf address-family details
		"""    		
		func = self.get_vrf_af
		merge_dict(self.vrf_dict, self.vrf_read(func))


	# # Add more vrf related methods as needed.


# ------------------------------------------------------------------------------


def get_vrfs_running(cmd_op, *args):
	"""defines set of methods executions. to get various vrf parameters.
	uses RunningVRFs in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""    	
	R  = RunningVRFs(cmd_op)
	R.vrf_description()
	R.vrf_rd()
	R.vrf_rt()
	R.vrf_af()

	# # update more interface related methods as needed.

	if not R.vrf_dict:
		R.vrf_dict['dummy_vrf'] = ""
	
	return {'op_dict': R.vrf_dict }

