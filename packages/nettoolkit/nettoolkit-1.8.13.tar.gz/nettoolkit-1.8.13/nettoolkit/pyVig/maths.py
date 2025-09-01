import numpy as np
import pandas as pd

# -------------------------------------------------------------------------------------

def df_with_slops_and_angles(df, x1_col, x2_col, y1_col, y2_col):
	"""add the dataframe with slop and angle for the given co-ordinates on plane.

	Args:
		df (DataFrame): Input DataFrame
		x1_col (str): column name for point 1 - x axis
		x2_col (str): column name for point 2 - x axis
		y1_col (str): column name for point 1 - y axis
		y2_col (str): column name for point 2 - y axis

	Returns:
		DataFrame: Updated Output DataFrame
	"""	
	df['slop'] = (df[y2_col] - df[y1_col])/(df[x2_col] - df[x1_col])
	df = df.fillna("")
	df['angle_angled_connector'] = df.slop.apply(slop_to_angled_connector)
	df['angle_straight_connector'] = df.slop.apply(slop_to_straight_connector)
	return df.fillna("")


def slop_to_straight_connector(m):
	"""calculate angle from given slop(m) of a straight line.

	Args:
		m (float): slop of a straight line

	Returns:
		int: degree/slop of line
	"""		
	if not m: return 0
	angle = int(np.math.degrees(np.math.tanh(m)))
	if angle < 0: angle = 90+angle
	if m <= 0: angle = 360-angle 
	return angle

def slop_to_angled_connector(m):
	"""calculate angle from given slop(m) of an angled line.

	Args:
		m (float): slop of an angled line

	Returns:
		int: degree/slop of line
	"""		
	if not m: return 0
	angle = int(np.math.degrees(np.math.tanh(m)))
	if angle < 0: angle = 180-angle
	if m > 0: angle = 360-angle 
	return angle




# --------------------------------------------- 
# Co-ordinate calculator
# --------------------------------------------- 
class CalculateXY():
	"""Co-ordinate calculator

	Args:
		dev_df (DataFrame): Device DataFrame
		default_x_spacing (int, float): horizontal spacing between two devices
		default_y_spacing (int, float): vertical spacing between two devices
		cbl_df (DataFrame): Cabling DataFrame
		sheet_filter_dict (dict): sheet filters for multi tab drawing
	"""	
	def __init__(self, dev_df, default_x_spacing, default_y_spacing, cbl_df, sheet_filter_dict):
		"""initialize object by providing device DataFrame, default x & y - axis spacing values.
		"""		
		self.df = dev_df
		self.cbl_df = cbl_df
		#
		self.spacing_x = default_x_spacing
		self.spacing_y = default_y_spacing
		#
		self.sheet_filter_dict = sheet_filter_dict


	def calc(self):
		"""calculation sequences
		"""		
		self.sort()
		ho_dict = self.count_of_ho(self.df)
		#
		self.update_ys(self.df, 'y-axis', ho_dict)
		self.update_xs(self.df, 'x-axis', ho_dict)
		#
		if self.sheet_filter_dict:
			self.update_xy_for_sheet_filter_dict()
			self.merge_xy_filter_dfs_with_dev_df()


	def update_xy_for_sheet_filter_dict(self):
		"""create and calculate x-axis, y-axis columns, values for each filtered tab database
		"""		
		self.sheet_filter_cbl_df_dict = {}
		self.sheet_filter_dev_df_dict = {}
		self.sheet_filter_dev_dict = {}
		for k, v in self.sheet_filter_dict.items():
			self.sheet_filter_cbl_df_dict[k] = self.cbl_df[self.cbl_df[k] == v] 
			self.sheet_filter_dev_dict[k] = set(self.sheet_filter_cbl_df_dict[k]['a_device']).union(set(self.sheet_filter_cbl_df_dict[k]['b_device']))
			self.sheet_filter_dev_df_dict[k] = self.df[self.df.hostname.apply(lambda x: x in self.sheet_filter_dev_dict[k])]
			ho_dict = self.count_of_ho(self.sheet_filter_dev_df_dict[k])
			self.update_ys(self.sheet_filter_dev_df_dict[k], f'{k}-y-axis', ho_dict)
			self.update_xs(self.sheet_filter_dev_df_dict[k], f'{k}-x-axis', ho_dict)
			self.sheet_filter_dev_df_dict[k] = self.sheet_filter_dev_df_dict[k][['hostname', f'{k}-x-axis', f'{k}-y-axis']]

	def merge_xy_filter_dfs_with_dev_df(self):
		"""merge sheet filter x,y column information with main device dataframe
		"""		
		for k, v in self.sheet_filter_dev_df_dict.items():
			self.df = self.df.join(v.set_index('hostname'), on='hostname')


	def sort(self):
		"""sort the Device DataFrame based on ['hierarchical_order', 'hostname']
		"""		
		self.df.sort_values(by=['hierarchical_order', 'hostname'], inplace=True)
		self.df = self.df[self.df.hierarchical_order != 100]

	def count_of_ho(self, df):
		"""counts hierarchical_order items for given dataframe and stores it in local dict 

		Args:
			df (DataFrame): Device Dataframe with `hierarchical_order` column

		Returns:
			_type_: _description_
		"""		
		vc = df['hierarchical_order'].value_counts()
		return {ho: c for ho, c in vc.items()}

	def calc_ys(self, ho_dict):
		"""calculate y-axis refereances with respect to high order dictionary

		Args:
			ho_dict (dict): high order devices dictionary

		Returns:
			dict: high order dictionary with y-axis reference values
		"""		
		ih, y = 0, {}
		for i, ho in enumerate(sorted(ho_dict)):
			if i == 0: 
				y[ho] = ih
				prev_ho = ho
				continue
			c = ho_dict[ho] + ho_dict[prev_ho]
			ih += c/2 * self.spacing_y
			y[ho] = ih
		y = self.inverse_y(y)
		return y

	def inverse_y(self, y):
		"""inverses the y axis values (turn upside down)

		Args:
			y (dict): dictionary with y axis placement values based on hierarchical_order

		Returns:
			dict: inversed dictionary with y axis placement values based on reversed hierarchical_order
		"""
		return {k: max(y.values()) - v+2 for k, v in y.items()}

	def get_y(self, ho): 
		"""get the y axis value for the given hierarchical_order

		Args:
			ho (int): hierarchical order number

		Returns:
			int, float: y axis value
		"""		
		return self.y[ho]

	def update_ys(self, df, y_axis, ho_dict):
		"""update  `y-axis` column to given `df` Device DataFrame

		Args:
			df (DataFrame): Device DataFrame
			y_axis (str): column name for y_axis
			ho_dict (dict): high order devices dictionary
		"""			
		self.y = self.calc_ys(ho_dict)
		df[y_axis] = df['hierarchical_order'].apply(self.get_y)

	# -----------------------------------------------

	def get_x(self, ho): 
		"""get the x axis value for a device from given hierarchical order number

		Args:
			ho (int): hierarchical order number

		Returns:
			int, float: x axis value
		"""		
		for v in sorted(self.xs[ho]):
			value = self.xs[ho][v]
			break
		del(self.xs[ho][v])
		return value

	def calc_xs(self, ho_dict):
		"""calculate x-axis refereances with respect to high order dictionary

		Args:
			ho_dict (dict): high order devices dictionary

		Returns:
			dict: high order dictionary with x-axis reference values
		"""		
		xs = {}
		middle = self.full_width/2
		halfspacing = self.spacing_x/2
		for ho in sorted(ho_dict):
			if not xs.get(ho):
				xs[ho] = {}
			c = ho_dict[ho]
			b = middle - (c/2*self.spacing_x) - halfspacing
			for i, x in enumerate(range(c)):
				pos = x*self.spacing_x + b 
				xs[ho][i] = pos
		return xs

	def update_xs(self, df, x_axis, ho_dict):
		"""update  `x-axis` column to given `df` Device DataFrame

		Args:
			df (DataFrame): Device DataFrame
			x_axis (str): column name for x_axis
			ho_dict (dict): high order devices dictionary
		""" 	
		self.full_width = (max(ho_dict.values())+2) * self.spacing_x
		self.xs = self.calc_xs(ho_dict)
		df[x_axis] = df['hierarchical_order'].apply(self.get_x)


# --------------------------------------------- 

class CalculateXYNative():
	"""Calculate co-ordinate default Native way

	Args:
		ddf (DataFrame): Devices DataFrame
		cdf (DataFrame): Cabling DataFrame

	"""    	

	def __init__(self, ddf, cdf, sfd):
		"""Initializer
		"""    		
		self.ddf = ddf
		self.df = self.ddf
		self.cdf = cdf
		self.sfd = sfd
		self.item_indexes = {}
		self.indexes = [] 
		self._x = 0
		self._y = 0

	def count_of_devices(self, dev):
		"""identify devices from cable matrix and provide its occurances number.

		Args:
			dev (str): Device hostname to match with 

		Returns:
			int: number of occurances
		"""    		
		return len(self.cdf[(self.cdf.a_device == dev)]) + len(self.cdf[(self.cdf.b_device == dev)])

	def dev_connectors_dict(self):
		"""set device connectors dictionary and its inverse dictionary
		"""    		
		self.dcd = {device:self.count_of_devices(device) for device in set(self.ddf.hostname)}
		self.ddc = {}
		for k, v in self.dcd.items():
			if not self.ddc.get(v):
				self.ddc[v] = set()
			self.ddc[v].add(k)

	def calc(self):
		"""start calculator
		"""    		
		self.dev_connectors_dict()
		self.iterate()
		self.add_x_y_to_df()

	def add(self, item, x, y):
		"""add an item to provided co-ordinates

		Args:
			item (str): device hostname
			x (int): x-coordinate
			y (int): y-coordinate
		"""    		
		if item not in self.item_indexes:
			self.item_indexes[item] = (x,y)
			self.indexes.append((x,y))

	def iterate(self):
		"""iterate thru all devices and add its co-ordinates
		"""    		
		for n in sorted(self.ddc.keys()):
			devices = self.ddc[n]
			for device in devices:
				self.device_add(device, root=True)

	def device_add(self, device, root):
		"""check if device and its childs is added or not and add its co-ordinates.

		Args:
			device (str): hostname of device
			root (bool): is it root path or not

		Returns:
			None: No return
		"""    		
		if device not in self.item_indexes and (self._x, self._y) not in self.indexes:
			self.add(device, self._x, self._y)
			return None
		if root:
			nbr_devices = self.get_nbr_devices(device)
			for dev in nbr_devices:
				self._x += 2
				self.device_add(dev, root=False)
			self._y += 2


	def get_nbr_devices(self, device):
		"""get set of neighbor devices for provided host/device

		Args:
			device (str): device hostname

		Returns:
			set: set of devices
		"""    		
		return set(self.cdf[(self.cdf.a_device == device)].b_device).union(set(self.cdf[(self.cdf.b_device == device)].a_device))

	def add_x_y_to_df(self):
		"""add x,y axis columns to devices data frame.
		"""
		self.ddf['x-axis'] = self.ddf.hostname.apply(lambda x: self.get_xy(x, 0))
		self.ddf['y-axis'] = self.ddf.hostname.apply(lambda x: self.get_xy(x, 1))
		for k in self.sfd:
			self.ddf[f'{k}-x-axis'] = self.ddf.hostname.apply(lambda x: self.get_xy(x, 0))
			self.ddf[f'{k}-y-axis'] = self.ddf.hostname.apply(lambda x: self.get_xy(x, 1))

	def get_xy(self, dev, i):
		"""retrive (x,y) co-ordinate for provided device. (i=0 for x, i=1 for y)

		Args:
			dev (str): device hostname
			i (int): index number from tuple for x, y

		Returns:
			int: respective co-ordinate
		"""    		
		try:
			return self.item_indexes[dev][i]
		except: pass
		try:
			return self.item_indexes[dev.strip()][i]
		except: pass
		return -10
