"""juniper routing instances parsing from set config  """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *
from ._cmd_parse_running import Running


merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningIntances(Running):
	"""object for instance level config parser

	Args:
		cmd_op (list, str): config output, either list of multiline string
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the  config output
		"""    		    		
		super().__init__(cmd_op)
		self.instance_dict = OrderedDict()

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
			if not l.startswith("set routing-instances "): continue
			spl = l.split()
			p = spl[2]
			if not p: continue
			if not ports_dict.get(p): ports_dict[p] = {}
			port_dict = ports_dict[p]
			port_dict['filter'] = 'vrf'
			func(port_dict, l, spl)
		return ports_dict

	def vrf_route_target(self):
		"""update the vrf route target
		"""    		
		func = self.get_vrf_route_target
		merge_dict(self.instance_dict, self.instance_read(func))

	@staticmethod
	def get_vrf_route_target(port_dict, l, spl):
		"""parser function to update vrf route target details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""  
		if spl[3] == 'route-distinguisher':
			port_dict['vrf_route_target'] = spl[-1].strip().split(":")[-1]


	def vrf_description(self):
		"""update the vrf description
		"""    		
		func = self.get_vrf_description
		merge_dict(self.instance_dict, self.instance_read(func))

	@staticmethod
	def get_vrf_description(port_dict, l, spl):
		"""parser function to update vrf description details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""  
		if spl[3] == 'description':
			desc = " ".join(spl[4:]).strip()
			if desc[0] == '"': desc = desc[1:]
			if desc[-1] == '"': desc = desc[:-1]
			port_dict['vrf_description'] = desc




	# # Add more interface related methods as needed.


# ------------------------------------------------------------------------------


def get_instances_running(cmd_op, *args):
	"""defines set of methods executions. to get various instance parameters.
	uses RunningIntances in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""    	
	R  = RunningIntances(cmd_op)
	R.vrf_route_target()
	R.vrf_description()

	# # update more instance related methods as needed.
	if not R.instance_dict:
		R.instance_dict['dummy_instance'] = ''

	return {'op_dict': R.instance_dict}



# ------------------------------------------------------------------------------

