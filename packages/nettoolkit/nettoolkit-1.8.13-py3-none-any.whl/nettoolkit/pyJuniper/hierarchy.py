# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from collections import OrderedDict

from .hierarchy_rules import *
from nettoolkit.nettoolkit_common.gpl import STR, IO

# # -- Enablebelow - only if Max Recursion depth reach.
# import sys
# sys.setrecursionlimit(10**5)


def mysplit(line, by=" "):
	"""
	split line by (default space), also retain the strings like descriptions as it is.

	Args:
		line (str): string line
		by (character, optional): Split by option. Defaults to " ".

	Returns:
		list: split line and return list
	"""
	spl = line.split(by)
	for item in description_strings:
		if item in spl:
			s1 = spl[:spl.index(item)+1]
			s2 = " ".join(spl[spl.index(item)+1:])
			s1.append(s2)
			return s1
	return spl


def li_li_words(in_str):
	"""
	converts multiline string in to list of list of words.

	Args:
		in_str (str): Multiline string

	Returns:
		list: list of list of words.
	"""
	return [[w for w in mysplit(line[4:])] for line in in_str.split('\n')]


def section_dict(in_list, word, full_review=False):
	"""
	create section dectionary from given input list for the selected word.

	Args:
		in_list (list, str): Input list or string
		word (str): selected word for which list to be search up on and generate dictionary
		full_review (bool, optional): go thru full list if set to true, else only check first match only. Defaults to False.

	Raises:
		NotImplementedError: Unmatched input type for input.

	Returns:
		dict: dictionary with key equal input word and value as list of words from matched suffixes.
	"""
	section_config_dict = OrderedDict()
	section_config_dict[word] = []
	if isinstance(in_list, str):
		in_list = li_li_words(in_list)
	elif isinstance(in_list, (list, tuple)): 
		pass
	else:
		raise NotImplementedError
	for line in in_list:
		section_config_list = []
		add_to = False
		for i, w in enumerate(line):
			wordCheck = i == 0
			if wordCheck and w == word: 
				add_to = True
				continue
			elif wordCheck and w != word:
				if not full_review: break
			if add_to:
				section_config_list.append(w)
		if add_to:
			section_config_dict[word].append(section_config_list)
		else:
			if not full_review: break
	return section_config_dict


def zero_items(in_list):
	"""
	Return all Zero (0) indexed Items from list of lists

	Args:
		in_list (list): input list of lists

	Returns:
		list: all 0-index items from list of lists
	"""
	_zi = []
	for item_zero in in_list:
		if item_zero[0] not in _zi: _zi.append(item_zero[0])
	return _zi


def related_list(in_list, word):
	"""
	filter input list for the given word in index-0 position

	Args:
		in_list (list): input list of list
		word (str): word to be check in index-0 position.

	Returns:
		list: filtered output list 
	"""
	section_config_list = []
	for line in in_list:
		add_to = line[0] == word
		if add_to: section_config_list.append(line)
	return section_config_list


def recursive_item_lookup(lili_words):
	"""
	create and yields dictionary/list from provided list of list of words.

	Args:
		lili_words (list): input list of list of words

	Yields:
		dict: yields dictionary item/value pairs
	"""
	for ezi in zero_items(lili_words):
		nv = related_list(lili_words, ezi)
		ns_dic = section_dict(nv, ezi)
		yield ns_dic


def excluded(dic, members, member_key):
	"""Checks for matching key from provided dictionary (dic) in to members dictionary's member_key,
	returns True if found any.

	Args:
		dic ([type]): input dictionary for which keys to be searched in to members dictinary members
		members ([type]): members dicationary to be looked in to.
		member_key (str): member key to be looked in to members dictionary

	Returns:
		bool: True if any excluded member found, None Else
	"""
	if member_key in members:
		for k in dic.keys():
			if k in members[member_key]:
				return True


def included(dic, members, member_key):
	"""Checks for matching key from provided dictionary (dic) in to members dictionary's member_key,
	returns True if found or member_key not found in members dict.

	Args:
		dic ([type]): input dictionary for which keys to be searched in to members dictinary members
		members ([type]): members dicationary to be looked in to.
		member_key (str): member key to be looked in to members dictionary

	Returns:
		bool: True if any excluded member found or member_key not in members, False Else
	"""
	if member_key in members:
		for k in dic.keys():
			if k in members[member_key]:
				return True
		return False
	else:
		return True


class Section():
	"""Configuration Section Creator"""

	def __init__(self, in_list, ordered=False):
		"""Section Object Initializer

		Args:
			in_list (list): list of list
			ordered (bool, optional): Section Dictionary to be ordered or unordered. Defaults to False.
		"""
		self.lst = in_list
		self.dic = OrderedDict()
		if not ordered: self.dic = {}
		self.add(ordered)

	def add(self, ordered):
		"""add the key value to self.dic
		go thru recursive lookup for dictionary tree

		Args:
			ordered (bool): dictionary to be ordered or not
		"""
		try:
			for dic in recursive_item_lookup(self.lst):
				if isinstance(dic, OrderedDict):
					for k, v in dic.items():
						s = Section(v, ordered=ordered)
						self.dic[k] = s.dic

		except: pass


class Convert():
	"""Converts Dicationary to Hierarchical config string

	Args:
		dic (dict): dictionary
		tabs (int): front tabs
		is_tailed (bool, optional): tailed config. Defaults to True.
		is_grouped (bool, optional): grouped config. Defaults to False.
		is_distributed (bool, optional): distributed config. Defaults to False.
		is_straight (bool, optional): straight config. Defaults to False.
		is_straight_anyway (bool, optional): straight anyway config. Defaults to False.
		parent_prefix (str, optional): parent prefix. Defaults to ''.

	"""

	def __init__(self, 
		dic, 
		tabs, 
		is_tailed=True,
		is_grouped=False,
		is_distributed=False,
		is_straight=False,
		is_straight_anyway=False,
		parent_prefix = '',
		test=False
		):
		"""Initializer
		"""		
		self.dic = dic
		self.tabs = tabs
		self.is_tailed = is_tailed
		self.is_grouped = is_grouped
		self.is_distributed = is_distributed
		self.is_straight = is_straight
		self.is_straight_anyway = is_straight_anyway
		self.parent_prefix = parent_prefix
		self.test = test
		self.s = ''
		self.tab = '    '
		self.front_tabs = self.tabs
		self.convert

	def __str__(self): return self.s

	@property
	def front_tabs(self): return self._front_tabs

	@front_tabs.setter
	def front_tabs(self, tabs): self._front_tabs = f'{self.tab*tabs}'

	def add_to_str(self, s): self.s += s

	def update_front_tabs(self, n):
		"""update front tab value with add of n

		Args:
			n (int): adds n to tabs
		"""		
		self.tabs += n
		self.front_tabs = self.tabs

	def update_prefix(self, k):
		"""update prefix value to k

		Args:
			k (str): key to be added
		"""		
		if self.parent_prefix:
			self.prefix = self.front_tabs + self.parent_prefix + " " + k
		else:
			self.prefix = self.front_tabs + k
		if self.is_tailed or self.is_straight:
			self.prefix = self.parent_prefix + " " + k
		if self.is_distributed:
			pfx_list = self.prefix.split()[-1]
			if pfx_list[-1] != k:
				self.prefix = self.front_tabs + self.parent_prefix + " " + k


	@property
	def convert(self):
		"""
		start Converting dictionary to config string.

		Returns:
			None: None
		"""
		if len(self.dic) == 0: return None
		for dic_key, dic_value in self.dic.items():
			self.exception(dic_key)
			self.update_prefix(dic_key)
			if isinstance(dic_value, (dict, OrderedDict)):
				self.update_front_tabs(1)
				self.update_prefix(dic_key)

				if self.logic_terminators(dic_key, dic_value):
					pass
				elif self.logic_groups(dic_key, dic_value):
					pass

				self.update_front_tabs(-1)
		self.closure

	# - LOGICS -----------------------------------------------------

	def exception(self, dic_key):
		"""Exceptional identifiex configurations - Add more as found any

		Args:
			dic_key (str): key to be found in set line
		"""		
		if self.tabs == -1:
			if dic_key == 'policy-options':
				# candidates_not_expand_in_anycase.clear()
				candidates_not_expand_if_single.clear()
				candidates_not_expand_if_single.add('from')
				candidates_not_expand_if_single.add('then')
				candidates_not_expand_if_single.add('community')
			elif dic_key =='firewall':
				# candidates_not_expand_in_anycase.clear()
				candidates_not_expand_if_single.clear()
				candidates_not_expand_if_single.add('then')
			elif dic_key =='class-of-service':
				# candidates_not_expand_in_anycase.clear()
				candidates_not_expand_if_single.clear()
				candidates_not_expand_if_single.add('class')
			else:
				candidates_not_expand_if_single.clear()
				# candidates_not_expand_in_anycase.clear()

	def logic_terminators(self, dic_key, dic_value):
		"""line terminators selector logic

		Args:
			dic_key (str): string key to be pass on to selector logic
			dic_value (dic): dictionary for the key to be pass on to selector logic

		Returns:
			bool: Returns True if any terminator logic matches found else None
		"""

		# if self.test : print(dic_key)
		# if self.is_straight: print(dic_key)

		# ex: destination-port [ <"telnet tacacs ldap 636"> ];
		if self.is_grouped:
			self.clubbed_candidate_terminator_lines(dic_key, dic_value)
			return True

		# ex: <"community add blue;\n community add yellow;\n ....">
		elif self.is_distributed:
			self.distributed_candidate_terminator_lines(dic_key, dic_value)
			return True

		# Terminators
		elif not dic_value :
			# ex: <"ip-protocol tcp;">
			# ex: <"0.0.0.0/0;">
			self.terminator_line
			return True

	def logic_groups(self, dic_key, dic_value):
		"""section group selector logic

		Args:
			dic_key (str): string key to be pass on to selector logic
			dic_value (dic): dictionary for the key to be pass on to selector logic
		"""


		# if self.test : print(dic_key)
		# if self.is_straight: print(dic_key)
		if dic_key == "community": self.test = True
		if False: pass

		elif (len(dic_value) == 1 
			and (self.is_straight
				or dic_key in candidates_not_expand_if_single)
			):
			self.grp_candidate_straight(dic_key, dic_value)

		# elif (self.is_straight_anyway
		# 	or dic_key in candidates_not_expand_in_anycase
		# 	):
		# 	self.grp_candidate_straight_anyway(dic_key, dic_value)

		# ex: <"destination-port"> [ telnet tacacs ldap 636 ];
		elif dic_key in candidates_can_club_members:
			self.grp_candidates_clubbed(dic_key, dic_value)

		# ex: <"community add blue;\n community add yellow;\n ....">
		elif (dic_key in candidates_distributed_to_multi_lines
			and not excluded(dic_value, candidates_distributed_to_multi_lines_exclude, dic_key)
			and included(dic_value, candidates_distributed_to_multi_lines_include, dic_key)
			):
			self.grp_candidates_distributed(dic_key, dic_value)

		# ex: <"term"> al_att_forward_class2_protocol_seq_100 {
		elif (dic_key in candidates_require_suffix
			and not excluded(dic_value, candidates_require_suffix_exclude_members, dic_key)
			and included(dic_value, candidates_require_suffix_include_members, dic_key)
			):
			self.grp_has_suffix_candidate(dic_key, dic_value)

		# ex: term <"al_att_forward_class2_protocol_seq_100"> {
		elif self.is_tailed:
			self.grp_suffixes(dic_key, dic_value)

		# ex: <"ip-source-address"> {
		else: 
			self.grp_nested(dic_key, dic_value)


	# - CLOSURES -----------------------------------------------------

	@property
	def closure(self):
		"""Append Section closure to string """
		if not self.is_tailed and not self.is_grouped:
			s = self.front_tabs + "}\n"
			self.add_to_str(s)
		

	# - TERMINATORS -----------------------------------------------------

	@property
	def terminator_line(self):
		s = self.prefix + ";\n"
		self.add_to_str(s)

	def clubbed_candidate_terminator_lines(self, dic_key, dic_value):
		"""Clubbed candidates terminator words getting added to string

		Args:
			dic_key (str): key/string to be added to config
			dic_value (dict): sub-section config (if any)
		"""		
		# if self.test : print(dic_key)
		sObj = Convert(dic_value, self.tabs, is_tailed=True, is_grouped=True)
		s = dic_key + " " + str(sObj)
		self.add_to_str(s)

	def distributed_candidate_terminator_lines(self, dic_key, dic_value):
		"""Distributed terminator candidate words getting added to string

		Args:
			dic_key (str): key/string to be added to config
			dic_value (dict): sub-section config (if any)
		"""		
		# if self.test : print(dic_key)
		for k, v in dic_value.items():
			s = self.prefix + " " + k + ";\n"
			self.add_to_str(s)


	# - GROUPS -----------------------------------------------------
	"""
	Args:
		dic_key (str): key/string to be added to config
		dic_value (dict): sub-section config (if any)

	Returns:
		None: None
	"""

	def grp_candidate_straight(self, dic_key, dic_value):
		"""group config, which has straight candidate

		Args:
			dic_key (str): key/string to be added to config
			dic_value (dict): sub-section config (if any)
		"""		
		# if self.test : print(self.is_straight, dic_key)
		sObj = Convert(dic_value, self.tabs, is_tailed=True, is_straight=self.is_straight)
		# if self.test: print(">", self.prefix, sObj.s)
		s = self.prefix + str(sObj)
		self.add_to_str(s)

	# def grp_candidate_straight_anyway(self, dic_key, dic_value):
	# 	s = dic_key
	# 	for k, v in dic_value.items():
	# 		# print(k)
	# 		sObj = Convert(v, self.tabs, is_tailed=True, is_straight_anyway=self.is_straight_anyway, test=self.test)
	# 		s += "X" + k + "\n"
	# 	self.add_to_str(self.prefix + s)

		
	def grp_has_suffix_candidate(self, dic_key, dic_value):
		"""group config, which has suffix candidate.

		Args:
			dic_key (str): key/string to be added to config
			dic_value (dict): sub-section config (if any)
		"""		
		# if self.test : print(self.is_straight, dic_key)
		if len(dic_value) > 1:
			sObj = Convert(dic_value, self.tabs, is_tailed=True, parent_prefix=self.prefix)
			s = str(sObj)
		else:
			sObj = Convert(dic_value, self.tabs, is_tailed=True)
			s = self.prefix + str(sObj)
		self.add_to_str(s)

	def grp_suffixes(self, dic_key, dic_value):
		"""group config

		Args:
			dic_key (str): key/string to be added to config
			dic_value (dict): sub-section config (if any)
		"""		
		# if self.test : print(dic_key)
		self.update_front_tabs(-1)
		sObj = Convert(dic_value, self.tabs, is_tailed=False)
		s = self.prefix + " {\n"+ str(sObj)
		self.add_to_str(s)
		self.update_front_tabs(1)

	def grp_candidates_clubbed(self, dic_key, dic_value):
		"""clubbed group config

		Args:
			dic_key (str): key/string to be added to config
			dic_value (dict): sub-section config (if any)
		"""		
		# if self.test : print(dic_key)
		sObj = Convert(dic_value, self.tabs, is_tailed=True, is_grouped=True)
		if dic_value.get("") and len(dic_value[""]) > 1:
			s = self.prefix + " ["+ str(sObj) + "];\n"
		else:
			s = self.prefix + " "+ str(sObj)[:-1] + ";\n"
		self.add_to_str(s)

	def grp_candidates_distributed(self, dic_key, dic_value):
		"""Distributed group config

		Args:
			dic_key (str): key/string to be added to config
			dic_value (dict): sub-section config (if any)
		"""		
		# if self.test : print(dic_key)
		pp = self.parent_prefix + dic_key
		sObj = Convert(dic_value, self.tabs-1, is_tailed=True, is_distributed=True, parent_prefix=pp)
		s = str(sObj)
		self.add_to_str(s)

	# DEFAUT AT END
	def grp_nested(self, dic_key, dic_value):
		"""nested group config

		Args:
			dic_key (str): key/string to be added to config
			dic_value (dict): sub-section config (if any)
		"""		
		# ELSE AFTER ALL grp matches
		# if self.test : print(dic_key)
		sObj = Convert(dic_value, self.tabs, is_tailed=False)
		s = self.prefix + " {\n"+ str(sObj)
		self.add_to_str(s)


class Hierarchy():
	"""Hierarchical config conversion

	Args:
		input_file (str): input set config file
		output_file (str): output file

	"""	

	def __init__(self, input_file, output_file):
		"""Object initializer
		"""		
		self.input_file = input_file
		self.output_file = output_file

	def convert(self):
		"""convert input file
		"""		
		section = self._gen_section_dict( IO.file_to_str(self.input_file) )
		self._conv_dict_to_hierarchy(section)

	def _gen_section_dict(self, input_file_lst):
		return Section(li_li_words(input_file_lst), 
					ordered=False)

	def _conv_dict_to_hierarchy(self, section):
		self.output = str(Convert(section.dic, -1, is_tailed=False))



# ------------------------------------------------------------------------------
if __name__ == '__main__':
	pass
# ------------------------------------------------------------------------------
