# """
# # Dictionary converter for extremely nested dictionary to and from to excel data tabular format
# """
import pandas as pd
import yaml

# ----------------------------------------------------------------------------
INDEX_KEY_PARENTS = {'instances', 'ifphysicals', 'ifvlans', 'ifloopbacks', 'ifaggregates' } 

# ----------------------------------------------------------------------------
def varsheet(dic):
	"""convert and return captured var dictionary to FIND/REPLACE pairs of dict 
	to generate the DataFrame.
	constraint: var-sheet has column names "FIND" & "REPLACE"

	Args:
		dic (dict): dictionary with find/replace pairs as key/value pair

	Returns:
		dict: dictionary which is friendly to convert to DataFrame and ultimately to Excel
	"""    	
	ndic = {'FIND':[], 'REPLACE':[]}
	for k, v in dic.items(): 
		ndic['FIND'].append(k)
		ndic['REPLACE'].append(v)
	return ndic

def appendkey(dic, prefix=""):
	"""add the prefix to keys of dictionary and return updated dictionary. 
	conjuction will be "_".

	Args:
		dic (dict): dictionary
		prefix (str, optional): prefix to add on key while removing nesting. Defaults to "".

	Returns:
		dict: updated dictionary
	"""    	
	if not prefix: return dic
	ndic = {}
	for key, value in dic.items():
		ndic[prefix + "_" + key ] = value
	return ndic

def recursive_dic(dic, prevkey=''):
	"""recursive lookup in provided dictionary and serialize it to convert it to 
	pandas data frame which can be later used to convert to excel.
	returns updated dictionary with key:[list of values]

	Args:
		dic (dict): nested dictionary
		prevkey (str, optional): previous key to add as prefix. Defaults to ''.

	Returns:
		dict: updated dictionary
	"""    	
	opd = {}
	for dickey, dicvalue in dic.items():
		if isinstance(dicvalue, dict):
			opd.update( appendkey(recursive_dic(dicvalue, dickey), dickey ))
		else:
			opd[dickey] = dicvalue
	return opd

def standup_dic(dic, ikp):
	"""create and return a dictionary with basic basic keys/header
	OBSOLETE NOW.

	Args:
		dic (dict): dictionary
		ikp (_type_): basic mandatory interface id/types/value

	Returns:
		dict: dictionary with mandatory items
	"""    	
	ndic = {'inttype':[], 'intid':[], 'intvalues':[]}
	for dickey, dicvalue in dic.items():
		for dicvaluek, dicvaluev in dicvalue.items():
			if dickey in ikp:
				ndic['inttype'].append(dickey)
				ndic['intid'].append(dicvaluek)
			else:
				ndic['inttype'].append('')
				ndic['intid'].append('')
			ndic['intvalues'].append(dicvaluev)			# Hungami
	return ndic

def expand_var_dict(dic):
	"""rollback of varsheet(), revert the values to its original dictionary format.

	Args:
		dic (dict): dictionary

	Returns:
		dict: updated dictionary
	"""    	
	return {k:v for k, v in zip(dic['FIND'].values(),  dic['REPLACE'].values() )}

def expand_table_dict(dic):
	"""rollback of recursive_dic(), revert the key:value nested pairs to its original position.
	returns nested dictionary

	Args:
		dic (dict): dictionary

	Returns:
		dict: updated dictionary
	"""
	opd = {}
	inttypeset = set(dic['inttype'].values())
	for i, intid in dic['intid'].items():
		respectiveinttype = dic['inttype'][i]
		if not opd.get(respectiveinttype):
			opd[respectiveinttype] = {}
		if not opd[respectiveinttype].get(intid):
			opd[respectiveinttype][intid] = {}
	diccopy = dic.copy()
	for k, v in diccopy.items():
		if k in ('intid', 'inttype'): continue
		keys = k.split("_")
		for i, vitem in v.items():
			if not vitem: continue
			respectiveinttype = dic['inttype'][i]
			respectiveint = dic['intid'][i]
			dd = opd[respectiveinttype][respectiveint]
			opd[respectiveinttype][respectiveint] = update_nested_key(dd, keys, vitem)
	for k, v in diccopy.items():
		del(dic[k])
	return opd

def update_nested_key(dic, keys, vitem):
	"""add the nested keys in dictionary if missing, update value for trailing key, 
	and returns updated dictionary

	Args:
		dic (dict): dictionary
		keys (str): keys
		vitem (str,iterator,dict): any nested items

	Returns:
		dict: updated dictionary
	"""    	
	nd = dic
	for i, key in enumerate(keys):
		if i > 0:
			nd = dic[prevkey]
		if not nd.get(key): nd[key] = {}
		prevkey = key
	nd[key] = vitem
	return dic


def yaml_to_dict(file):
	"""reads yaml file and return data as dict format

	Args:
		file (str): yaml file

	Returns:
		dict: dictionary formatted data
	"""    	
	with open(file, 'r') as f:
		return yaml.safe_load(f)


def dict_to_yaml(d, file=None, mode='a'):
	"""converts dictionary to yaml and write it out to a file

	Args:
		d (dict): dictionary
		file (str): output file name ( display on screen otherwise )
		mode (str): character string of mode a=append, w=write mode.

	"""    	
	s = yaml.dump(d, indent=2)
	if file:
		with open(file, mode) as f:
			f.write(s)
	else: 
		print(s)
	return s


# ----------------------------------------------------------------------------
# Class to convert dictionary 
# ----------------------------------------------------------------------------
class ConvDict():
	"""convert dictionary to and from between nested and serialzed format
	"""

	def __init__(self, dic=None):
		"""initialize object

		Args:
			dic (dict, optional): dictionary to be convert to. Defaults to None.
		"""    		
		self.dic = dic
		self.set_var_table_keys()
		self.set_index_keys_parents()

	def set_var_table_keys(self, var='var', table='table'):
		"""standup variable of tab name, static variables:var , tabular data:table

		Args:
			var (str, optional): static find/replace kind data variable referance. Defaults to 'var'.
			table (str, optional): tabular data variable referance. Defaults to 'table'.
		"""    		
		self.var = var
		self.table = table

	def set_index_keys_parents(self, ikp=INDEX_KEY_PARENTS):
		"""set the parents of index keys

		Args:
			ikp (set, optional): Parent Index keys. Defaults to INDEX_KEY_PARENTS.
		"""    		
		self.index_keys_parents = ikp

	def convert_table_dic(self):
		"""convert the nested table dictionary to serialized format, returns serialized dict

		Returns:
			dict: updated table dictionary
		"""
		ndic = standup_dic(self.dic[self.table], self.index_keys_parents)
		ndiclen = len(ndic['intvalues'])
		for i, d in enumerate(ndic['intvalues']):
			rd = recursive_dic(d)
			for k, v in rd.items():
				if not ndic.get(k):
					ndic[k] = ["" for _ in range(ndiclen)]
				ndic[k][i] = v
		del(ndic['intvalues'])
		return ndic

	def convert_var_dic(self):
		"""convert the var key:value pair to a dictionary of list of FIND/REPLACE pairs

		Returns:
			dict: updated var dictionary
		"""    		
		return varsheet(self.dic[self.var])

	def to_dataframe(self, sheetname):
		"""convert the given sheetname dictionary to necessary serialized format and convert and 
		return to pandas dataframe object

		Args:
			sheetname (str): Sheet Name

		Returns:
			DataFrame: dataframe
		"""
		if sheetname == self.var:
			return pd.DataFrame(self.convert_var_dic()).fillna("")
		if sheetname == self.table:
			return pd.DataFrame(self.convert_table_dic()).fillna("")

	def expand_to_dict(self, df_var, df_table):
		"""expand the provided dataframes of var/table to nested dictionary and return it

		Args:
			df_var (DataFrame): var (find/replace) pairs dictionary
			df_table (DataFrame): tabular data dictionary

		Returns:
			dict: dictionary of converted data
		"""    		
		d_var = df_var.to_dict()
		opdv = self.expand_dfdic_to_dict(self.var, d_var)
		d_table = df_table.to_dict()
		opdt = self.expand_dfdic_to_dict(self.table, d_table)
		opd = {self.var: opdv}
		opd.update(opdt)
		return opd

	def expand_dfdic_to_dict(self, sheetname, dic):
		"""expand the provided dictionary to nested dictionary and return it

		Args:
			sheetname (str): sheet name
			dic (dict): dataframe dictionary

		Returns:
			dict: dictionary of converted dictionary
		"""    		
		if sheetname == self.var:
			return expand_var_dict(dic)
		if sheetname == self.table:
			return expand_table_dict(dic)




# ----------------------------------------------------------------------------
if __name__ == '__main__':
	pass
# ----------------------------------------------------------------------------
