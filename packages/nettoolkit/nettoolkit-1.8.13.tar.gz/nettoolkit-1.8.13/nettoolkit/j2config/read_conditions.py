
# ---------------------------------------------------------------------------------------
import pandas as pd
from dataclasses import dataclass, field
from nettoolkit.nettoolkit_common import LST, STR
from nettoolkit.nettoolkit_db import read_xl_all_sheet

# ---------------------------------------------------------------------------------------

def get_conditions(jinja_file):
	"""get all conditional statements from jinja file

	Args:
		jinja_file (str): jinja template file

	Returns:
		dict: dictionary with list of jinja variables, conditions, and loops.
	"""	
	d = {'conditions':set(), 'loops':set(), 'variables': set() }
	with open(jinja_file, 'r') as f:
		lns = f.readlines()
	for ln in lns:
		if ln.strip().startswith("{% for "):
			d['loops'].add(ln)
		elif ln.strip().startswith("{% if") or ln.strip().startswith("{% elif"):
			d['conditions'].add(ln)
		elif ln.strip().startswith("{% set "):
			d['variables'].add(ln)
	return d

def get_variables(jinja_file):
	"""get all jinja variables defined in jinja file

	Args:
		jinja_file (str): jinja template file

	Returns:
		set: set of jinja variables
	"""	
	conds = set()
	with open(jinja_file, 'r') as f:
		lns = f.readlines()
	for ln in lns:
		starts, ends = [], []
		for i in range(20):
			if i == 0: s,e = 0,0
			start = STR.find_multi(ln, '{{', start=s, count=None, index=True, beginwith=False)
			end   = STR.find_multi(ln, '}}', start=e, count=None, index=True, beginwith=False)
			if start == -1: break
			starts.append(start)
			ends.append(end)
			s = start+2
			e = end+2

		if starts == []: continue
		for s, e in zip(starts, ends):
			cond = ln[s:e+2]
			conds.add(cond)
	return conds

# ---------------------------------------------------------------------------------------
#  Jinja variables check class
# ---------------------------------------------------------------------------------------

@dataclass
class JinjaVarCheck():
	jinja_file: str
	clean_file: str
	global_file: str = ''

	def __post_init__(self):
		self.variables = get_variables(self.jinja_file)
		self.var_df = pd.read_excel(self.clean_file, sheet_name='var').fillna("") 
		if self.global_file:
			self.global_df = pd.read_excel(self.global_file).fillna("") 
		else:
			self.global_df = pd.DataFrame()
		self.dfd = read_xl_all_sheet(self.clean_file)

	def __call__(self):
		self.jinja_var_only_variables = set(self._get_var_only_variables())
		self.device_xl_var_only_variables = set(self.var_df['var'])
		if not self.global_df.empty:
			self.global_xl_var_only_variables = set(self.global_df['var'])
		# self.xl_table_variables = self._get_xl_table_variables()
		# self.jinja_table_variables = set(self._get_otherthan_vars_variables())
		self._merge_global_device_vars()
		self._check()

	def _merge_global_device_vars(self):
		if not self.global_df.empty:
			self.xl_var_only_variables = self.device_xl_var_only_variables | self.global_xl_var_only_variables
		else:
			self.xl_var_only_variables = self.device_xl_var_only_variables

	def _get_xl_table_variables(self):
		del(self.dfd['var'])
		table_vars = set()
		for df in self.dfd.values():
			table_vars = table_vars | set(df.keys())
		return table_vars

	def _get_var_only_variables(self):
		nvs = []
		for v in self.variables:
			v = v.split("{{")[-1].split("}}")[0].strip()
			v = v.split("|")[0].strip()
			if v.startswith("var."):
				nvs.append(v[4:])
		return nvs

	def _get_otherthan_vars_variables(self):
		nvs = []
		for v in self.variables:
			v = v.split("{{")[-1].split("}}")[0].strip()
			v = v.split("|")[0].strip()
			if not v.startswith("var."):
				spl = v.split(".")
				if len(spl) > 1:
					if spl[1].startswith("index"): continue
					s = ".".join(spl[1:])
					nvs.append(s)
		return nvs

	def _check(self):
		self.xl_var_missing = self.jinja_var_only_variables - self.xl_var_only_variables
		# self.jinja_var_missing = self.xl_var_only_variables - self.jinja_var_only_variables
		# self.xl_table_missing = self.jinja_table_variables - self.xl_table_variables
		# self.jinja_table_missing = self.xl_table_variables - self.jinja_table_variables



