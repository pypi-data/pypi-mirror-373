
import pandas as pd
from copy import deepcopy, copy
from nettoolkit.nettoolkit_db import *
from nettoolkit.nettoolkit_common import *
from nettoolkit.nettoolkit.forms.formitems import get_cable_n_connectors, add_cable_n_connectors, CONNECTOR_TYPES_FILE
from .devices import AdevDevices, device_df_drop_empty_duplicates, update_var_df_details_to_table_df
from .cablings import ADevCablings
from .maths import CalculateXY, CalculateXYNative
from .general import *

pd.set_option('mode.chained_assignment', None)


# ------------------------------------------------------------------------- 
CABLING_COLUMNS = ['a_device', 'a_dev_model', 'a_dev_serial', 'aport', 'a_media_type', 'a_connector_type', 
	'b_device', 'b_dev_model', 'b_dev_serial', 'bport',  'b_media_type', 'b_connector_type', 
	'cable_type', 'speed', 'cable',
]
VISIO_DRAWING_COLUMNS= [
	'connector_type', 'color', 'pattern', 'weight',
]
# --------------------------------------------- 
# Data Frame Generator
# --------------------------------------------- 
class DFGen():
	"""DataFrame generator

	Args:
		files (list): list of input excel -clean files 
	"""	
	def __init__(self, files):
		"""initializer of DF Generator
		"""		
		self.files = sorted(files)
		self.default_stencil = None
		self.default_x_spacing = 3.5
		self.default_y_spacing = 2
		self.line_pattern_style_separation_on = None
		self.line_pattern_style_shift_no = 2
		self.weight = DEFAULT_LINE_WT
		self.func_dict = {}
		self.var_func_dict = {
			'hostname': get_dev_hostname,
			'device_model': get_dev_model,
			'serial_number': get_dev_serial,
		}
		self.pattern = 1
		self.blank_dfs()
		self.color_map = {
			'aoc': 'red',
			'copper': 'darkgray',
			'fiber om3 mm': 'skyblue',
			'fiber om4 mm': 'skyblue',
			'fiber mm': 'green',
			'fiber sm': 'yellow',
			#
			# ... add more as and when need ... #
			# --- adding new color will require respective edit in visio.py ---
		}


	def blank_dfs(self):
		"""creates devices/cabling blank DataFrames
		"""		
		self.devices_merged_df = pd.DataFrame({'hostname':[]})
		self.cabling_merged_df = pd.DataFrame({'a_device':[]})

	def custom_attributes(self, **kwargs):
		"""add/update custom attributes for object
		"""		
		for k, v in kwargs.items():
			if v:
				self.__dict__[k] = v

	def custom_functions(self, **kwargs):
		"""add/update custom functions for object
		"""		
		for k, v in kwargs.items():
			self.func_dict[k] = v

	def custom_var_functions(self, **kwargs):
		"""add/update custom `var` tab functions for object
		"""		
		for k, v in kwargs.items():
			self.var_func_dict[k] = v

	def __call__(self):
		self.run()

	def run(self):
		"""iterate over all files for generating devices/cabling DataFrame details.
		"""		
		self.DCT = {}
		for file in self.files:
			DCT = DF_ConverT(file, self.default_stencil, self.line_pattern_style_separation_on, self.line_pattern_style_shift_no)
			DCT.get_self_details(self.var_func_dict)
			DCT.convert(self.func_dict)
			self.update_devices_df(DCT, file)
			self.update_cabling_df(DCT, file)
			self.DCT[DCT.hostname] = DCT
		#
		self.devices_merged_df = device_df_drop_empty_duplicates(self.devices_merged_df)
		self.devices_merged_df = update_var_df_details_to_table_df(self.devices_merged_df, self.DCT, self.var_func_dict)
		#
		self.cabling_merged_df.reset_index(inplace=True)
		self.add_b_device_media_types()
		self.add_cable_connector_details()
		#
		self.remove_subintf_from_ports()
		self.standardize_intf_on_ports()
		self.remove_duplicate_cablings()
		self.add_model_n_serial_number_to_cabling()
		#
		#
		self.update_weight()
		if not self.__dict__.get('color'): self.update_color()
		# ---------------------------------------- #
		#
		self.df_dict = {'Devices': self.devices_merged_df, 'Cablings': self.cabling_merged_df }
		#

	def map_color(self, **kwargs):
		"""add, edit  line color map
		"""    		
		for k, v in kwargs.items():
			self.color_map[k] = v

	def arrange_cablings(self, keep_all_cols=True):
		"""arrange cabling tab in to appropriate order given in CABLING COLUMNS
		"""		
		cabeling_columns = set(self.df_dict['Cablings'].columns)
		extra_cols = cabeling_columns.difference(set(CABLING_COLUMNS)).difference(set(VISIO_DRAWING_COLUMNS))
		arranged_cols = copy(CABLING_COLUMNS)
		if keep_all_cols:
			arranged_cols += VISIO_DRAWING_COLUMNS
			arranged_cols += extra_cols
		self.df_dict['Cablings'] = self.df_dict['Cablings'][arranged_cols]

	def update(self, *funcs):
		for f in funcs:
			f(self.df_dict)

	def update_devices_df(self, DCT, file):
		"""update Devices DataFrame

		Args:
			DCT (DF_ConverT): DataFrame Convertor object
			file (str): a single database. -clean excel file. ( not in use )
		"""		
		ddf = DCT.update_devices()
		#
		ddf_dev = DCT.update_device_self_detils(self.func_dict)
		ddf = pd.concat([ddf, ddf_dev], axis=0, join='outer')
		#
		self.devices_merged_df = pd.concat([self.devices_merged_df, ddf], axis=0, join='outer')

	def update_cabling_df(self, DCT, file):
		"""update Cabling DataFrame

		Args:
			DCT (DF_ConverT): DataFrame Convertor object
			file (str): a single database. -clean excel file.
		"""		
		cdf = DCT.update_cablings(**self.__dict__)
		#
		self.cabling_merged_df = pd.concat([self.cabling_merged_df, cdf], axis=0, join='outer')

	def calculate_cordinates(self, sheet_filter_dict={}):
		"""calculate the x,y coordinate values for each devices and keep Devices, Cablings DataFrame Dictionary ready.

		Args:
			sheet_filter_dict (dict): sheet filter dictionary for mutitab executions.
		"""		
		if self.cabling_merged_df.empty: return

		if 'hierarchical_order' in self.func_dict:
			CXY = CalculateXY(self.devices_merged_df, self.default_x_spacing, self.default_y_spacing, self.cabling_merged_df, sheet_filter_dict)
			CXY.calc()
		else:
			CXY = CalculateXYNative(self.devices_merged_df, self.cabling_merged_df, sheet_filter_dict)
			CXY.calc()

		self.df_dict = {'Devices': CXY.df, 'Cablings': self.cabling_merged_df }


	def remove_duplicate_cablings(self):
		"""removes redundant cabling entries between two devices with same port identified
		"""
		self.cabling_merged_df["a_dev_duplicate"] = self.cabling_merged_df.b_device
		self.cabling_merged_df["aport_duplicate"] = self.cabling_merged_df.bport
		self.cabling_merged_df["b_dev_duplicate"] = self.cabling_merged_df.a_device
		self.cabling_merged_df["bport_duplicate"] = self.cabling_merged_df.aport
		self.cabling_merged_df = remove_duplicates(self.cabling_merged_df)
		self.cabling_merged_df = self.cabling_merged_df.drop(
			columns=["a_dev_duplicate", "aport_duplicate", "b_dev_duplicate", "bport_duplicate"]
		)
		self.cabling_merged_df = merge_port_for_duplicates(self.cabling_merged_df)		

	def remove_duplicate_cabling_entries(self):
		"""removes duplicate cabling entries between a-b devices / deprycated.
		"""		
		a_to_b = {}
		copy_full_df = deepcopy(self.cabling_merged_df)
		for i, data in copy_full_df.iterrows():
			if not a_to_b.get(data.a_device):
				a_to_b[data.a_device] = {'remotedev':[]}
			if data.b_device in a_to_b.keys() and data.a_device in a_to_b[data.b_device]['remotedev']:
				self.cabling_merged_df.drop(i, inplace=True)
				continue
			if data.a_device in a_to_b.keys() and data.b_device in a_to_b[data.a_device]['remotedev']:
				self.cabling_merged_df.drop(i, inplace=True)
				continue
			a_to_b[data.a_device]['remotedev'].append(data.b_device)

	def remove_undefined_cabling_entries(self):
		"""removes undefined cabling entries where device doesn't exist in devices tab / deprycated
		"""		
		dev_hosts = set(self.devices_merged_df.hostname) 
		copy_full_df = deepcopy(self.cabling_merged_df)
		for i, data in copy_full_df.iterrows():
			if not data.a_device in dev_hosts or not data.b_device in dev_hosts:
				self.cabling_merged_df.drop(i, inplace=True)
				continue

	def add_b_device_media_types(self):
		"""add b-device media types to database
		"""		
		self.cabling_merged_df['b_media_type'] = self.cabling_merged_df.apply(lambda x: 
				update_b_media_type(x.b_device, x.bport, self.DCT), axis=1)

	def add_cable_connector_details(self):		
		"""add cable and connector details to database (such as: media_type, cable_type, connector_types, mediaspeed, cable-type )
		"""		
		self.additional_sfp_cts = {'media_type':[], 'cable_type': [],'_connector_type': [], 'speed':[]}
		self.cabling_merged_df['cable_type'] = self.cabling_merged_df.apply(lambda x: self.update_cable_connector(x, 'cable_type'), axis=1)
		self.cabling_merged_df['a_connector_type'] = self.cabling_merged_df.apply(lambda x: self.update_cable_connector(x, '_connector_type', 'a_media_type'), axis=1)
		self.cabling_merged_df['b_connector_type'] = self.cabling_merged_df.apply(lambda x: self.update_cable_connector(x, '_connector_type', 'b_media_type'), axis=1)
		self.cabling_merged_df['speed'] = self.cabling_merged_df.apply(lambda x: self.update_cable_connector(x, 'speed',), axis=1)
		self.cabling_merged_df['cable'] = self.cabling_merged_df.apply(lambda x: self.merge_cable_type(x), axis=1)

		add_cable_n_connectors(CONNECTOR_TYPES_FILE, **self.additional_sfp_cts)


	def merge_cable_type(self, df):
		"""checks a side and b side connectors, media speed and returns desired cable type

		Args:
			df (DataFrame): Pandas DataFrame (cabling)

		Returns:
			str: cable type (ex: lc to lc 10g Multimode OM3 Cable)
		"""		
		ac = df.a_connector_type if df.a_connector_type else "??"
		bc = df.b_connector_type if df.b_connector_type else "??"
		s = f"{ac} to {bc} {df.speed} {df.cable_type}"
		return s

	def update_cable_connector(self, cm_df, what, mt_col=None):
		"""common definition to update attributes: cable_type, connector_types, mediaspeed

		Args:
			cm_df (DataFrame): Pandas DataFrame (cabling)
			what (str): attribute name to be updated
			mt_col (str, optional): mediatype column name. Defaults to None.

		Returns:
			str: found atribute value
		"""		
		if mt_col is None:
			media_type = cm_df.a_media_type if cm_df.a_media_type else cm_df.b_media_type
		else:
			media_type = cm_df[mt_col]

		if not media_type: return ""
		if media_type in self.additional_sfp_cts['media_type']:
			try:
				if self.additional_sfp_cts[what][self.additional_sfp_cts['media_type'].index(media_type)]:
					return self.additional_sfp_cts[what][self.additional_sfp_cts['media_type'].index(media_type)]
			except:
				pass
		#
		c = get_cable_n_connectors(CONNECTOR_TYPES_FILE, what, media_type)
		if c: return c
		#
		c = input(f"Provide [{what}] - New SFP identified: [{media_type}]:")
		if c:
			self._update_additional_sfp_cts(media_type, what, c)
			return c
		#
		return ''

	# support to above
	def _update_additional_sfp_cts(self, media_type, what, c):
		if media_type not in self.additional_sfp_cts['media_type']:
			self.additional_sfp_cts['media_type'].append(media_type)
			for _ in {'cable_type', '_connector_type', 'speed'}: 
				self.additional_sfp_cts[_].append("")
		self.additional_sfp_cts[what][self.additional_sfp_cts['media_type'].index(media_type)] = c

	def update_weight(self):
		"""define thickness of connector
		"""		
		update_weight(self.cabling_merged_df, self.weight)

	def update_color(self):
		"""define color of connector
		"""		
		update_color(self.cabling_merged_df, self.color_map)

	def remove_subintf_from_ports(self):
		"""removes subninterface value/string from ports
		"""		
		self.cabling_merged_df['aport'] = self.cabling_merged_df['aport'].apply(lambda x: x.split(".")[0])
		self.cabling_merged_df['bport'] = self.cabling_merged_df['bport'].apply(lambda x: x.split(".")[0])

	def standardize_intf_on_ports(self):
		"""standardize all interfaces
		"""		
		self.cabling_merged_df['aport'] = self.cabling_merged_df['aport'].apply(lambda x: STR.intf_standardize_or_null(x, intf_type='PHYSICAL'))
		self.cabling_merged_df['bport'] = self.cabling_merged_df['bport'].apply(lambda x: STR.intf_standardize_or_null(x, intf_type='PHYSICAL'))

	def add_model_n_serial_number_to_cabling(self):
		"""cabling tab - add device model and serial numbers
		"""		
		self.cabling_merged_df['a_dev_model'] = self.cabling_merged_df.apply(lambda x: get_model_number(x, self.devices_merged_df, 'a_device'), axis=1)
		self.cabling_merged_df['b_dev_model'] = self.cabling_merged_df.apply(lambda x: get_model_number(x, self.devices_merged_df, 'b_device'), axis=1)
		self.cabling_merged_df['a_dev_serial'] = self.cabling_merged_df.apply(lambda x: get_serial_number(x, self.devices_merged_df, 'a_device'), axis=1)
		self.cabling_merged_df['b_dev_serial'] = self.cabling_merged_df.apply(lambda x: get_serial_number(x, self.devices_merged_df, 'b_device'), axis=1)

CableMatrix = DFGen

# --------------------------------------------------------------------------------------------------

def get_serial_number(df, devices_merged_df, device):
	"""get serial number for match device

	Args:
		df (DataFrame): Cable Matrix DataFrame
		devices_merged_df (DataFrame): Devices DetaFrame
		device (str): device hostname

	Returns:
		str: serial number of device
	"""	
	mini_dev_df = devices_merged_df[(devices_merged_df.hostname == df[device])]
	if mini_dev_df.empty: return ""
	idx = mini_dev_df.index[0]
	return mini_dev_df['serial_number'][idx]

def get_model_number(df, devices_merged_df, device):
	"""get model number for match device

	Args:
		df (DataFrame): Cable Matrix DataFrame
		devices_merged_df (DataFrame): Devices DetaFrame
		device (str): device hostname

	Returns:
		str: model number of device
	"""	
	mini_dev_df = devices_merged_df[(devices_merged_df.hostname == df[device])]
	if mini_dev_df.empty: return ""
	idx = mini_dev_df.index[0]
	return mini_dev_df['device_model'][idx]


def update_weight(df, base_weight=1):
	"""update line thickness for all connectors, where found multiple connectivities between two devices

	Args:
		df (DataFrame): Pandas DataFrame (cabling)
		base_weight (int, optional): base weight. Defaults to 1.
	"""	
	for i, v in df.iterrows():
		minidf = df[ (df.a_device == v.a_device) & (df.b_device == v.b_device) ]
		minidf_len = len(minidf)
		if minidf_len == 1:
			continue
		elif minidf_len > 1:
			df.loc[ ((df.a_device == v.a_device) & (df.b_device == v.b_device)), 'weight' ] = minidf_len * base_weight

def update_color(df, colors):
	"""update line color for all connectors, based on the found cable type.  Available options are 
	# ( white, black, red, green, skyblue, blue, yellow, gray, lightgray, darkgray, orange )

	Args:
		df (DataFrame): Pandas DataFrame (cabling)
	"""
	df.color = df.apply(lambda x: get_color(x, colors), axis=1)

def get_color(df, colors):
	"""get color of a connector

	Args:
		df (DataFrame): Pandas DataFrame (cabling)
		colors (dict): fibertype v/s color dictionary

	Returns:
		str: color for given found cable (Default: black)
	"""	
	if df.cable_type.lower() in colors:
		return colors[df.cable_type.lower()]
	return 'black'


def update_b_media_type(cable_df_b_device, cable_df_bport, DCT):
	"""update media type for b-end device.

	Args:
		cable_df_b_device (str): hostname of b-end device 
		cable_df_bport (str): connected b-end device port
		DCT (DF_ConverT): DataFrame Convertor object

	Returns:
		str: media type information detected for b-end device/port (Default: "")
	"""	
	if cable_df_b_device not in DCT: 
		return ""
	remote_ph_df = DCT[cable_df_b_device].full_df['physical']
	try:
		filtered_df = remote_ph_df[remote_ph_df['interface'] == STR.if_standardize(cable_df_bport)]
	except:
		print(f"[-] ERROR getting b-device info for port {cable_df_b_device} - {cable_df_bport}")
		return ""
	if filtered_df.empty: 
		return ""
	if 'media_type' not in  filtered_df.columns: return ""
	if not filtered_df.fillna("")['media_type'][filtered_df.index[0]]: return ""
	return filtered_df['media_type'][filtered_df.index[0]]


def remove_duplicates(df):
	"""removes duplicate cabling entries between a-b devices
	"""		
	#
	df2 = deepcopy(df)
	for i, v in df.iterrows():
		bdev = v.b_device
		bport = v.bport
		adev = v.a_device
		aport = v.aport
		minidf = df[(df.a_dev_duplicate == adev) & (df.aport_duplicate == aport) & (df.b_dev_duplicate == bdev) & (df.bport_duplicate == bport)]
		if minidf.empty:
			continue
		df2 = df2.drop(minidf.index)
		break
	if len(df) == len(df2): 
		return df2
	return remove_duplicates(df2)

def merge_port_for_duplicates(df):
	"""merge multiple cabling for a-b devices
	"""	
	df2 = deepcopy(df)
	for i, r in  df.iterrows():
		mdf = df[((df.a_device == r.a_device) & (df.b_device == r.b_device))]
		if len(mdf.a_device) == 1: 
			continue
		idx = 0
		for j, m in mdf.iterrows():
			if idx == 0:
				idx = j
				prv_aport = m.aport
				prv_bport = m.bport
				continue
			prv_aport += "\n"+m.aport
			prv_bport += "\n"+m.bport
			df2.at[idx, 'aport'] = prv_aport
			df2.at[idx, 'bport'] = prv_aport
			df2 = df2.drop(j)
		break
	if len(df) == len(df2): 
		return df2
	return merge_port_for_duplicates(df2)


# --------------------------------------------- 
# Data Frame Converter
# --------------------------------------------- 
class DF_ConverT():
	"""Data Frame Converter

	Args:
		file (str): a single database. -clean excel file.
		default_stencil (str): default visio stencil file.
		line_pattern_style_separation_on (str): column name on which line pattern separation should be decided on
		line_pattern_style_shift_no (int): line pattern change/shift number/steps
	"""	

	def __init__(self, file, 
		default_stencil, 
		line_pattern_style_separation_on, 
		line_pattern_style_shift_no,
		):
		"""object initializer
		"""		
		self.file = file
		self.full_df = read_xl(file)
		file = file.split("/")[-1].split("\\")[-1]
		self.self_device = file.split("-clean")[0].split(".")[0]
		#
		self.stencils = default_stencil
		self.line_pattern_style_separation_on = line_pattern_style_separation_on
		self.line_pattern_style_shift_no = line_pattern_style_shift_no


	def get_self_details(self, var_func_dict):
		"""update the value from var tab of var function dictionary

		Args:
			var_func_dict (dict): custom var functions dictionary
		"""		
		self.var_func_dict = var_func_dict
		for k,  f in var_func_dict.items():
			v = f(self.full_df['var'])
			if not v: v = 'N/A'
			self.__dict__[k] = v

	def convert(self, func_dict):
		"""create physical DataFrame, update with patterns  

		Args:
			func_dict (dict): custom functions dictionary
		"""		
		# vlan
		vlan_df = get_vlan_if_up(self.full_df['vlan'])
		vlan_df = get_vlan_if_relevants(vlan_df)
		self.vlan_df = vlan_df

		# physical
		df = get_physical_if_up(self.full_df['physical'])
		df = get_physical_if_relevants(df)
		#
		df = self.update_devices_df_pattern_n_custom_func(df, func_dict)
		#
		self.u_ph_df = df


	def update_devices_df_pattern_n_custom_func(self, df, func_dict):
		"""updates Devices DataFrame patterns as per custom functions provided in func_dict

		Args:
			df (DataFrame): pandas DataFrame for devices
			func_dict (dict): custom functions dictionary

		Returns:
			DataFrame: updated DataFrame
		"""		
		for k, f in func_dict.items():
			df[k] = f(df)
		#
		self.patterns = get_patterns(df, self.line_pattern_style_separation_on, self.line_pattern_style_shift_no)
		df = update_pattern(df, self.patterns, self.line_pattern_style_separation_on)
		#
		return df


	def update_cablings(self, **default_dic):
		"""creates Cabling object and its DataFrame, adds cabling details

		Returns:
			DataFrame: pandas DataFrame
		"""	
		self.C = ADevCablings(self.self_device, **default_dic)
		for k, v in self.u_ph_df.iterrows():
			kwargs = {}
			for x, y in v.items():
				kwargs[x] = y
			self.C.add_to_cablings(**kwargs)
		#
		self.C.cabling_dataframe()
		return self.C.merged_df

	def update_devices(self):
		"""creates Devices object, and its DataFrame, adds vlan informations.

		Returns:
			DataFrame: updated pandas DataFrame for interface connected devices
		"""		
		self.D = AdevDevices(self.stencils, self.var_func_dict, self.full_df['var'])
		self.D.int_df = self.update_devices_for(df=self.u_ph_df, dic=self.D.devices)
		self.D.add_vlan_info(self.vlan_df)
		return self.D.merged_df

	def update_device_self_detils(self, func_dict):
		"""create a pandas DataFrame object for the self object using `var` tab and custom functions

		Args:
			func_dict (dict): custom var functions

		Returns:
			DataFrame: pandas DataFrame for self device
		"""		
		self_device_df = self.D.get_self_device_df()
		self_dev_df = self.update_devices_for(df=self_device_df, dic=self.D.self_device)
		self_dev_df = self.update_devices_df_pattern_n_custom_func(self_dev_df, func_dict)
		return self_dev_df

	def update_devices_for(self, df, dic):
		"""update DataFrame for the provided dictionary (dic) objects, and removes empty and duplicate hostname value rows.

		Args:
			df (DataFrame): variable DataFrame
			dic (dict): variable dictionary

		Returns:
			DataFame: updated DataFrame
		"""		
		for k, v in df.iterrows():
			kwargs = {}
			for x, y in v.items():
				kwargs[x] = y
			self.D.add_to_devices(what=dic, **kwargs)

		u_df = device_df_drop_empty_duplicates(dic)
		return u_df



# --------------------------------------------- 
