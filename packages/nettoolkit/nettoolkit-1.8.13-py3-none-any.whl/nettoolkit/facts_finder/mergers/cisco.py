
from nettoolkit.facts_finder.modifiers import cisco_modifier
from .common import Merged

# ========================================================================================

class CiscoMerge(Merged):
	"""Class which merges generator and modifier data for Cisco. 
	Inherits Merged class

	Args:
		fg (generator object): Facts generator object from generators
		capture_tfsm_file (str): file name of configuration capture 
		use_cdp (bool): defines for cisco use cdp neighbors or not. Some cases where lldp is disabled using cdp to identify neighbors.

	"""	

	def __init__(self, fg, capture_tfsm_file, use_cdp):
		"""object initializer for cisco merger class.
		"""		
		super().__init__(fg, capture_tfsm_file, use_cdp)

	def __call__(self):
		"""object call,  merger execution steps by step
		"""		
		if not self.capture_tfsm_file: return None
		self.get_facts_modifiers()

		self.merged_var_dataframe()			# self.var_df
		self.merged_interfaces_dataframe()	# self.int_df
		self.merged_vrfs_dataframe()		# self.vrf_df
		self.bgp_dataframe()
		self.ospf_dataframe()
		self.static_dataframe()

		self.generate_interface_numbers()
		self.split_interface_dataframe()
		self.add_filters()

		self.add_fg_dfs()

	def get_facts_modifiers(self):
		"""retrives cisco modifier databse in a dictionary format and store it within object as pdf_dict
		"""		
		self.pdf_dict = cisco_modifier(self.capture_tfsm_file, use_cdp=self.use_cdp)


	def add_fg_dfs(self):
		"""add facts generator data frames to merged dictionary
		"""		
		self.fg_merged_dict = {
			'var': self.fg_var_df,
			'vrf': self.fg_vrf_df,
			'bgp': self.fg_bgp_df,

		}