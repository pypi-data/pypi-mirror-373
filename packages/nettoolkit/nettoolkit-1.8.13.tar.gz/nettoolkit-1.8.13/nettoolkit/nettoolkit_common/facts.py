

# ------------------------------------------------------------------------------------
# COMMON FUNCTIONS USED IN FACTS EDITING
# ------------------------------------------------------------------------------------

def add_blankdict_key(dic, key):
	"""add balnk dictionary to provided dictionary with key as provided key

	Args:
		dic (dict): dictionary to edit with blank key:{}
		key (non-mutable): key name or non-mutable object

	Returns:
		dict: updated dictionary
	"""    	
	if not dic.get(key):
		dic[key] = {}
	return dic[key]

def add_blankset_key(dic, key):
	"""add balnk set to provided dictionary with key as provided key

	Args:
		dic (dict): dictionary to edit with blank key: set()
		key (non-mutable): key name or non-mutable object

	Returns:
		dict: updated dictionary
	"""    	
	if not dic.get(key):
		dic[key] = set()
	return dic[key]

def add_blanklist_key(dic, key):
	"""add balnk list to provided dictionary with key as provided key

	Args:
		dic (dict): dictionary to edit with blank key:[]
		key (non-mutable): key name or non-mutable object

	Returns:
		dict: updated dictionary
	"""    	
	if not dic.get(key):
		dic[key] = []
	return dic[key]

def add_blanktuple_key(dic, key):
	"""add balnk tuple to provided dictionary with key as provided key

	Args:
		dic (dict): dictionary to edit with blank key:()
		key (non-mutable): key name or non-mutable object

	Returns:
		dict: updated dictionary
	"""    	
	if not dic.get(key):
		dic[key] = ()
	return dic[key]

def add_blanknone_key(dic, key):
	"""add balnk / None to provided dictionary with key as provided key

	Args:
		dic (dict): dictionary to edit with blank key: None
		key (non-mutable): key name or non-mutable object

	Returns:
		dict: updated dictionary
	"""    	
	if not dic.get(key):
		dic[key] = None
	return dic[key]

def update_key_value(dic, key, value):
	"""update a key value with provided value in given dictionary, if the key doesn't exist in dictionary.
	If it does exist, it will be skipped.

	Args:
		dic (dict): dictionary to edit
		key (non-mutable): key name to update to 
		value (any): value to be updated with.

	Returns:
		dict: updated dictionary with provided key:value
	"""    	
	if not dic.get(key):
		dic[key] = value

def next_index_item(lst, item):
	"""get the next index item from provided lst-list, for the item provided as item

	Args:
		lst (list): list of items
		item (any): item to match

	Returns:
		any: next index item for the provided item to search within
	"""
	if item not in lst: return None
	idx = lst.index(item)
	if len(lst) > idx:
		return lst[idx+1]
	return None

def append_attribute(dic, attribute, value, remove_duplicate=False):
	"""Appends an attribute to dictionary. (dynamic changes). 
	if dic doesnot have attribute: it will add
	if dic has attribute, and of list type: it will be appended
	if dic has attribute, and of str type: it will convert it to list, and append

	Args:
		dic (dict): dictionary to be update
		attribute (non-mutable): non-mutable key object
		value (any): value to be update/append
		remove_duplicate (bool, optional): doesnot append attribute if same entry already exist if set to True. Defaults to False.
	"""    	
	if not dic.get(attribute):
		dic[attribute] = value		
	elif dic[attribute] and isinstance(dic[attribute], str):
		if remove_duplicate and value == dic[attribute]: return
		dic[attribute] = [ dic[attribute], value ]
	elif dic[attribute] and isinstance(dic[attribute], list):
		if remove_duplicate and value in dic[attribute]: return
		dic[attribute].append( value )
	else:
		dic[attribute] = value

def get_instance_parameter_for_items(dic, line, spl, items, unique=False):
	"""updates dic (dictionary)  for items found in spl(splitted line) with its next index values

	Args:
		dic (dict): dictionary to be udpated with (inline update)
		line (str): line string (NIU) 
		spl (list): splitted line string
		items (list, set, tuple): items to be match in string
		unique (bool, optional): keeps unique values if set to True. Defaults to False.
	"""	
	for item in items:
		_get_instance_parameter(dic, line, spl, item, unique)

# updates dic (dictionary)  for a single item found in spl(splitted line) with its next index values
def _get_instance_parameter(dic, line, spl, item, unique=False):
	if item not in spl: return
	append_attribute(dic, attribute=item, value=spl[spl.index(item)+1], remove_duplicate=unique)

def update_true_instance_items(dic, line, spl, items):
	"""updates dic (dictionary)  for items found in spl(splitted line) with True

	Args:
		dic (dict): dictionary to be udpated with (inline update)
		line (str): line string (NIU) 
		spl (list): splitted line string
		items (list, set, tuple): items to be match in string
	"""    	
	for item in items:
		_update_true_instance(dic, line, spl, item)

# updates dic (dictionary)  for an item found in spl(splitted line) with True
def _update_true_instance(dic, line, spl, item):
	if item not in spl: return
	dic[item]=True

def get_nest_attributes(input_dict, line, spl, nest_attrs, next_attr=True, unique=False):
	"""updated nested attributes for provided input dictionary. action will be dynamic.
	if next_attr set to True: added/appended attribute will be next item from provided list of keys of nest_attrs
	if next_attr set to False: added/appended attribute will be True from provided list of keys of nest_attrs
	if unique set to True: added/appended attribute will be unique in nature, i.e. no duplicates added.
	Iterative.

	Args:
		input_dict (dict): input dictionary to be updated (inline)
		line (str): line string (NIU)
		spl (list): splitted line string
		nest_attrs (dict): attributes to be updated with
		next_attr (bool, optional): whether to choose next attribute from list or True. Defaults to True.
		unique (bool, optional): items to be unique or not. Defaults to False.
	"""    	
	if isinstance(nest_attrs, dict):
		for k, v in nest_attrs.items():
			if not v: continue
			if k not in spl: continue
			dic = add_blankdict_key(input_dict, k)
			get_nest_attributes(dic, line, spl, v, next_attr, unique)

	elif isinstance(nest_attrs, (list, tuple, set)):
		if next_attr:
			get_instance_parameter_for_items(input_dict, line, spl, nest_attrs, unique)
		else:
			update_true_instance_items(input_dict, line, spl, nest_attrs)

	else:
		print(f"[-] Unidentified attribute type: {type(nest_attrs)}, {nest_attrs}")

def get_appeneded_value(dic, key, value):
	"""appends the value to an existing value found in dictionary with provided key if exist other wise returns same value

	Args:
		dic (dict): dictionary
		key (str): dictionary key
		value (str): arbitrary value to be appended to existing key if exist

	returns:
		str: appened string
	"""
	if not dic.get(key):
		return value
	else:
		return dic[key] + '\n'+ value

def add_to_list(lst, item):
	"""appends item to list if not found

	Args:
		lst (list): list
		item (str, int): item to be added to list

	Returns:
		list: updated list
	"""	
	if item in lst:
		return lst
	return lst.append(item)


