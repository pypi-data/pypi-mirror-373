"""cisco running-config - ip routes output parser """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *

merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningRoutes():
	"""object for running config routes parser
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the running config output

		Args:
			cmd_op (list, str): running config output, either list of multiline string
		"""    		
		self.cmd_op = verifid_output(cmd_op)
		self.route_dict = {}

	def route_read(self, func):
		"""directive function to get the various routes level output

		Args:
			func (method): method to be executed on ip routes config line

		Returns:
			dict: parsed output dictionary
		"""    		
		n = 0
		ports_dict = OrderedDict()
		for l in self.cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("!"): continue
			if not l.startswith("ip route ") and not l.startswith("ipv6 route "): continue
			#
			spl = l.strip().split()
			n += 1
			ports_dict[n] = {}
			rdict = ports_dict[n]
			rdict['filter'] = 'static'
			func(rdict,  l, spl)
		return ports_dict

	def routes_dict(self):
		"""update the route details
		"""   
		func = self.get_route_dict
		merge_dict(self.route_dict, self.route_read(func))

	@staticmethod
	def get_route_dict(dic, l, spl):
		"""parser function to update route details

		Args:
			dic (dict): blank dictionary to update a route info
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
		if spl[2] == 'vrf':  idx_update += 2
		#
		prefix, next_hop, idx_update = get_pfx_nh_idxdist(version, spl, idx_update)
		#
		dic['version'] = version
		dic['pfx_vrf'] = get_singel_idx_item('vrf', spl)
		dic['prefix'] = prefix
		dic['next_hop'] = next_hop
		dic['adminisrative_distance'] = get_administrative_dist(spl, next_hop, idx_distance=idx_update)
		dic['tag_value'] = get_singel_idx_item('tag', spl)
		dic['remark'] = get_multi_idx_item('name', spl)
		dic['track'] = get_singel_idx_item('track', spl)
		return dic





# ------------------------------------------------------------------------------


def get_system_running_routes(cmd_op, *args):
	"""defines set of methods executions. to get various ip route parameters.
	uses RunningRoutes in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""
	R  = RunningRoutes(cmd_op)
	R.routes_dict()


	# # update more interface related methods as needed.
	if not R.route_dict:
		R.route_dict['dummy_col'] = ""

	return {'op_dict': R.route_dict }

# ------------------------------------------------------------------------------

def index_of(item, lst):
	"""index of an item from list

	Args:
		item (str): item
		lst (list): list of items

	Returns:
		int: index of found item else ``
	"""	
	if item in lst:
		return lst.index(item)
	return ""

def get_singel_idx_item(item, lst):
	"""gives next item if found item from list

	Args:
		item (str): item
		lst (list): list of items

	Returns:
		str: Next index item found in list
	"""	
	idx = index_of(item, lst)
	if idx: return lst[idx+1]
	return ""

def get_multi_idx_item(item, lst):
	"""get multi indexex item from list

	Args:
		item (str): item
		lst (list): list of items

	Returns:
		str: index till end of list
	"""	
	candidates = {'vrf', 'Null0', 'tag', 'name', 'track'}
	my_idx = index_of(item, lst)
	if not my_idx: return ""
	max_idx = len(lst)
	others_idx = {index_of(c, lst):c for c in candidates if index_of(c, lst)}
	for k in sorted(others_idx.keys()):
		if k > my_idx:
			max_idx = k
			break
	return " ".join(lst[my_idx+1:max_idx])

def get_administrative_dist(spl, next_hop, idx_distance):
	"""get administrative distance value from ip route command list

	Args:
		spl (list): ip route command splitted
		next_hop (str): next hop value
		idx_distance (int): index distance

	Returns:
		str: value of administrative distance configured or ``
	"""	
	adminisrative_distance = ''
	if (
			('Null0' in spl and len(spl)>=idx_distance+6 and spl[idx_distance+5].isnumeric())
		or 	(next_hop != '' and len(spl)>=idx_distance+5 and spl[idx_distance+4].isnumeric())
		):
		adminisrative_distance = get_singel_idx_item('Null0', spl)
	return adminisrative_distance

def get_pfx_nh_idxdist(version, spl, idx_distance):
	"""get tuple of prefix, nexthop, indexdistance for give ip route split line

	Args:
		version (int): ip route version
		spl (list): list of splitted ip route command
		idx_distance (int): index distance

	Returns:
		_type_: _description_
	"""	
	if version == 4:
		prefix, subnet_mask, next_hop = spl[idx_distance+2], spl[idx_distance+3], ''
		prefix = inet_address(prefix, subnet_mask)
		nh = spl[idx_distance+4]
		try:
			addressing(nh)
			next_hop = nh
			idx_distance += 1
		except:
			pass
	elif version == 6:
		prefix, next_hop = spl[idx_distance+2], ''
		nh = spl[idx_distance+3]
		idx_distance -= 1
		try:
			addressing(nh)
			next_hop = nh
			idx_distance += 1
		except:
			pass
	return (prefix, next_hop, idx_distance)