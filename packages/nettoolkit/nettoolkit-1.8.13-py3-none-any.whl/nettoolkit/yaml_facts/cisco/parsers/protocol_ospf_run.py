"""cisco show running-config parser for ospf section output """

# ------------------------------------------------------------------------------
from .common import *
from .protocols import ProtocolsConfig, get_protocol_instance_dict
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
#  OSPF ATTR FUNCS
# ------------------------------------------------------------------------------

def _get_router_id(attr_dict, l, spl):
	if len(spl)>0 and spl[0] == 'router-id':
		attr_dict['router_id'] = spl[-1]

def _get_active_interfaces(attr_dict, l, spl):
	if len(spl)>1 and spl[0] == 'no' and spl[1] == 'passive-interface':
		append_attribute(attr_dict, 'active_interfaces', spl[-1])

def _get_networks(attr_dict, l, spl):
	if len(spl) > 0 and spl[0] == 'network':
		subnet = spl[1]
		mask = invmask_to_mask(spl[2])
		area = spl[4] if spl[3] == 'area' else ''
		network = str(addressing(subnet+"/"+str(mask)))
		network_op_dict = add_blankdict_key(attr_dict, 'area')
		area_dict = add_blankdict_key(network_op_dict, area)
		append_attribute(area_dict, 'active_on_networks', network)

def _get_summaries(attr_dict, l, spl):
	if len(spl)>3 and spl[0] == 'area' and spl[2] == 'range':
		area = spl[1]
		subnet = spl[3]
		mask = to_dec_mask(spl[4])
		prefix = str(addressing(subnet+"/"+str(mask)))
		range_op_dict = add_blankdict_key(attr_dict, 'area')
		area_dict = add_blankdict_key(range_op_dict, area)
		append_attribute(area_dict, 'area-summaries', prefix)

	elif len(spl)>=3 and spl[0] == 'summary-address':
		subnet = spl[1]
		mask = to_dec_mask(spl[2])
		prefix = str(addressing(subnet+"/"+str(mask)))
		ext_summary_dict = add_blankdict_key(attr_dict, 'external-summaries')
		summary_pfx_dict = add_blankdict_key(ext_summary_dict, prefix)
		if "not-advertise" in spl:
			append_attribute(summary_pfx_dict, 'advertise', False)
		if "nssa-only" in spl:
			append_attribute(summary_pfx_dict, 'nssa-only', True)
		if "tag" in spl:
			tag = spl[spl.index('tag') +1]
			append_attribute(summary_pfx_dict, 'tag', tag)

def _get_area_types(attr_dict, l, spl):
	ospf_area_types = {'stub', 'nssa'}
	if len(spl)>2 and spl[0] == 'area' and spl[2] in ospf_area_types:
		area = spl[1]
		range_op_dict = add_blankdict_key(attr_dict, 'area')
		area_dict = add_blankdict_key(range_op_dict, area)
		totally = "Totally " if spl[-1] == 'no-summary' else ""
		area_type = totally + spl[2]
		append_attribute(area_dict, 'area_type', area_type)

def _get_area_default_cost(attr_dict, l, spl):
	if len(spl)>2 and spl[0] == 'area' and spl[2] == 'default-cost':
		area = spl[1]
		range_op_dict = add_blankdict_key(attr_dict, 'area')
		area_dict = add_blankdict_key(range_op_dict, area)
		append_attribute(area_dict, 'default-cost', spl[-1])

def _get_transit_area(attr_dict, l, spl):
	if len(spl)>2 and spl[0] == 'area' and spl[2] == 'virtual-link':
		area = spl[1]
		router_id = spl[3]
		attribs = ('authentication', 'hello-interval', 'retransmit-interval', 'transmit-delay',
			'dead-interval', )
		auth_attribs = ('authentication-key', 'message-digest-key', 'md5')
		attrib_dict = {attr: spl[spl.index(attr)+1] for attr in attribs if attr in spl}
		auth_attrib_dict = {}
		for attr in auth_attribs:
			if attr in spl:
				try:
					auth_attrib_dict[attr] = decrypt_type7( spl[spl.index(attr)+1])
				except:
					auth_attrib_dict[attr] = spl[spl.index(attr)+1]
		#
		range_op_dict = add_blankdict_key(attr_dict, 'area')
		area_dict = add_blankdict_key(range_op_dict, area)
		append_attribute(area_dict, 'area_type', 'transit')
		append_attribute(area_dict, 'router-id', router_id)
		merge_dict(area_dict, attrib_dict)
		merge_dict(area_dict, auth_attrib_dict)

def _get_neighbors(attr_dict, l, spl):
	if len(spl)>1 and spl[0] == 'neighbor':
		nbrs_dict = add_blankdict_key(attr_dict, 'neighbors')
		nbr_dict = add_blankdict_key(nbrs_dict, spl[1])
		if 'cost' in spl:
			nbr_dict['cost'] = spl[spl.index('cost')+1]			
		if 'database-filter' in spl:
			dfidx = spl.index('database-filter')
			nbr_dict['database-filter'] = {'filter': spl[dfidx+1], 'direction': spl[dfidx+2]}			

def _get_ospf_cost(attr_dict, l, spl):
	if l.startswith("ip ospf cost "):
		attr_dict['cost'] = spl[-1]

def _get_ospf_priority(attr_dict, l, spl):
	if l.startswith("ip ospf priority "):
		attr_dict['priority'] = spl[-1]

def _get_ospf_intervals(attr_dict, l, spl):
	if len(spl) > 2 and spl[2] in ('hello-interval', 'dead-interval'):
		op_dict = add_blankdict_key(attr_dict, 'intervals')
		for interval in ('hello', 'dead'):
			if spl[2].startswith(interval):
				op_dict[interval] = spl[-1]

def _get_ospf_auto_cost_ref_bw(attr_dict, l, spl):
	if l.startswith("auto-cost reference-bandwidth "):
		attr_dict['auto-cost reference-bandwidth'] = spl[-1]

def _get_redistribution(attr_dict, l, spl):
	if spl[0] == 'redistribute':
		protocol = spl[1]
		protocol_id = spl[2]
		attribs = {'metric', 'metric-type', 'match', 'tag', 'route-map'}
		static_attribs = {'subnets', 'nssa-only'}
		attrib_dict = {attr: spl[spl.index(attr)+1] for attr in attribs if attr in spl}
		op_dict = add_blankdict_key(attr_dict, 'redistribute')
		protocol_dict = add_blankdict_key(op_dict, protocol)
		protocol_id_dict = add_blankdict_key(protocol_dict, protocol_id)
		for attr in static_attribs:
			if attr in spl:
				append_attribute(protocol_id_dict, attr, True)
		merge_dict(protocol_id_dict, attrib_dict)



# ====================================================================================================
#  OSPF Config extractor Class
# ====================================================================================================

@dataclass
class OSPF(ProtocolsConfig):
	run_list: list[str] = field(default_factory=[])

	attr_functions = [
		_get_router_id,
		_get_active_interfaces,
		_get_networks,
		_get_summaries,
		_get_neighbors,
		_get_ospf_cost,
		_get_ospf_priority,
		_get_ospf_intervals,
		_get_area_types,
		_get_area_default_cost,
		_get_transit_area,
		_get_ospf_auto_cost_ref_bw,
		_get_redistribution,
	]

	def __post_init__(self):
		self.protocol_config_initialize(protocol='ospf')
		self.ospf_vrf_dict = self.protocol_vrf_dict
		self._iterate_vrfs()
		self.remove_empty_vrfs(self.ospf_vrf_dict)


	def _iterate_vrfs(self):
		for process_id, lines in self.vrfs.items():
			self.ospf_vrf_dict[process_id].update( self._get_attributes(lines))


# ====================================================================================================
#  RIP Config extractor function
# ====================================================================================================

def get_ospf_running(command_output):
	"""parse output of : show running-config

	Args:
		command_output (list): command output

	Returns:
		dict: protocols ospf and ospfv6 level parsed output dictionary
	"""    	
	O  = OSPF(command_output)
	return get_protocol_instance_dict(protocol='ospf', instances_dic=O.ospf_vrf_dict)
	
# ====================================================================================================
