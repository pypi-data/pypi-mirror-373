"""cisco show running-config parser for ospf section output """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *

merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class OSPF():
	"""parent object for OSPF running config parser

	Args:
		cmd_op (list, str): running config output, either list of multiline string
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the running config output
		"""    		    		
		self.cmd_op = verifid_output(cmd_op)
		self.op_dict = {}

	def ospf_read(self, func):
		"""directive function to get the various ospf level output

		Args:
			func (method): method to be executed on ospf config line

		Returns:
			dict: parsed output dictionary
		"""    		
		toggle, af, update_dict = False, False, ""
		op_dict = OrderedDict()
		for l in self.cmd_op:
			spl = l.strip().split()
			if l.startswith("router ospf "):
				p = spl[2]
				vrf = spl[4] if len(spl) > 3 and spl[3] == 'vrf' else ""
				if not op_dict.get(p): op_dict[p] = {}
				vrf_op_dict = op_dict[p]
				vrf_op_dict['ospf_vrf']= vrf
				toggle = True
				continue
			if l.startswith("!"): toggle = False
			if toggle:
				vrf_op_dict['filter'] = 'ospf'
				func(vrf_op_dict, l, spl)

		return op_dict



	def router_id(self):
		"""update the router-id details
		"""    		
		merge_dict(self.op_dict, self.ospf_read(self.get_router_id))

	@staticmethod
	def get_router_id(vrf_op_dict, l, spl):
		"""parser function to get router-id details

		Args:
			vrf_op_dict (dict): dictionary with a vrf info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""

		if len(spl)>0 and spl[0] == 'router-id':
			vrf_op_dict['router_id'] = spl[-1]


	def active_interfaces(self):
		"""update the active interfaces
		"""    		
		merge_dict(self.op_dict, self.ospf_read(self.get_active_interfaces))

	@staticmethod
	def get_active_interfaces(vrf_op_dict, l, spl):
		"""parser function to get active interfaces

		Args:
			vrf_op_dict (dict): dictionary with a vrf info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""
		if len(spl)>1 and spl[0] == 'no' and spl[1] == 'passive-interface':
			vrf_op_dict['active_interfaces']  = get_appeneded_value(vrf_op_dict, 'active_interfaces', spl[-1])


	def networks(self):
		"""update the networks
		"""    		
		merge_dict(self.op_dict, self.ospf_read(self.get_networks))

	@staticmethod
	def get_networks(vrf_op_dict, l, spl):
		"""parser function to get networks

		Args:
			vrf_op_dict (dict): dictionary with a vrf info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""
		if len(spl) > 0 and spl[0] == 'network':
			subnet = spl[1]
			mask = invmask_to_mask(spl[2])
			area = spl[4] if spl[3] == 'area' else ''
			network = str(addressing(subnet+"/"+str(mask)))
			if not vrf_op_dict.get('ospf'):
				vrf_op_dict['ospf'] = {}
			network_op_dict = vrf_op_dict['ospf']

			network_op_dict['network']  = get_appeneded_value(network_op_dict, 'network', network)
			network_op_dict['area']  = get_appeneded_value(network_op_dict, 'area', area)
			network_op_dict['area_'+area+'_networks'] = get_appeneded_value(network_op_dict, 'area_'+area+'_networks', network)


	def summaries(self):
		"""update the ospf area range summaries
		"""    		
		merge_dict(self.op_dict, self.ospf_read(self.get_summaries))

	@staticmethod
	def get_summaries(vrf_op_dict, l, spl):
		"""parser function to get ospf area range summaries

		Args:
			vrf_op_dict (dict): dictionary with a vrf info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""
		if len(spl)>3 and spl[0] == 'area' and spl[2] == 'range':
			area = spl[1]
			subnet = spl[3]
			mask = to_dec_mask(spl[4])
			prefix = str(addressing(subnet+"/"+str(mask)))
			if not vrf_op_dict.get('summary'):
				vrf_op_dict['summary'] = {}
			range_op_dict = vrf_op_dict['summary']

			range_op_dict['prefixes']  = get_appeneded_value(range_op_dict, 'prefixes', prefix)
			range_op_dict['areas']  = get_appeneded_value(range_op_dict, 'areas', area)
			range_op_dict['area_'+area+'_prefixes'] = get_appeneded_value(range_op_dict, 'area_'+area+'_prefixes', prefix)


# ------------------------------------------------------------------------------

def get_ospf_running(cmd_op, *args):
	"""defines set of methods executions. to get various ospf parameters.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with ospf fields
	"""    	
	R  = OSPF(cmd_op)
	R.router_id()
	R.active_interfaces()
	R.networks()
	R.summaries()

	
	if not R.op_dict:
		R.op_dict['dummy_ospf'] = ""
	
	return {'op_dict': R.op_dict }

