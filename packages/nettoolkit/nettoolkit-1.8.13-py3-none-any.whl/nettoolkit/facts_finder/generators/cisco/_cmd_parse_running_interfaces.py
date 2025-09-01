"""cisco show running-config parser for interface section outputs """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *

merge_dict = DIC.merge_dict
# ------------------------------------------------------------------------------

class RunningInterfaces():
	"""object for interface level running config parser

	Args:
		cmd_op (list, str): running config output, either list of multiline string
	"""    	

	def __init__(self, cmd_op):
		"""initialize the object by providing the running config output
		"""    		    		
		self.cmd_op = verifid_output(cmd_op)
		self.interface_dict = OrderedDict()

	def interface_read(self, func):
		"""directive function to get the various interface level output

		Args:
			func (method): method to be executed on interface config line

		Returns:
			dict: parsed output dictionary
		"""    		
		int_toggle = False
		ports_dict = OrderedDict()
		for l in self.cmd_op:
			if blank_line(l): continue
			if l.strip().startswith("!"): 
				int_toggle = False
				continue
			if l.startswith("interface "):
				p = get_interface_cisco(l)
				if not p: continue
				if not ports_dict.get(p): ports_dict[p] = {}
				port_dict = ports_dict[p]
				port_dict['filter'] = interface_type(l.split("interface ")[-1])[0].lower()
				int_toggle = True
				continue
			if int_toggle:
				func(port_dict, l)
		return ports_dict

	def interface_description(self):
		"""update the interface description details
		"""    		
		func = self.get_interface_description
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_interface_description(port_dict, l):
		"""parser function to update interface description details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		if l.strip().startswith("description "):
			port_dict['description'] = l.strip().split(" ", 1)[-1]

	def interface_state(self):
		"""update the interface status (up/down/disabled) details
		"""    		
		func = self.get_interface_state
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_interface_state(port_dict, l):
		"""parser function to update interface state details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		if l.strip().startswith("shutdown"):
			port_dict['link_status'] = 'administratively down'

	def interface_ips(self):
		"""update the interface ipv4 ip address details
		"""    		
		func = self.get_ip_details
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_ip_details(port_dict, l):
		"""parser function to update interface ipv4 ip address details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		address = get_inet_address(l)
		secondary_address = get_secondary_inet_address(l)
		if address: port_dict['subnet'] = get_subnet(address)
		if secondary_address: port_dict['subnet_secondary'] = get_subnet(secondary_address)


	def interface_v6_ips(self):
		"""update the interface ipv6 ip address details
		"""   
		func = self.get_ipv6_details
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_ipv6_details(port_dict, l):
		"""parser function to update interface ipv6 ip address details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		link_local = l.find("link-local") > -1
		if l.find("anycast") > -1: return None
		address = get_inetv6_address(l, link_local)
		if not address: return None
		if link_local:
			return None
		port_dict['v6subnet'] = get_v6_subnet(address)
		port_dict['h4block'] = IPv6(address).getHext(4)

	def interface_mode(self):
		"""update the interface mode details
		"""   
		func = self.get_int_mode_details
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_int_mode_details(port_dict, l):
		"""parser function to update interface mode details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		if l.strip().startswith('switchport mode '):
			port_dict['interface_mode'] = l.strip().split()[-1]


	def interface_vlans(self):
		"""update the interface vlan details
		"""   
		func = self.get_int_vlan_details
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_int_vlan_details(port_dict, l):
		"""parser function to update interface vlan details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		vlans = get_vlans_cisco(l.strip())
		if not vlans: return None
		for k, v in vlans.items():
			if v and port_dict.get(k): 
				port_dict[k] += ","+str(v)
			elif v and not port_dict.get(k): 
				port_dict[k] = v


	def interface_channel_group(self):
		"""update the interface port channel details
		"""   
		func = self.get_int_channel_group
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_int_channel_group(port_dict, l):
		"""parser function to update interface port channel details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		po = None
		if l.strip().startswith("channel-group"):
			spl = l.strip().split() 
			po = spl[1]
			po_mode = spl[-1]

		if not po: return None
		port_dict['channel_group_interface'] = "Port-channel" + po
		port_dict['channel_group_mode'] = po_mode
		port_dict['channel_group'] = po


	def interface_vrf(self):
		"""update the interface vrf details
		"""   
		func = self.get_int_vrf
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_int_vrf(port_dict, l):
		"""parser function to update interface vrf details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		vrf = None
		if (l.strip().startswith("vrf forwarding") 
			or l.strip().startswith("ip vrf forwarding")):
			vrf = l.strip().split()[-1]
		if not vrf: return None
		port_dict['intvrf'] = vrf


	def interface_udld(self):
		"""update the interface udld parameter details
		"""   
		func = self.get_int_udld
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_int_udld(port_dict, l):
		"""parser function to update udld parameter details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		udld = None
		if l.strip().startswith("udld port "):
			port_dict['int_udld'] = l.strip().split(" ", 2)[-1]
		if not udld: return None

	def interface_ospf_auth(self):
		"""update the interface ospf authentication details
		"""   
		func = self.get_int_ospf_auth
		merge_dict(self.interface_dict, self.interface_read(func))

	@staticmethod
	def get_int_ospf_auth(port_dict, l):
		"""parser function to update ospf authentication details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		auth, auth_type = None, None
		if l.strip().startswith("ip ospf authentication-key"):
			try:
				port_dict['ospf_auth'] = decrypt_type7(l.strip().split()[-1])
			except:
				port_dict['ospf_auth'] = l.strip().split()[-1]
		if l.strip().startswith("ip ospf network "):
			port_dict['ospf_auth_type'] = l.strip().split()[-1]
		if not auth and not auth_type: return None

	def interface_v4_helpers(self):
		"""update the interface ipv4 helpers details
		"""   
		func = self.get_interface_v4_helpers
		merge_dict(self.interface_dict, self.interface_read(func))


	@staticmethod
	def get_interface_v4_helpers(port_dict, l):
		"""parser function to update ipv4 helpers details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		if l.strip().startswith("ip helper-address"):
			if not port_dict.get('v4_helpers'):
				port_dict['v4_helpers'] = l.strip().split()[-1]
			else:
				port_dict['v4_helpers'] += '\n'+l.strip().split()[-1]

	def interface_v6_helpers(self):
		"""update the interface ipv6 helpers details
		"""   
		func = self.get_interface_v6_helpers
		merge_dict(self.interface_dict, self.interface_read(func))


	@staticmethod
	def get_interface_v6_helpers(port_dict, l):
		"""parser function to update ipv6 helpers details

		Args:
			port_dict (dict): dictionary with a port info
			l (str): string line to parse

		Returns:
			None: None
		"""    		
		if l.strip().startswith("ipv6 dhcp relay destination"):
			if not port_dict.get('v6_helpers'):
				port_dict['v6_helpers'] = l.strip().split()[-1]
			else:
				port_dict['v6_helpers'] += '\n'+l.strip().split()[-1]


	# # Add more interface related methods as needed.


# ------------------------------------------------------------------------------


def get_interfaces_running(cmd_op, *args):
	"""defines set of methods executions. to get various inteface parameters.
	uses RunningInterfaces in order to get all.

	Args:
		cmd_op (list, str): running config output, either list of multiline string

	Returns:
		dict: output dictionary with parsed with system fields
	"""    	
	R  = RunningInterfaces(cmd_op)

	R.interface_description()
	R.interface_ips()
	R.interface_v6_ips()
	R.interface_vlans()
	R.interface_mode()
	R.interface_vrf()
	R.interface_state()

	R.interface_channel_group()
	R.interface_ospf_auth()
	R.interface_udld()
	R.interface_v4_helpers()
	R.interface_v6_helpers()

	# # update more interface related methods as needed.
	if not R.interface_dict:
		R.interface_dict['dummy_int'] = ""

	return {'op_dict': R.interface_dict }

