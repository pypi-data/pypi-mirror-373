
import nettoolkit.nettoolkit_common as nt

# ----------------------------------------------------------------------------------------------------
# Some of static fixed / default values
# ----------------------------------------------------------------------------------------------------
DEFAULT_CONNECTOR_TYPE = 'straight'  ## other options = 'curved', 'angled'
DEFAULT_LINE_COLOR = 'blue'
DEFAULT_LINE_WT = 1
DEFAULT_LINE_PATTERN = 1
DEFAULT_STENCIL = None
DEFAULT_X_COLUMN = 'x-axis'
DEFAULT_Y_COLUMN = 'y-axis'
DEFAULT_DEVICES_TAB = 'Devices'
DEFAULT_CABLINGS_TAB = 'Cablings'
# ----------------------------------------------------------------------------------------------------


def get_physical_if_up(df):
	"""filter the DataFrame rows for active/enabled physical interfaces 

	Args:
		df (DataFrame): pandas DataFrame

	Returns:
		DataFrame: udpated DataFrame
	"""
	try:
		return df[ (df['link_status'] != 'administratively down')| (df['link_status'] != 'Enabled')].fillna("")
	except:
		return df

def get_physical_if_relevants(df, 
	relevant_cols = ['interface', 'nbr_dev_type', 'int_filter', 'nbr_hostname',   'nbr_interface', 'vlan_members', 'media_type']
	):
	"""filters the DataFrame columns for relevant columns

	Args:
		df (DataFrame): pandas DataFrame
		relevant_cols (list, optional): list of relevant columns. Defaults to ['interface', 'nbr_dev_type', 'int_filter', 'nbr_hostname',   'nbr_interface', 'vlan_members',].

	Returns:
		DataFrame: udpated DataFrame
	"""		
	try:
		return df[relevant_cols]
	except:
		return df

# --------------------------------------------- 

def get_vlan_if_up(df):
	"""filter the DataFrame rows for active/enabled vlan/irb interfaces 

	Args:
		df (DataFrame): pandas DataFrame

	Returns:
		DataFrame: udpated DataFrame
	"""
	try:
		return df[ (df['link_status'] != 'administratively down')| (df['link_status'] != 'Enabled')].fillna("")
	except:
		return df

def get_vlan_if_relevants(df, relevant_cols = ['int_number', 'interface', 'intvrf', 'subnet' ]):
	"""filters the DataFrame columns for relevant columns

	Args:
		df (DataFrame): pandas DataFrame
		relevant_cols (list, optional): list of relevant columns. Defaults to ['int_number', 'interface', 'intvrf', 'subnet' ].

	Returns:
		DataFrame: udpated DataFrame
	"""		
	try:
		return df[relevant_cols]
	except:
		return df

# --------------------------------------------- 


def get_patterns(df, line_pattern_style_separation_on, line_pattern_style_shift_no):
	"""get the line pattern numbers for the unique line styles require based on `line_pattern_style_separation_on`

	Args:
		df (DataFrame): pandas DataFrame
		line_pattern_style_separation_on (str): DataFrame Column name on which line patters to be separated
		line_pattern_style_shift_no (int): line pattern skip step number.

	Returns:
		dict: dictionary of unique line pattern identifies with its shift number.
	"""	
	if not line_pattern_style_separation_on: return None
	uniq_medias = df[line_pattern_style_separation_on].unique()
	media_pattern = {}
	for m in uniq_medias:
		for n in range(1, 10000, line_pattern_style_shift_no):
			if n in media_pattern.values(): continue
			media_pattern[m] = n
			break
	return media_pattern

def update_pattern(df, patterns, line_pattern_style_separation_on):
	"""update the line pattern column for the unique line styles require based on column `line_pattern_style_separation_on`

	Args:
		df (DataFrame): pandas DataFrame
		patterns (dict): dictionary of unique line pattern identifies with its shift number
		line_pattern_style_separation_on (str): DataFrame Column name on which line patters to be separated

	Returns:
		DataFrame: updated DataFrame
	"""
	if not line_pattern_style_separation_on: return df
	df['pattern'] = df[line_pattern_style_separation_on].apply(lambda x: patterns[x])
	return df

# --------------------------------------------- 

def series_item_0_value(s):
	"""returns the first item value of a series

	Args:
		s (series): pandas series object

	Returns:
		str: value from series
	"""
	for x in s:
		return x

def get_vlans_info(vlan_members, vlan_df):
	"""get the vlan-vrf-subnet information string for provided vlan number(s) from vlan DataFrame

	Args:
		vlan_members (str, int): a single vlan number or vlan numbers separated by comma
		vlan_df (DataFrame): DataFrame from `vlan` tab of -clean excel file

	Returns:
		str: concatenated string of vlan-vrf-subnet information.
	"""	
	if isinstance(vlan_members, float):
		vlan_members = [int(vlan_members)]
	else:
		vlan_members = nt.LST.remove_empty_members(vlan_members.split(","))
	s = ''
	# print(vlan_members)
	if len(vlan_members) == 0: return s
	for vlan in vlan_members:
		try:
			vlan = int(vlan)
			s += __get_a_vlan_info_string(vlan_df, vlan)
		except ValueError:
			try:
				vlans = vlan.split("-") 
				for v in range(int(vlans[0]), int(vlans[1])+1):
					s+= __get_a_vlan_info_string(vlan_df, v)
			except:
				pass
	return s


## return vlan information string for matching vlan number from given dataframe db
def __get_a_vlan_info_string(vlan_df, vlan):
	s = ""
	try:
		df = vlan_df[vlan_df['int_number'] == vlan]
		if df.empty:
			return s
		s += series_item_0_value(df['interface']) + " "
		s += series_item_0_value(df['intvrf']) + " "
		s += series_item_0_value(df['subnet']) + "\n"
	except:
		print(f'[-] Information:\tmissing information for vlan: {vlan}')
	return s


def update_vlans_info(int_df, vlan_df):
	"""add `vlan_info` [column] to interface DataFrame using help of vlan DataFrame

	Args:
		int_df (DataFrame): interface DataFrame
		vlan_df (DataFrame): DataFrame from `vlan` tab of -clean excel file

	Returns:
		DataFrame: updated interface DataFrame
	"""	
	int_df['vlan_info'] = int_df['vlan_members'].apply(lambda x: get_vlans_info(x, vlan_df))
	return int_df


# --------------------------------------------- 

def drop_empty(df, column):
	"""remove emptry rows found for given column

	Args:
		df (DataFrame): pandas DataFrame
		column (str): column name

	Returns:
		DataFrame: data filtered DataFrame
	"""
	return df[df[column] != ""]

# --------------------------------------------- 

def get_item_first(s):
	"""get first index item

	Args:
		s (series): pandas series

	Returns:
		str: first item from provided Pandas Series
	"""	
	for x in s:
		return x

def update_merged_df_series(merged_df_ser_hostname, merged_df_series_key, key, value, hostname):
	"""update merged dataframe series

	Args:
		merged_df_ser_hostname (series): hostname series
		merged_df_series_key (series): key series
		key (str): key value
		value (str): value
		hostname (str): hostname to match with

	Returns:
		str: matched result
	"""	
	if merged_df_ser_hostname == hostname:
		if merged_df_series_key:
			r = merged_df_series_key
		else:
			r = value
	else:
		r = merged_df_series_key
	return r

def get_dev_serial(var_df=None, update=False, merged_df_ser_hostname=None, merged_df_series_key=None, key=None, value=None, hostname=None):
	"""either get serial number from var tab or update full series with serial numbers

	Args:
		var_df (DataFrame, optional): var DataFrame. Defaults to None.
		update (bool, optional): updating full series or not. Defaults to False.
		merged_df_ser_hostname (series, optional): hostnames series. Defaults to None.
		merged_df_series_key (key, optional): series key name. Defaults to None.
		key (str, optional): series key. Defaults to None.
		value (value, optional): result value. Defaults to None.
		hostname (str, optional): hostname to match with. Defaults to None.

	Returns:
		str, series: return serial number based on update
	"""	
	if not update:
		return get_item_first(var_df[(var_df['var'] == 'serial')]['default'])
	else:
		return update_merged_df_series(merged_df_ser_hostname, merged_df_series_key, key, value, hostname)

def get_dev_model(var_df=None, update=False, merged_df_ser_hostname=None, merged_df_series_key=None, key=None, value=None, hostname=None):
	"""either get device model from var tab or update full series with device model

	Args:
		var_df (DataFrame, optional): var DataFrame. Defaults to None.
		update (bool, optional): updating full series or not. Defaults to False.
		merged_df_ser_hostname (series, optional): hostnames series. Defaults to None.
		merged_df_series_key (key, optional): series key name. Defaults to None.
		key (str, optional): series key. Defaults to None.
		value (value, optional): result value. Defaults to None.
		hostname (str, optional): hostname to match with. Defaults to None.

	Returns:
		str, series: return device model based on update
	"""	
	if not update:
		return get_item_first(var_df[(var_df['var'] == 'model')]['default'])
	else:
		return update_merged_df_series(merged_df_ser_hostname, merged_df_series_key, key, value, hostname)

def get_dev_hostname(var_df=None, update=False, merged_df_ser_hostname=None, merged_df_series_key=None, key=None, value=None, hostname=None):
	"""either get device hostname from var tab or update full series with device hostname

	Args:
		var_df (DataFrame, optional): var DataFrame. Defaults to None.
		update (bool, optional): updating full series or not. Defaults to False.
		merged_df_ser_hostname (series, optional): hostnames series. Defaults to None.
		merged_df_series_key (key, optional): series key name. Defaults to None.
		key (str, optional): series key. Defaults to None.
		value (value, optional): result value. Defaults to None.
		hostname (str, optional): hostname to match with. Defaults to None.

	Returns:
		str, series: return device hostname based on update
	"""	
	if not update:
		return get_item_first(var_df[(var_df['var'] == 'hostname')]['default'])
	else:
		return update_merged_df_series(merged_df_ser_hostname, merged_df_series_key, key, value, hostname)
