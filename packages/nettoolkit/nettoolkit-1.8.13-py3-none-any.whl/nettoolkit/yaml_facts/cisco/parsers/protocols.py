"""cisco running-config parser for protocol xxx section output """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  Class
# ------------------------------------------------------------------------------

@dataclass
class ProtocolsConfig():
	"""Base class for protocols standard methods implementation

	Raises:
		Exception: if any unsupported protocol provided

	"""    	
	run_list: list[str] = field(default_factory=[])

	single_instance_protocols = { 'rip', 'bgp' }
	multi_instance_protocols = { 'ospf', 'eigrp' }


	def protocol_config_initialize(self, protocol):
		if protocol in self.single_instance_protocols:		
			self.routing_protocol_config_list = self._get_router_configurations(protocol)
			self.vrfs = self._get_instances()
			self._add_instances_lines_to_instance_dict()
		elif protocol in self.multi_instance_protocols:
			self.vrfs = self._get_router_configurations_for_multi_instance_protocols(protocol)

		else:
			raise Exception(f"[-] UnsupportedProtocol: Protocol detail extraction unavailable for the protocol {protocol}")

	### Single instance Protocol Methods

	def _get_router_configurations(self, protocol):
		start = False
		lst = []
		for line in self.run_list:
			if not line.strip() : continue
			start = start or line.startswith(f"router {protocol}")
			if start and line[0] == "!": break
			if not start: continue
			lst.append(line)
		return lst

	def _get_instances(self):
		vrfs = { }
		for line in self.routing_protocol_config_list:
			if not line[1:].startswith("address-family"): continue
			spl = line.strip().split()
			if 'vrf' not in spl: continue
			if not vrfs.get(spl[-1]):
				vrfs[spl[-1]] = {}
			if spl[1] in self.supported_af_types:
				if not vrfs[spl[-1]].get('af_type'):
					vrfs[spl[-1]]['af_type'] = set()
				vrfs[spl[-1]]['af_type'].add(spl[1])

		add_blankdict_key(vrfs, None)
		return vrfs

	def _add_instances_lines_to_instance_dict(self):
		## config list for all appeared vrfs
		for vrf, vrf_dict in self.vrfs.items():
			if vrf == None: continue
			start = False
			lst = []
			for line in self.routing_protocol_config_list:
				if line.strip().startswith("address-family") and line.strip().endswith(f"vrf {vrf}"):
					start = True
					spl = line.strip().split()
					vrf_type = ''
					if spl[1] in self.supported_af_types: 
						vrf_type = spl[1]
					if not vrf_dict.get('lines'):
						vrf_dict['lines'] = []
				if line.strip() == 'exit-address-family': start = False
				if not start: continue
				vrf_dict['lines'].append(line.strip())

		## config list for global instance
		for vrf, vrf_dict in self.vrfs.items():
			if vrf : continue
			lst = []
			start = True
			for line in self.routing_protocol_config_list:
				if line.strip().startswith("!"): 
					continue
				if line.strip().startswith("address-family"):
					start = False
					continue
				if line.strip() == 'exit-address-family': 
					start = True
					continue
				if not start: 
					continue
				if not vrf_dict.get('lines'):
					vrf_dict['lines'] = []
				vrf_dict['lines'].append(line.strip())

	### Multi instance protocol methods

	def _get_router_configurations_for_multi_instance_protocols(self, protocol):
		self.protocol_vrf_dict = {}
		start = False
		dic = {}
		for line in self.run_list:
			if not line.strip() : continue
			if line.startswith(f"router {protocol} "):
				spl = line.split()
				vrf = next_index_item(spl, 'vrf') if 'vrf' in spl else None					
				process_id, lst = spl[2], []
				start = True
				self._add_instance_name_for_multi_instance_protocols(process_id, vrf)
			if start and line[0] == "!": 
				dic[process_id] = lst
				start = False
				lst.append(line)
				continue
			if not start: continue
			lst.append(line)
		return dic

	def _add_instance_name_for_multi_instance_protocols(self, process_id, vrf):
		add_blankdict_key(self.protocol_vrf_dict, process_id)
		update_key_value(self.protocol_vrf_dict[process_id], 'process-id', process_id)
		update_key_value(self.protocol_vrf_dict[process_id], 'vrf', vrf)




	### GENERAL

	def _get_attributes(self, lines):
		attr_dict = {}
		for line in lines:
			line = line.strip()
			spl  = line.split()
			for f in self.attr_functions:
				f(attr_dict, line, spl)
		return attr_dict		


	def remove_empty_vrfs(self, vrf_dict):
		for vrf in list(vrf_dict.keys()):
			if not vrf_dict[vrf]:
				del(vrf_dict[vrf])


# ------------------------------------------------------------------------------
#  functions
# ------------------------------------------------------------------------------

def get_protocol_instance_dict(protocol, instances_dic):
	if instances_dic:
		return {'protocols': {protocol: {'instances': instances_dic}} }
	else:
		return {'protocols': {}}


