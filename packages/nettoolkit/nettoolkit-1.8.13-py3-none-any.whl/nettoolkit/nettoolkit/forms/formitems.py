
# ---------------------------------------------------------------------------------------
sg = None
try:
	import PySimpleGUI as sg
except:
	pass
from abc import abstractclassmethod
import pandas as pd
from pathlib import *
import nettoolkit.nettoolkit.forms as frm
import time


# ---------------------------------------------------------------------------------------
formpath_str = str(frm).split('from')[-1].split(">")[0].strip()[1:-1]
p = Path(formpath_str)
previous_path = p.resolve().parents[0]
CACHE_FILE = previous_path.joinpath('caches.xlsx')
CONNECTOR_TYPES_FILE = previous_path.joinpath('cable_n_connectors.xlsx')


# ------------------------------------------------------------------------
#   DOUBLE CLICK ACtion
# ------------------------------------------------------------------------
class DoubleClick():
	"""Class which defines basic methods to detect the mouse double click 
	threshold is set to 0.5 ms
	
	should always have a do_action() method to determine what to when
	mouse double click is detected.

	Args:
		obj (NGui): NGui object.
		i (dict): NGui Window object fields.
	"""

	last_click_time = 0

	def __init__(self, obj, i):
		self.open_gtacmfa_devopt(obj, i)

	def is_double_clicked(self, threshold=0.5):
		current_time = time.time()
		if current_time - DoubleClick.last_click_time <= threshold:
			return True
		return False

	def open_gtacmfa_devopt(self, obj, i):
		if self.is_double_clicked():
			self.do_action()
		DoubleClick.last_click_time = time.time()	

	@abstractclassmethod
	def do_action(self, **kwargs):
		pass

# ------------------------------------------------------------------------
#   Triple CLICK ACtion
# ------------------------------------------------------------------------
class TripleClick():
	"""Class which defines basic methods to detect the mouse triple click 
	threshold is set to 0.5 ms
	
	should always have a do_action() method to determine what to when
	mouse double click is detected.

	Args:
		obj (NGui): NGui object.
		i (dict): NGui Window object fields.
	"""

	first_click_time = 0
	second_click_time = 1

	def __init__(self, obj, i, threshold=0.5):
		self.i = i
		self.obj = obj
		self.threshold = threshold
		self.open_gtacmfa_devopt(obj, i)

	def is_triple_clicked(self, threshold=0.5):
		current_time = time.time()
		if current_time - TripleClick.second_click_time <= threshold:
			return True
		return False

	def open_gtacmfa_devopt(self, obj, i):
		current_time = time.time()
		if self.is_triple_clicked():
			print('[*] Triple click achieved, Saving Passphrase to user preferences file')
			self.do_action(obj=obj, i=i)
		if current_time - TripleClick.first_click_time <= self.threshold:
			TripleClick.first_click_time = current_time	
		elif current_time - TripleClick.first_click_time <= self.threshold*2:
			TripleClick.second_click_time = current_time

		if (
			current_time - TripleClick.first_click_time <= self.threshold and
			current_time - TripleClick.second_click_time <= self.threshold*2
			):
			TripleClick.second_click_time = current_time

		elif (TripleClick.second_click_time == 1 and TripleClick.first_click_time == 0  )or current_time - TripleClick.first_click_time <= self.threshold:
			TripleClick.second_click_time = current_time

		elif TripleClick.first_click_time ==0 or current_time - TripleClick.first_click_time <= self.threshold:
			TripleClick.first_click_time = current_time	

		else:
			TripleClick.first_click_time = 0
			TripleClick.second_click_time = 1



	@abstractclassmethod
	def do_action(self, *args, **kwargs):
		pass

# ------------------------------------------------------------------------
def popupmsg(pre=None, *, post=None,):
	"""Decorator to provide pre/post custom popup message to a function

	Args:
		pre (str, optional): Popup Message to display before function execution. Defaults to None.
		post (str, optional): Popup Message to display after function execution. Defaults to None.
	"""    	
	def outer(func):
		def inner(*args, **kwargs):
			if pre: 
				sg.Popup(pre)
			#
			fo = func(*args, **kwargs)
			#
			if post: 
				sg.Popup(post)
			return fo
		return inner
	return outer


activity_finish_popup = popupmsg(post="Activity Completed")

# ---------------------------------------------------------------------------------------

def blank_line(): 
	"""to insert a blank row

	Returns:
		list: blank row
	"""		
	return [sg.Text(''),]

def item_line(item, length):
	"""to draw a line with provided character or repeat a character for n-number of time

	Args:
		item (str): character
		length (int): to repeat the character

	Returns:
		list: list with repeated item Text
	"""    	
	return [sg.Text(item*length)]

def under_line(length, background_color=None): 
	"""To draw a line

	Args:
		length (int): character length of line

	Returns:
		list: underline row
	"""		
	if background_color is None:
		return [sg.Text('_'*length)]
	else:
		return [sg.Text('_'*length, background_color=background_color)]


def banner(version, background_color):
	"""Banner / Texts with bold center aligned fonts

	Args:
		version (str): version of code

	Returns:
		list: list with banner text
	"""    		
	return [sg.Text(version, font=('Calibri', 20, 'bold'), text_color='lightgray', justification='center', 
		size=(768,1), background_color=background_color,

	)] 


def footer(version, width):
	"""Footer Credit text

	Args:
		version (str): gui template version
		width (_type_): width of window

	Returns:
		list: list with footer text
	"""    	
	return [sg.Text(f"Prepared using Nettoolkit NGUI {version}", justification='right', size=(width, 1))]

def tabs(background_color, **kwargs):
	"""create tab groups for provided kwargs

	Returns:
		sg.TabGroup: Tab groups
	"""    		
	_tabs = []
	for k, v in kwargs.items():
		_tabs.append( sg.Tab(k, [[v]], background_color=background_color,   ) )
	return sg.TabGroup( [_tabs], 
		background_color=background_color,
		tab_background_color=background_color,
		selected_background_color=background_color,
	)


def button_ok(text, **kwargs):  
	"""Insert an OK button of regular size. provide additional formating as kwargs.

	Args:
		text (str): Text instead of OK to display (if need)

	Returns:
		sg.OK: OK button
	"""		
	return sg.OK(text, size=(10,1), **kwargs)	

def button_cancel(text, **kwargs):
	"""Insert a Cancel button of regular size. provide additional formating as kwargs.

	Args:
		text (str): Text instead of Cancel to display (if need)

	Returns:
		sg.Cancel: Cancel button
	"""    	  
	return sg.Cancel(text, size=(10,1), **kwargs)

def button_pallete():
	"""button pallete containing standard OK  and Cancel buttons 

	Returns:
		list: list with sg.Frame containing buttons
	"""    		
	return [sg.Frame(title='Button Pallete', 
			title_color='blue', 
			relief=sg.RELIEF_RIDGE, 
			layout=[
		[button_ok("Go", bind_return_key=True), button_cancel("Cancel"),],
	] ), ]

def get_list(raw_items):
	"""create list from given raw items splits by enter and comma

	Args:
		raw_items (str): multiline raw items

	Returns:
		list: list of items
	"""	
	ri_lst = raw_items.split("\n")
	lst = []
	for i, item in enumerate(ri_lst):
		if item.strip().endswith(","):
			ri_lst[i] = item[:-1]
	for ri_item in ri_lst:
		lst.extend(ri_item.split(","))
	for i, item in enumerate(lst):
		lst[i] = item.strip()		
	return lst

def tabs_display(background_color, **tabs_dic):
	"""define tabs display

	Returns:
		list: list of tabs
	"""    		
	return [tabs(background_color, **tabs_dic),]

# ---------------------------------------------------------------------------------------

def update_cache(cache_file, **kwargs):
	"""add/update cache item/value

	Args:
		cache_file (str): cache file name with full path
	"""		
	#
	df = pd.read_excel(cache_file).fillna("")
	dic = df.to_dict()
	#
	for input_key, input_value in kwargs.items():
		prev_value = ""
		prev_value_idx = None
		if input_key in dic['VARIABLE'].values():
			for (vrk, vr), (vlk, vl) in zip(dic['VARIABLE'].items(), dic['VALUE'].items()):
				if vr == input_key:
					prev_value_idx = vlk
					prev_value = vl
		v = input_value or prev_value
		if not prev_value or v != prev_value:
			if prev_value_idx is None:
				try:
					prev_value_idx = max(dic['VARIABLE'].keys())+1
				except:
					prev_value_idx = 0
			dic['VARIABLE'][prev_value_idx] = input_key
			dic['VALUE'][prev_value_idx] = v
	ndf = pd.DataFrame(dic, columns=['VARIABLE', 'VALUE'])
	ndf.to_excel(cache_file, index=False)


def get_cache(cache_file, key):
	"""retrive the value for provided key(item) from cache file

	Args:
		cache_file (str): cache file name with full path
		key (str): name of item

	Returns:
		str: matched item value from cache file
	"""	
	#
	try:
		df = pd.read_excel(cache_file).fillna("")
	except FileNotFoundError:
		try:
			df = pd.DataFrame({'VARIABLE': [], 'VALUE':[]})
			df.to_excel(cache_file, index=False)
		except:
			return ""
	dic = df.to_dict()
	#
	for vrk, vr in dic['VARIABLE'].items():
		if key == vr:
			return dic['VALUE'][vrk]
	#
	return ""
# ---------------------------------------------------------------------------------------


def get_cable_n_connectors(file, column, item):
	"""retrive the value for provided item for given column

	Args:
		file (str): cached cable and connector file name with full path
		column (str): column name (attribute)
		item (str): row item (connector type)

	Returns:
		str: matched item value from cached file
	"""	
	try:
		df = pd.read_excel(file).fillna("")
	except FileNotFoundError:
		df = pd.DataFrame({'media_type': [], 'cable_type':[], '_connector_type':[], 'speed':[] })
		df.to_excel(file, index=False)
	dic = df.to_dict()
	#
	for vrk, vr in dic['media_type'].items():
		if item.lower() == vr.lower():
			return dic[column][vrk]
	#
	return ""

def add_cable_n_connectors(file, **kwargs):
	"""add item/value

	Args:
		file (str): cached cable and connector excel file name with full path
	"""		
	#
	df = pd.read_excel(file).fillna("")
	df2 = pd.DataFrame(kwargs)
	df = pd.concat([df, df2], ignore_index=True).fillna("")
	df.to_excel(file, index=False)

# ---------------------------------------------------------------------------------------


def enable_disable(obj, * , group, group_frames, all_tabs, event_updaters):
	"""enable/disable provided object frames

	Args:
		obj (NGui): NGui class instance object
		group (str): button group key, which is to enabled.
		group_frames (list): list of frames to be enabled
		all_tabs (set): set of all frames keys
		event_updaters (set): set of Button pallet names button keys
	"""	
	tabs_to_disable = all_tabs.difference(group_frames)
	buttons_to_rev = event_updaters.difference(group)
	for tab in tabs_to_disable:
		d = {tab: {'visible':False}}
		obj.event_update_element(**d)	
	for i, tab in enumerate(group_frames):
		e = {tab: {'visible':True}}
		obj.event_update_element(**e)
		if i ==0: obj.w[tab].select()
	if group:
		for tab in buttons_to_rev:
			e = {tab: {'button_color': 'gray'}}
			obj.event_update_element(**e)
		e = {group: {'button_color': 'blue'}}
		obj.event_update_element(**e)


