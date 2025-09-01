"""juniper routes parsing from set config  """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *
from ._cmd_parse_running import Running

merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningRoutes(Running):
	"""object for routes level config parser
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the  config output

		Args:
			cmd_op (list, str): config output, either list of multiline string
		""" 
		self.n = 0   		    		
		super().__init__(cmd_op)
		self.route_dict = OrderedDict()

	# ----------------------------------------------------------------------------- #
	def route_read(self, func, v=4):
		"""directive function to get the various static routes level output

		Args:
			func (method): method to be executed on set commands

		Returns:
			dict: parsed output dictionary
		"""
		v4spl_str = ' routing-options static route '
		v6spl_str = ' routing-options rib blue.inet6.0 static route '
		if v == 4: spl_str = v4spl_str
		if v == 6: spl_str = v6spl_str
		prev_prefix, prev_vrf = "", ""		
		ports_dict = OrderedDict()
		for l in self.set_cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("#"): continue
			if not l.find(spl_str) > -1: continue
			vrf_spl_route = l.split(spl_str)
			vrf_spl_sect = vrf_spl_route[0].split()
			route_spl_sect = vrf_spl_route[-1].split()
			prefix = route_spl_sect[0]
			vrf = vrf_spl_sect[2] if len(vrf_spl_sect)>2 else ""
			if prefix != prev_prefix or vrf != prev_vrf:
				self.n+=1
				ports_dict[self.n] = {} 
			prev_prefix = prefix
			prev_vrf = vrf 
			rdict = ports_dict[self.n]
			rdict['filter'] = 'static'
			func(rdict,  l, vrf_spl_sect, route_spl_sect, v)
		return ports_dict

	# ----------------------------------------------------------------------------- #

	def routes_dict(self):
		"""update the route details
		"""   
		func = self.get_route_dict
		merge_dict(self.route_dict, self.route_read(func, 4))

	def v6routes_dict(self):
		"""update the route details
		"""   
		func = self.get_route_dict
		merge_dict(self.route_dict, self.route_read(func, 6))

	@staticmethod
	def get_route_dict(dic, l, vrf_spl_sect, route_spl_sect, v):
		"""parser function to update route details

		Args:
			dic (dict): blank dictionary to update a route info
			l (str): line to parse

		Returns:
			None: None
		"""
		## Do not use negative index for any items other than remark, it may not work.
		#
		if not dic.get('prefix'): dic['prefix'] = route_spl_sect[0]
		if not dic.get('pfx_vrf') and len(vrf_spl_sect)> 1: dic['pfx_vrf'] = vrf_spl_sect[2]
		#
		if not dic.get('next_hop'):
			dic['next_hop'] = ''
		#
		if route_spl_sect[1] == 'next-hop': 
			if dic['next_hop']:
				dic['next_hop'] += "\n"+route_spl_sect[2] 
			else:
				dic['next_hop'] = route_spl_sect[2]
		if route_spl_sect[1] == 'preference': dic['adminisrative_distance'] = route_spl_sect[2] 
		if route_spl_sect[1] == 'tag': dic['tag_value'] = route_spl_sect[2] 
		if not dic.get('version'): dic['version'] = v
		if not dic.get('remark'): 
			if l.find("  ## comment: ")>1:
				dic['remark'] = l.split("  ## comment: ")[-1]
			else:
				dic['remark'] = ""
		#
		if not dic.get('resolve'): 
			dic['resolve'] = True if l.find(" resolve")>1 else ""
		if not dic.get('retain'): 
			dic['retain'] = True if l.find(" retain")>1 else ""
		#




	# # Add more static route related methods as needed.


# ------------------------------------------------------------------------------


def get_system_running_routes(cmd_op, *args):
	"""defines set of methods executions. to get various instance of route parameters.
	uses RunningRoutes in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""    	
	R  = RunningRoutes(cmd_op)
	R.routes_dict()
	R.v6routes_dict()


	# # update more interface related methods as needed.
	if not R.route_dict:
		R.route_dict['dummy_route'] = ""

	return {'op_dict': R.route_dict}



# ------------------------------------------------------------------------------

