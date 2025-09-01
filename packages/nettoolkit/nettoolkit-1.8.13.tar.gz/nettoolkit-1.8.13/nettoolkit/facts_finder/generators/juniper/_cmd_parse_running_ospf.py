"""juniper ospf parsing from set config  """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *
from ._cmd_parse_running import Running

merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningOSPF(Running):
	"""object for ospf level config parser

	Args:
		cmd_op (list, str): config output, either list or multiline string
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the  config output
		"""    		    		
		super().__init__(cmd_op)
		self.op_dict = OrderedDict()

	# ----------------------------------------------------------------------------- #
	def ospf_read(self, func):
		"""directive function to get the various instance level output

		Args:
			func (method): method to be executed on interface config line

		Returns:
			dict: parsed output dictionary
		"""    		
		instance_dict = OrderedDict()
		for l in self.set_cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("#"): continue
			ospf_spl = l.split(" protocols ospf ")
			if len(ospf_spl) != 2: continue
			spl = ospf_spl[-1].split()
			p = "1" if ospf_spl[0] == 'set' else ospf_spl[0].split()[-1]
			if not p: continue
			#
			if not instance_dict.get(p): instance_dict[p] = {}
			vrf_instance_dict = instance_dict[p]
			vrf_instance_dict['ospf_vrf'] = "" if p =='1' else  p
			#
			vrf_instance_dict['filter'] = 'ospf'
			# if not (vrf_instance_dict.get('filter') and vrf_instance_dict['filter']):
			# 	vrf_instance_dict['filter'] = get_juniper_int_type(p).lower()
			#
			func(vrf_instance_dict, ospf_spl[-1], spl)
		return instance_dict

	# ----------------------------------------------------------------------------- #

	def passive_interfaces(self):
		"""update the passive interfaces
		"""    		
		merge_dict(self.op_dict, self.ospf_read(self.get_passive_interfaces))

	@staticmethod
	def get_passive_interfaces(vrf_op_dict, l, spl):
		"""parser function to get passive interfaces

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""
		if spl[-1] == 'passive':
			vrf_op_dict['passive_interfaces']  = get_appeneded_value(vrf_op_dict, 'passive_interfaces', spl[-2])



	def summaries(self):
		"""update the ospf area range summaries
		"""    		
		merge_dict(self.op_dict, self.ospf_read(self.get_summaries))

	@staticmethod
	def get_summaries(vrf_op_dict, l, spl):
		"""parser function to get ospf area range summaries

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""
		if len(spl)>3 and spl[2] == 'area-range':
			area = spl[1]
			prefix = spl[3]
			if not vrf_op_dict.get('summary'):
				vrf_op_dict['summary'] = {}
			range_op_dict = vrf_op_dict['summary']

			range_op_dict['prefixes']  = get_appeneded_value(range_op_dict, 'prefixes', prefix)
			range_op_dict['areas']  = get_appeneded_value(range_op_dict, 'areas', area)
			range_op_dict['area_'+area+'_prefixes'] = get_appeneded_value(range_op_dict, 'area_'+area+'_prefixes', prefix)


	def ospf_authentication(self):
		"""update the ospf authentication parameters
		"""    		
		merge_dict(self.op_dict, self.ospf_read(self.get_ospf_authentication))

	@staticmethod
	def get_ospf_authentication(vrf_op_dict, l, spl):
		"""parser function to get ospf authentication parameters

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""
		if len(spl)>6 and spl[4] == 'authentication':
			password = get_juniper_pw_string(spl, 6)
			interface = spl[3]
			if not vrf_op_dict.get('auth'):
				vrf_op_dict['auth'] = {}
			auth_op_dict = vrf_op_dict['auth']

			auth_op_dict['interfaces']  = get_appeneded_value(auth_op_dict, 'interfaces', interface)
			auth_op_dict['password']  = get_appeneded_value(auth_op_dict, 'password', password)


	def interface_type(self):
		"""update the ospf interface type
		"""    		
		merge_dict(self.op_dict, self.ospf_read(self.get_interface_type))

	@staticmethod
	def get_interface_type(vrf_op_dict, l, spl):
		"""parser function to get ospf interface type

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse
			spl (list): splitted line to parse

		Returns:
			None: None
		"""
		if len(spl)>5 and spl[4] == 'interface-type':
			if_type = spl[-1]
			interface = spl[3]
			if not vrf_op_dict.get('ospf'):
				vrf_op_dict['ospf'] = {}
			auth_op_dict = vrf_op_dict['ospf']

			auth_op_dict['ifs']  = get_appeneded_value(auth_op_dict, 'ifs', interface)
			auth_op_dict['if_type']  = get_appeneded_value(auth_op_dict, 'if_type', if_type)



	# # Add more interface related methods as needed.


# ------------------------------------------------------------------------------


def get_instances_ospfs(cmd_op, *args):
	"""defines set of methods executions. to get various instance of ospf parameters.
	uses RunningOSPF in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""    	
	R  = RunningOSPF(cmd_op)
	R.passive_interfaces()
	R.summaries()
	R.ospf_authentication()
	R.interface_type()

	# # update more instance related methods as needed.
	if not R.op_dict:
		R.op_dict['dummy_ospf'] = ""

	return {'op_dict': R.op_dict}



# ------------------------------------------------------------------------------

