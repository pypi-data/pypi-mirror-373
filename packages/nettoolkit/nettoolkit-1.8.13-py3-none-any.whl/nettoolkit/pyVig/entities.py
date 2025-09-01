# -----------------------------------------------------------------------------------

from nettoolkit.nettoolkit_common import Multi_Execution

from nettoolkit.pyVig.visio import device

# -----------------------------------------------------------------------------------
#  Visio Objects / Items
# -----------------------------------------------------------------------------------
class ItemObjects(Multi_Execution):
	"""Execution of Devices/Item objects on visio

	Args:
		visObj (visObj): visio object
		devices_data (AdevDevices): Device object
		connectors (ADevCablings): Cabling object
		filterOnCables (bool, optional): multi tab filters. Defaults to True.
	"""		

	def __init__(self, 
		visObj, 
		devices_data,
		connectors,
		filterOnCables=True
		):
		"""object initializer
		"""		
		self.visObj = visObj
		self.devices_data = devices_data
		self.devices_details_list = (dev for i, dev in devices_data.df.iterrows())
		self.connectors = connectors
		self.filterOnCables=filterOnCables
		#
		self.devices = {}
		self.x_coordinates = []
		self.y_coordinates = []
		super().__init__(self.devices_details_list)
		self.start(multi_thread=False)

	def __getitem__(self, k): return self.devices[k]

	@property
	def top_most(self):
		"""top most used co-ordinate on visio

		Returns:
			int: maximum of used y-axis
		"""		 
		return max(self.y_coordinates)
	@property
	def bottom_most(self): 
		"""bottom most used co-ordinate on visio

		Returns:
			int: minimum of used y-axis
		"""		 
		return min(self.y_coordinates)
	@property
	def left_most(self): 
		"""left most used co-ordinate on visio

		Returns:
			int: minimum of used x-axis
		"""		 
		return min(self.x_coordinates)
	@property
	def right_most(self): 
		"""right most used co-ordinate on visio

		Returns:
			int: maximum of used x-axis
		"""		 
		return max(self.x_coordinates)
	@property
	def page_height(self): 
		"""total height occupied by drawing  on visio page

		Returns:
			int: page height
		"""		 		
		try:
			return self.top_most - self.bottom_most + 3
		except:
			return 4
	@property
	def page_width(self): 
		"""total width occupied by drawing  on visio page

		Returns:
			int: page width
		"""		 		
		try:
			return self.right_most - self.left_most + 3
		except:
			return 8
	
	def execute(self, dev):
		"""Executor
		Paralllel processing disabled currently due to visio not support

		Args:
			dev (dict): a single row details of device data

		Returns:
			None: None
		"""		
		#
		# filter to only drop connected devices.
		if (self.filterOnCables 
			and (not (
					(dev.hostname == self.connectors.df[self.connectors.dev_a]).any() 
				or 	(dev.hostname == self.connectors.df[self.connectors.dev_b]).any()) 
				) 
			):
			return None

		# ---- get column values from row of a device info --- #
		x=get_col_value(dev, self.devices_data.x, isMerged=False)
		y=get_col_value(dev, self.devices_data.y, isMerged=False)

		# # ---------- ADD FORMATTING AND OPTIONALS ----------------------- #
		format = {}

		# OPTIONAL
		optional_columns = self.devices_data.optional_columns
		for k, v in optional_columns.items():
			_cc = get_col_value(dev, k, isMerged=False)
			format[k] = _cc if _cc else v
			continue


		# FORMATTING
		format_columns = self.devices_data.format_columns
		for k, v in format_columns.items():
			_cc = get_col_value(dev, k, isMerged=False)
			format[k] = _cc if _cc else v
			continue


		# // adhoc, add corordinates for future calculation purpose.
		self.x_coordinates.append(x)
		self.y_coordinates.append(y)

		# if not format['stencil']: stencil = self.devices_data.default_stencil
		if not format['stencil']:
			print(f"[-] Warning:\t\tno stencil or no default-stencil found for {dev.hostname} ")

		# -- start drops ---
		self.devices[dev.hostname] = device(						# drop device
			visObj=self.visObj, 
			x=x,
			y=y,
			**format
			)
		# -- add description ---
		self.devices[dev.hostname].description(dev.description)	# description of device


# -----------------------------------------------------------------------------------
#  Visio Connectors
# -----------------------------------------------------------------------------------
class Connectors(Multi_Execution):
	"""Execution of Cabling/Connector objects on visio

	Args:
		cable_matrix_data (ADevCablings): cablnig object
		devices (AdevDevices): devices object
	"""		


	def __init__(self, cable_matrix_data, devices):
		"""object initializer
		"""		
		self.connectors = cable_matrix_data
		self.connectors_list = (connector for i, connector in cable_matrix_data.df.iterrows())
		self.devices = devices
		super().__init__(self.connectors_list)
		self.start(multi_thread=False)

	def execute(self, connector):
		"""Executor
		Paralllel processing disabled currently due to visio not support

		Args:
			connector (dict): a single row details of cabling data

		Returns:
			None: None
		"""		
		if connector[self.connectors.dev_a] and connector[self.connectors.dev_b]:
			# angle = connector.angle_straight_connector if conn_type_x == "straight" else connector.angle_angled_connector
			kwargs = self.get_optional_columns_value(connector)

			# # connect the two devices	
			self.devices[connector[self.connectors.dev_a]].connect(
				self.devices[connector[self.connectors.dev_b]],
					# connector_type=conn_type_x, 
					**kwargs
			)

	def get_optional_columns_value(self, connector):
		"""get the value of all optional columns for given row

		Args:
			connector (dict): a single row information from a DataFrame

		Returns:
			dict: dictionary with found values else default
		"""		
		dic = {}
		for k, v in self.connectors.__dict__.items():
			if k in self.connectors.optional_columns:
				uv = get_col_value(connector, k+"_x", isMerged=False)
				dic[k] = uv if uv else v
		return dic
				


def get_col_value(row_info, column, isMerged=True):
	"""get the value of provided column from given row details

	Args:
		row_info (dict): a single row information from a DataFrame
		column (str): column name 
		isMerged (bool, optional): is it a merged column or native. Defaults to True.

	Returns:
		str: Cell information from row
	"""	
	try:
		return row_info[column]
	except:
		# if isMerged:
		# 	print(f"column information incorrect, check column existance `{column[:-2]}`")
		# else:
		# 	print(f"column information incorrect, check column existance `{column}`")
		return ""


# -----------------------------------------------------------------------------------
