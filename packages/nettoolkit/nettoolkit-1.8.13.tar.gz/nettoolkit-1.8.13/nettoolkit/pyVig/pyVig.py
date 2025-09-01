
from copy import deepcopy
from .stencils import get_list_of_stencils
from .database import DeviceData, CableMatrixData
from .entities import ItemObjects, Connectors
from .visio import VisioObject

# ------------------------------------------------------------------------- 
# ## pyvig boiler plate code.
# ------------------------------------------------------------------------- 
def cabling_data_operations(**dic):
	"""create and return cabling data object

	Args:
		dic (kwargs): keyword arguments

	Returns:
		CableMatrixData: Cablings data object
	"""	
	cable_matrix_data = CableMatrixData(**dic)
	return cable_matrix_data


def device_data_operations(**dic):
	"""creates and returns devices data object after merging columns of the list provided for `cols_to_merge` key  

	Args:
		dic (kwargs): keyword arguments.

	Returns:
		DeviceData: Devices data object
	"""	
	devices_data = DeviceData(**dic)
	if 'cols_to_merge' in dic:
		devices_data.add_description(dic['cols_to_merge'])
	else:
		devices_data.add_description([])
	return devices_data

def visio_operations(devices_data, cable_matrix_data, stencils, **dic):
	"""create a VisioObject

	Args:
		devices_data (DeviceData): Devices data object
		cable_matrix_data (CableMatrixData): Cablings data object
		stencils (list): list of visio stencils 
		dic (kwargs): keyword arguments

	Returns:
		None: None
	"""	
	outputFile = dic['op_file'] if 'op_file' in dic else None
	with VisioObject(stencils, outputFile) as v:
		print(f"[+] Information:\tVisio Drawing Inprogress, Do not close Visio Drawing while its running...")
		if (	(  'sheet_filters' in dic and dic['sheet_filters'])
			# and not ('is_sheet_filter' in dic and dic['is_sheet_filter'] != True) 			
			) :
			for kv in dic['sheet_filters'].items():
				if isinstance(kv[1], str):
					devices_data.x = f'{kv[0]}-x-axis'					
					devices_data.y = f'{kv[0]}-y-axis'
					repeat_for_filter(v, devices_data, cable_matrix_data, kv[0], kv[1], kv[0], **dic)
				elif isinstance(kv[1], (list, tuple, set)):
					for _kv in kv[1]:
						devices_data.x = f'{kv[0]}-x-axis'					
						devices_data.y = f'{kv[0]}-y-axis'
						repeat_for_filter(v, devices_data, cable_matrix_data, kv[0], _kv, kv[0] + '_' + _kv, **dic)
		else:
			visio_page_operation(v, devices_data, cable_matrix_data, {}, **dic)
	return None


def repeat_for_filter(v, devices_data, cable_matrix_data,
	filt_key, filt_value, page_key=None, 
	**dic ):
	"""starts visio page operation for the given filter

	Args:
		v (VisioObject): Visio Object
		devices_data (DeviceData): Devices data object
		cable_matrix_data (CableMatrixData): Cablings data object
		filt_key (str): filter key
		filt_value (str, tuple, list, set): filter value(s)
		page_key (str): page key (suffix for filter values in case if multiple filt_values)
		dic (kwargs): keyword arguments
	"""	
	flt ={filt_key:filt_value}
	cmd = deepcopy(cable_matrix_data)
	visio_page_operation(v, devices_data, cmd, flt, page_key=page_key, **dic)


def visio_page_operation(v, devices_data, cable_matrix_data, flt, page_key=None, **dic):
	"""operate on visio page

	Args:
		v (VisioObject): Visio Object
		devices_data (DeviceData): Devices data object
		cable_matrix_data (CableMatrixData): Cablings data object
		flt (dict): filters {key: value} pairs
		page_key (str, optional): page key (suffix for filter values in case if multiple filt_values). Defaults to None.
		dic (kwargs): keyword arguments
	"""	
	if 'filter_on_include_col' in dic:
		cable_matrix_data.filter_eligible_cables_only() # [Optional]
	if 'is_sheet_filter' in dic and dic['is_sheet_filter'] == True:   ## condition unnecessary, remove condition in future since taken care by parent function
		cable_matrix_data.filter(**flt)               # [Optional] column=records
	cable_matrix_data.calc_slop(devices_data)         # [Mandatory] calculate cable slop/angle
	if flt:
		v.insert_new_page(page_key)
	else:
		v.insert_new_page("PhysicalDrawing")
	filterOnCables = dic['filter_on_cable'] if 'filter_on_cable' in dic else True
	#
	item_objects = ItemObjects(v, devices_data, cable_matrix_data, filterOnCables=filterOnCables)
	Connectors(cable_matrix_data, item_objects)
	v.fit_to_draw(item_objects.page_height, item_objects.page_width)

def pyVig(**dic):
	"""main function starting the python based cli - visio generation

	Args:
		dic (kwargs): inputs dictionary ( valid and mandatory keys = stencil_folder, data_file ) (valid but optional keys = default_stencil, cols_to_merge, is_sheet_filter, sheet_filters ... and many more from DEFAULT_DIC )

	Returns:
		None: None
	"""	
	if 'stencil_folder' not in dic:
		raise Exception(f'[-] Mandatory input "stencil_folder" missing kindly provide.')
	if 'data_file' not in dic:
		raise Exception(f'[-] Mandatory input "data_file" missing kindly provide.')
	#
	devices_data = device_data_operations(**dic)
	cable_matrix_data = cabling_data_operations(**dic)
	#
	stencils = get_list_of_stencils(
		folder=dic['stencil_folder'],
		devices_data=devices_data,
	)
	#
	visio_operations(devices_data, cable_matrix_data, stencils, **dic)
	return None



# ------------------------------------------------------------------------- 


