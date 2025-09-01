
import pandas as pd
import numpy as np

from nettoolkit.facts_finder.commons.common import *


# ========================================================================================

def remove_duplicates(df, *cols):
	"""removes the duplicated _x, _y columns for the given list of columns. Remove duplicate columns as given in additional keyword arguments cols 

	Args:
		df (DataFrame): Pandas DataFrame

	Returns:
		DataFrame: updated DataFrame
	"""	
	duplicated_cols = {col+"_x": col+"_y" for col in cols}
	for x, y in duplicated_cols.items():
		if df[x].equals(df[y]):
			df.rename(columns={x: x[:-2]}, inplace=True)
		else:
			df[x[:-2]] = np.where( df[x]!="", df[x], df[y]) 
			df.drop([x], axis=1, inplace=True)
		df.drop([y], axis=1, inplace=True)
	return df


def split_to_multiple_tabs(pdf):
	"""splits dataframe to multiple tabs group by `filter` column

	Args:
		pdf (DataFrame): Pandas DataFrame

	Returns:
		DataFrame: updated DataFrame
	"""	
	set_of_filters = set(pdf['filter'])
	d = {}
	for f in set_of_filters:
		df = pdf[ pdf['filter']==f ]
		d[f] = df		
	pdf = d
	return pdf



# ========================================================================================

class Merged:
	"""Common class defining general methods for mergers of generator and modifiers

	Args:
		fg (generator object): Facts generator object from generators
		capture_tfsm_file (str): file name of configuration capture 
		use_cdp (bool): defines for cisco use cdp neighbors or not. Some cases where lldp is disabled using cdp to identify neighbors.

	"""	
	def __init__(self, fg, capture_tfsm_file, use_cdp):
		"""object initializer
		"""		
		self.Fg = fg
		self.capture_tfsm_file = capture_tfsm_file
		self.use_cdp = use_cdp
		self.merged_dict = {}

	def __iter__(self):
		for k, v in self.merged_dict.items():
			yield k, v

	def __getitem__(self, item):
		return self.merged_dict[item]

	def __setitem__(self, item, value):
		if item != "":
			self.merged_dict[item] = value

	def merge_and_drop_empty_filter_rows(self, fg_df, fm_df, merge_on):
		"""merges generator and modifier dataframes and drops empty rows for data where no filter value assigned.

		Args:
			fg_df (DataFrame): generator DataFrame
			fm_df (DataFrame): modifier DataFrame
			merge_on (str, list): column(s) on which merge to happen

		Returns:
			DataFrame: merged DataFrame
		"""		
		if merge_on in fg_df.keys() and merge_on in fm_df.keys():
			pdf = pd.merge( fm_df, fg_df, on=[merge_on,], how='outer').fillna("")		## merged dataframe
			return pdf
		elif merge_on in fg_df.keys() and merge_on not in fm_df.keys():
			return fg_df
		elif merge_on not in fg_df.keys() and merge_on in fm_df.keys():
			return fm_df
		

	def merged_interfaces_dataframe(self):
		"""merges Interfaces generator and modifier dataframes and drops empty rows for data where no filter value assigned.
		"""		
		self.interface_types = set(self.pdf_dict['tables']['filter'])
		for int_type in self.interface_types:
			fg_df = self.Fg[int_type]
			fm_df = self.pdf_dict['tables'][self.pdf_dict['tables']['filter'] == int_type]
			pdf = self.merge_and_drop_empty_filter_rows(fg_df, fm_df, 'interface')
			self[int_type] = pdf

	def merged_vrfs_dataframe(self):
		"""merges vrf generator and modifier dataframes and drops empty rows for data where no filter value assigned.
		"""	
		fg_df = self.Fg['vrf'].reset_index()									## facts-gen dataframe
		fm_df = self.pdf_dict['vrf']											## facts-modifier dataframe
		self.fg_vrf_df = fg_df
		pdf = self.merge_and_drop_empty_filter_rows(fg_df, fm_df, 'vrf')
		pdf.drop(pdf[pdf["vrf"] == "Mgmt-vrf"].index, axis=0, inplace=True)	## Remove row with management vrfs ( add more description for mgmt vrf )
		self.vrf_df = pdf
		self['vrf'] = pdf

	def merged_var_dataframe(self):
		"""merges system/var generator and modifier dataframes and drops empty rows for data where no filter value assigned.
		"""	
		fg_df = self.Fg['var'].reset_index()									## facts-gen dataframe
		fm_df = self.pdf_dict['var']											## facts-modifier dataframe
		self.fg_var_df = fg_df
		pdf = pd.merge( fm_df, fg_df, on=['var',], how='outer').fillna("")		## merged dataframe	
		pdf = remove_duplicates(pdf, 'default')
		pdf.drop('index', axis=1, inplace=True)
		self.var_df = pdf
		self['var'] = pdf

	def bgp_dataframe(self):
		"""merges bgp generator and modifier dataframes and drops empty rows for data where no filter value assigned.
		"""	
		fg_df = self.Fg['bgp'].reset_index()
		self.fg_bgp_df = fg_df
		fg_df['filter'] = 'bgp'
		self['bgp'] = fg_df

	def ospf_dataframe(self):
		"""merges ospf generator and modifier dataframes and drops empty rows for data where no filter value assigned.
		"""	
		fg_df = self.Fg['ospf'].reset_index()
		self.fg_ospf_df = fg_df
		fg_df['filter'] = 'ospf'
		self['ospf'] = fg_df

	def static_dataframe(self):
		"""merges static generator and modifier dataframes and drops empty rows for data where no filter value assigned.
		"""	
		fg_df = self.Fg['static'].reset_index()
		self.fg_ospf_df = fg_df
		fg_df['filter'] = 'static'
		self['static'] = fg_df

	def split_interface_dataframe(self):
		"""splits interface dataframe in to multiple tabs.
		"""	
		pass

	def generate_interface_numbers(self):
		"""generates interface number for each interfaces 
		"""		
		for int_type in self.interface_types:
			generate_int_number(self[int_type])

	def add_filters(self):
		"""add filter column to each dataframe except 'var'
		"""		
		for sheet, df in  self:
			if sheet == 'var': continue
			if not 'filter' in df.columns:
				df['filter'] = sheet

	@property
	def hostname(self):
		"""self device property (hostname) from var tab

		Returns:
			str: hostname of device
		"""		
		try:
			return [x for x in self.var_df[self.var_df['var'] == 'hostname']['default']][0]
		except:
			return ""
