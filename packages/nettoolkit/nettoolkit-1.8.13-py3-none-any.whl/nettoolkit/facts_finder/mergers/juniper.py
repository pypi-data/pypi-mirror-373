
from nettoolkit.facts_finder.modifiers import juniper_modifier
from .common import Merged

# ========================================================================================
def add_access_vlan_column(port_mode, vlan):
	"""get access vlan number if port_mode is `access`

	Args:
		port_mode (str): port mode access/trunk etc..
		vlan (str): string of list of vlans

	Returns:
		str: allowed vlan number (if access port)
	"""	
	if port_mode == 'access':
		return eval(f'{vlan}[0]')
	return ""

# ========================================================================================

class JuniperMerge(Merged):
	"""Class which merges generator and modifier data for Juniper. 
	Inherits Merged class

	Args:
		fg (generator object): Facts generator object from generators
		capture_tfsm_file (str): file name of configuration capture 
		use_cdp (bool): defines for cisco use cdp neighbors or not. Some cases where lldp is disabled using cdp to identify neighbors.
	"""	

	def __init__(self, fg, capture_tfsm_file, use_cdp):
		"""object initializer for juniper merger class.
		"""	
		super().__init__(fg, capture_tfsm_file, use_cdp)

	def __call__(self):
		"""object call,  merger execution steps by step
		"""		
		self.get_facts_modifiers()

		self.merged_var_dataframe()			# self.var_df
		self.merged_interfaces_dataframe()	# self.int_df
		# self.merged_vrfs_dataframe()		# self.vrf_df
		self.add_vrf_dataframe()
		self.bgp_dataframe()
		self.ospf_dataframe()
		self.static_dataframe()

		self.generate_interface_numbers()
		self.split_interface_dataframe()
		self.add_access_vlan_column_on_physical()
		self.add_filters()

	def get_facts_modifiers(self):
		"""retrives juniper modifier databse in a dictionary format and store it within object as pdf_dict
		"""		
		self.pdf_dict = juniper_modifier(self.capture_tfsm_file)

	def add_access_vlan_column_on_physical(self):
		"""add a new `access_vlan` column to physical interfaces dataframe
		"""		
		physical_int_df = self.int_dfs['physical']
		physical_int_df['access_vlan'] = physical_int_df.apply(lambda x: add_access_vlan_column(x['port_mode'], x['vlan']), axis=1)

	def add_vrf_dataframe(self):
		"""add new dataframe `vrf` data using generator
		"""		
		fg_df = self.Fg['vrf'].reset_index()										## facts-gen dataframe
		fg_df.drop(fg_df[fg_df["vrf"] == "Mgmt-vrf"].index, axis=0, inplace=True)	## Remove row with management vrfs ( add more description for mgmt vrf )
		self.vrf_df = fg_df
		self['vrf'] = fg_df

