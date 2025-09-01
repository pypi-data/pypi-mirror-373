
# import fields
from .cmn.common_fn import *
from nettoolkit.addressing import IPv4

# -----------------------------------------------------------------------------------------------

class Common():
	"""COMMON FUNCTIONALITY CLASS TO INHERIT 
	"""
	def __init__(self, table):
		self.table = table
		self.filter = self.__class__.__name__.lower()

	def __iter__(self):
		for key, data in self.table.items():
			if data['filter'].lower() == self.filter: 
				yield data

# -----------------------------------------------------------------------------------------------

class Vrf(Common):
	"""device vrf/instances

	Args:
		table (dict): dataframe dictionary

	Returns:
		Vrf: Instance of VRF

	Yields:
		Vrf: Instance of VRF
	"""	

	def vrf_not_none(self):
		"""condition: `vrf is not None` 

		Yields:
			data_slice: data from Row that matches condition
		"""		
		for data in self:
			if data['vrf'] != "":
				yield data

	def sorted(self):
		"""list of available vrfs sorted by `vrf` field.

		Returns:
			list: sorted vrfs
		"""		
		self.sorted_vrf = sorted([ _['vrf']  for _ in self.vrf_not_none() ])
		return  self.sorted_vrf

	def sorted_vpnids(self):
		"""list of available vpnids sorted.

		Returns:
			list: sorted vpnids
		"""		
		self.sorted_vpnids = sorted([ int(_['vrf_vpnid'])  for _ in self.vrf_not_none() if _['vrf_vpnid'] ])
		return self.sorted_vpnids

	def sorted_vrf_data(self):
		"""vrf data generator, sorted by vrf names

		Yields:
			data_slice: data for all vrf rows except vrf is none, sorted by vrf names
		"""		
		for vrf in self.sorted_vrf:
			for data in self.vrf_not_none():
				if data['vrf'] == vrf: 
					yield data
					break

	def sorted_vrf_data_by_vpnid(self):
		"""vrf data generator, sorted by vpnids

		Yields:
			data_slice: data for all vrf rows except vrf is none, sorted by vpnids
		"""		
		for vpnid in self.sorted_vpnids:
			for data in self.vrf_not_none():
				if data['vrf_vpnid'] and int(data['vrf_vpnid']) == vpnid: 
					yield data
					break

	def vrf_get(self, vrf):
		"""get a particular vrf data

		Args:
			vrf (str): vrf name

		Yields:
			data_slice: data for matching vrf row 
		"""		
		for data in self.vrf_not_none():
			if data['vrf'] == vrf: 
				yield data

# -----------------------------------------------------------------------------------------------

class Vlan(Common):
	"""device Vlan/instances

	Args:
		table (dict): dataframe dictionary

	Returns:
		Vlan: Instance of Vlan

	Yields:
		Vlan: Instance of Vlan
	"""	

	def __vlans_range(self, start, stop):
		for data in self:
			if start <= int(data['int_number']) < stop:
				yield data

	def _sorted_vl_range(self, start, stop):
		vlans = [ int(data['int_number']) for data in self if start <= int(data['int_number']) < stop ]
		return sorted(vlans)	

	def vlans_sorted_range(self, start, stop):
		"""yields data slice(s) for the vlans matching for the provided range

		Args:
			start (int): starting vlan number
			stop (int): ends vlan number

		Yields:
			data_slice: of matching vlan numbers
		"""		
		for vlan in self._sorted_vl_range(start, stop):
			for data in self:
				if start <= int(data['int_number']) < stop:
					if int(data['int_number']) == vlan:
						yield data
						break

	def vlan(self, n):
		"""returns data slice for the matching vlan number

		Args:
			n (int): vlan number

		Yields:
			data_slice: of matching vlan number
		"""		
		for data in self:
			if int(data['int_number']) == n:
				yield data
				break

	def of_instance(self, vrf):
		"""yields data slice(s) for the vrf matching with `intvrf` column

		Args:
			vrf (str): vrf name

		Yields:
			data_slice: of matching vrf with `intvrf`
		"""		
		for data in self:
			if data and data['intvrf'] == vrf: yield data

# -----------------------------------------------------------------------------------------------

class Bgp(Common):
	"""device Bgp/instances

	Args:
		table (dict): dataframe dictionary

	Returns:
		Bgp: Instance of Bgp

	Yields:
		Bgp: Instance of Bgp
	"""	

	def vrf_not_none(self):
		"""yields data slice(s) for the bgp information where `bgp_vrf` is not none

		Yields:
			data_slice: of matching bgp details
		"""		
		for data in self:
			if data['bgp_vrf'] != "":
				yield data

	def bgp_peers(self, vrf):
		"""yields data slice(s) for the bgp information where `bgp_vrf` matches with provided vrf name

		Args:
			vrf (str): vrf name

		Yields:
			data_slice: of matching bgp details
		"""		
		for data in self:
			if data['bgp_vrf'] == vrf:
				yield data

# -----------------------------------------------------------------------------------------------

class Physical(Common):
	"""device Physical/instances

	Args:
		table (dict): dataframe dictionary

	Returns:
		Physical: Instance of Physical

	Yields:
		Physical: Instance of Physical
	"""	

	def sorted(self):
		"""provides list of sorted interface numbers

		Returns:
			list: of interface numbers sorted
		"""		
		return  sorted([ int(_['int_number'])  for _ in self ])

	def uplinks(self):
		"""yields data slice(s) for the physical interface information,
		where `int_filter` information starts with uplink.

		Yields:
			data_slice: of matching physical interfaces details
		"""		
		for data in self:
			if data['int_filter'].lower().startswith('uplink'):
				yield data		

	def sorted_interfaces(self):
		"""yields data slice(s) for the sorted physical interfaces informations

		Yields:
			data_slice: sorted physical interfaces
		"""		
		for intf in self.sorted():
			for data in self:
				if int(data['int_number']) == intf:
					yield data
					break

	def interface(self, n):
		"""yields data slice(s) for the sorted physical interfaces informations

		Args:
			n (int): interface number

		Yields:
			data_slice: of matched interface
		"""		
		for data in self:
			if int(data['int_number']) == n:
				yield data
				break

	# @staticmethod     # removed since older python not support
	def interface_type(data, intf_type):
		"""condition: is provided dataslice is of given interface type

		Args:
			data (data_slice): Pandas DataFrame slice
			intf_type (str): interface type to be verify

		Returns:
			bool: result of condition
		"""		
		return data['int_filter'].lower().startswith(intf_type)

	# @staticmethod     # removed since older python not support
	def interface_type_ends(data, x):
		"""condition: is provided dataslice ends with given argument `x`

		Args:
			data (data_slice):  Pandas DataFrame slice
			x (str): interface type ending identifier to be verify with

		Returns:
			bool: result of condition
		"""		
		return data['int_filter'].lower().endswith(x)

# -----------------------------------------------------------------------------------------------

class Aggregated(Common):
	"""device Aggregated/instances

	Args:
		table (dict): dataframe dictionary

	Returns:
		Aggregated: Instance of Aggregated

	Yields:
		Aggregated: Instance of Aggregated
	"""	
	pass

# -----------------------------------------------------------------------------------------------

class Loopback(Common):
	"""device Loopback/instances

	Args:
		table (dict): dataframe dictionary

	Returns:
		Loopback: Instance of Loopback

	Yields:
		Loopback: Instance of Loopback
	"""	
	pass

# -----------------------------------------------------------------------------------------------

class Static(Common):
	"""device static

	Args:
		table (dict): dataframe dictionary

	Returns:
		Static: Instance of Static

	Yields:
		Static: Instance of Static
	"""	

	def version(self, ver):
		for data in self:
			if int(data['version']) == ver:
				yield data

	def has_nexthop(self):
		for data in self:
			if data['next_hop'] != "":
				yield data

	def default_route(self, default_route=True):
		for data in self:
			if (
				   ((data['prefix'] == "0.0.0.0/0" or data['prefix'] == "::/0") and default_route)
				or  (data['prefix'] != "0.0.0.0/0" and data['prefix'] != "::/0" and not default_route)
				):
				yield data

	def vrf(self, vrf):
		for data in self:
			if ((isinstance(vrf, str) and data['pfx_vrf'] == vrf)
				or (isinstance(vrf, (list, set, tuple)) and data['pfx_vrf'] in vrf)
				):
				yield data

# -----------------------------------------------------------------------------------------------

class Ospf(Common):
	"""device Ospf

	Args:
		table (dict): dataframe dictionary

	Returns:
		Ospf: Instance of Ospf

	Yields:
		Ospf: Instance of Ospf
	"""	
	def vrf(self, vrf=""):
		for data in self:
			if ((isinstance(vrf, str) and data['ospf_vrf'] == vrf)
				or (isinstance(vrf, (list, set, tuple)) and data['ospf_vrf'] in vrf)
				):
				yield data

	def area_summary_tupples(self):
		for data in self:
			for pfx, area in zip(str_to_list(data['summary_prefixes']), str_to_list(data['summary_areas'])):
				yield area, pfx


# -----------------------------------------------------------------------------------------------


def sort(obj):
	"""exectes sorted method on provided object

	Args:
		obj (dynamic): Any object object instance declaring sorted method

	Returns:
		dynamic: sorted method output from object.
	"""	
	return obj.sorted()

