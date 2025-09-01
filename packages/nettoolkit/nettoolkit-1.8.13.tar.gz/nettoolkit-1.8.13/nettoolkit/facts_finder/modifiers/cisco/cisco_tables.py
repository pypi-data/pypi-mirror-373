"""cisco tables modifiers 
"""

from nettoolkit.addressing import *
import pandas as pd
import numpy as np

from .commands.cmd_dict import *
from nettoolkit.facts_finder.modifiers.commons import *

# ================================================================================================
# Functions for DataFrame Modification Apply
# ================================================================================================

def nbr_hostname(hn):
	"""neighbour hostname split by domain and return striped hostname

	Args:
		hn (str): hostname string full dns

	Returns:
		str: hostname trunkated
	"""	
	return hn.split(".")[0]

def h4block(ipv6addr):
	"""check for the ipv6 string(s) and from the address returns either 4th or 7th block

	Args:
		ipv6addr (list, set, tuple): list of IPV6 address strings.

	Returns:
		str: 4th > 7th octet > Growable
	"""	
	try:
		l = eval(ipv6addr)
	except: return ""
	if isinstance(l, (list, set, tuple)):
		try:
			v6 = IPv6(l[-1][:-2]+"/64")
			#
			block = v6.get_hext(4)  # for major assignments
			if block and block!='0':
				return block
			#
			block = v6.get_hext(7)  # for minor assignments
			if block and block!='0':
				return block
			#
			# -- add more as needed.
			#
			return ""
		except: 
			pass
	return ""

def interface_mode(mode):
	"""check for the mode string if it is starting with trunk/access. returns appropriate mode accordingly

	Args:
		mode (str): interface mode type string (trunk, access)

	Returns:
		str: interface mode calculated
	""" 
	if mode.startswith("trunk"): return "trunk"
	if mode.startswith("access"): return "access"
	return ""

def vlan_members(members):
	"""check for the given vlan members and returns vlan numbers separated by comma.  will return no string if default/all 

	Args:
		members (str): vlan members string

	Returns:
		str: updated members string
	"""
	if members == "['ALL']": return ""
	if members == "": return ""
	return members.replace("'", "").replace("[", "").replace("]", "")

def filter_col(filtercol):
	"""check for the interface type column and maps it with well known interface type filters
	Growable.

	Args:
		filtercol (str): interface type filter column name (key)

	Returns:
		str: corresponding standard mapped value for interface type
	"""	
	filter_map = {
		'Ethernet SVI': 'vlan',
		'EtherChannel' : 'aggregated',
		'Loopback': 'loopback',
		'EtherSVI': 'vlan',		
		'Tunnel': 'tunnel',		

		## -- add as and when new interface type found -- ##
	}
	if filtercol in filter_map:
		return filter_map[filtercol]
	return 'physical'

def subnet(addr):
	"""get the subnet/network ip detail for the interface ip address

	Args:
		addr (str): ipv4 address/subnet string

	Returns:
		str: network address
	"""
	if not addr:
		return addr
	try:
		return IPv4(addr).n_thIP(0, withMask=True)
	except:
		addr

def intvrf_update(vrf):
	"""get the vrf name except management vrfs

	Args:
		vrf (str): vrf name

	Returns:
		str: vrf name if not management vrf
	"""	
	if vrf.lower() in ('mgmt-vrf', ): 
		return ""
	return vrf


# ================================================================================================
# Cisco Database Tables Object
# ================================================================================================
class TableInterfaceCisco(DataFrameInit, TableInterfaces):
	"""Cisco Database Tables Object

	Args:
		capture (str): configuration capture log file
		cmd_lst (list, optional): cisco capture command list. Defaults to None.
		use_cdp (bool, optional): use cdp neighbors (overrides lldp neighbor). Defaults to None.

	Inherits:
		DataFrameInit (cls): DataFrameInit
		TableInterfaces (cls): TableInterfaces
	"""	

	def __init__(self, capture, cmd_lst=None, use_cdp=None):
		"""instance initializer

		"""		
		self.cmd_lst=cmd_lst
		self.use_cdp = use_cdp
		if not self.cmd_lst:
			self.cmd_lst = cmd_lst_int
		super().__init__(capture)
		self.pdf = pd.DataFrame({"interface":[]})

	def __call__(self):
		self.merge_interface_data()
		self.remove_duplicates()
		self.po_to_interface()
		self.update_functional_cols()
		self.update_neighbor_intf()
		self.update_intf_vrf()

	## Calls

	def merge_interface_data(self):
		"""merges interface related data frames from the parsed excel sheet command output 
		which was originated from capture_it along with ntctemplate.
		DataFrame: A single pandas dataframe clubbed with all interface related details. 
		"""
		# Note: Some of the duplicate columns will get generated during merge 
		#       which will be taken care in next step
		pdf = pd.DataFrame({'interface':[]})
		for sheet, df in self.dfd.items():
			if sheet not in self.cmd_lst: continue
			if sheet == 'show cdp neighbors detail' and not self.use_cdp: continue 
			#
			ndf = df[ self.cmd_lst[sheet].keys() ]
			ndf = ndf.rename(columns=self.cmd_lst[sheet])
			ndf['interface'] = ndf['interface'].apply(lambda x: STR.if_standardize(x, True))
			pdf = pd.merge( ndf, pdf, on=['interface',], how='outer').fillna("")
		self.pdf = pdf

	def remove_duplicates(self):
		""" merges the duplicate columns _x, _y generated during dataframe merge, and removes extra column. 
		"""
		duplicated_cols = {									## Something to do to get this dynamically.
			'//nbr_hostname_x': '//nbr_hostname_y', 
			'nbr_interface_x': 'nbr_interface_y',
			'nbr_ip_x': 'nbr_ip_y',
		}
		for x, y in duplicated_cols.items():
			try:
				if self.pdf[x].equals(self.pdf[y]):
					self.pdf.rename(columns={x: x[:-2]}, inplace=True)
				else:
					self.pdf[x[:-2]] = np.where( self.pdf[x]!="", self.pdf[x], self.pdf[y]) 
					self.pdf.drop([x], axis=1, inplace=True)
				self.pdf.drop([y], axis=1, inplace=True)
			except:
				pass
				# print(f"Info: duplicate col removal not happen for {x}")

	def po_to_interface(self):
		"""add port channel number to member interfaces 
		"""
		sht = 'show etherchannel summary'
		sht_df = self._is_sheet_data_available(self.dfd, sht)
		if sht_df is None or sht_df is False: return None
		col_to_drop = self.cmd_lst[sht]['interfaces']
		#
		pos = sht_df['po_name']
		intfs = sht_df['interfaces']
		int_dict = {'interface':[],'channel_grp':[]}
		for po, ints in zip(pos, intfs):
			channel_group_no = po[2:]
			ints = eval(ints)
			for i in ints:
				int_dict['interface'].append(STR.if_standardize(i))
				int_dict['channel_grp'].append(channel_group_no)
		df = pd.DataFrame(int_dict)
		self.pdf = pd.merge(self.pdf , df, on=['interface',], how='outer').fillna("")
		self.pdf.drop([col_to_drop,], axis=1, inplace=True)

	def update_functional_cols(self):
		"""update functional columns values
		"""
		func_cols = {			# list of - functional columns and its respective filter function
			'//nbr_hostname': nbr_hostname,
			'//h4block': h4block,
			'//interface_mode': interface_mode,
			'//vlan_members': vlan_members,
			'//filter': filter_col,
			'//subnet': subnet,
		}
		for col, func in func_cols.items():
			try:
				self.pdf[col[2:]] = self.pdf[col].apply(func)
				self.pdf.drop([col,], axis=1, inplace=True)
			except:
				print(f"Warning: Missing detail found in database {col}, mostly a key output capture failed.  Further processing may fail due to missing elements.")

	def update_neighbor_intf(self):
		"""standardize neighbor interface length 
		"""
		self.pdf['nbr_interface'] = self.pdf['nbr_interface'].apply(lambda x: STR.if_standardize(x, True))

	def update_intf_vrf(self):
		"""update the interface vrf column (if any) by removing management vrfs 
		"""
		try:
			self.pdf['intvrf']
		except:
			return None
		if self.pdf['intvrf'].empty: return None

		self.pdf['intvrf'] = self.pdf['intvrf'].apply(intvrf_update)


# ================================================================================================
