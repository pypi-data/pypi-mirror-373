# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from inspect import signature

import pandas as pd

from abc import ABC, abstractproperty, abstractclassmethod
import datetime
from re import compile
from collections import OrderedDict
import os
import threading
from getpass import getpass
from .common import deprycation_warning

intBeginWith = compile(r'^\D+')
# ------------------------------------------------------------------------------
# Standard number of characters for identifing interface short-hand
# ------------------------------------------------------------------------------
PHYSICAL_IFS = OrderedDict()
PHYSICAL_IFS.update({
		'Ethernet': 2, 
		'FastEthernet': 2,
		'GigabitEthernet': 2, 
		'TenGigabitEthernet': 2, 
		'FortyGigabitEthernet':2, 
		'HundredGigE':2,
		'AppGigabitEthernet': 2,
		'mgmt': 4,
		'Async': 5,
})
PHYSICAL_IFS['TwoGigabitEthernet'] = 3     # Do not alter sequence of these two.
PHYSICAL_IFS['TwentyFiveGigE'] = 3  # ....
CISCO_IFSH_IDENTIFIERS = {
	"VLAN": {'Vlan':2,},
	"TUNNEL": {'Tunnel':2,},
	"LOOPBACK": {'Loopback':2,} ,
	"AGGREGATED": {'Port-channel':2,},
	"PHYSICAL": PHYSICAL_IFS,
	"NVI": {'NVI':2,},
	"NV": {'NV':2,},
}
JUNIPER_IFS_IDENTIFIERS = {
	"VLAN": ('irb', 'vlan', 'iw'),
	"LOOPBACK": ('lo', ),
	"RANGE": ('interface-range', ),
	"TUNNEL": ('lt', 'gr', 'ip', 'mt', 'vt', 'vtep', 'xt' ),
	"AGGREGATED": ('ae', 'as', 'fc'),
	"PHYSICAL": ('fe', 'ge', 'xe', 'et', 'xle', 'fte', ),
	"MANAGEMENT": ('mg', 'em', 'me', 'fxp', 'vme', 'bme', 'bm'),
	"INTERNAL": ('sxe', 'bcm', 'cp', 'demux', 'dsc', 'es', 'gre', 'ipip', 'ixgbe', 'lc','lsi', 'mo',
		'ms', 'pd', 'pimd', 'rlsq', 'rms', 'rsp', 'sp', 'tap', 'umd', 'vsp', 'vc4',  ),
	"CIRCUIT": ('at', 'cau4', 'ce1', 'coc1', 'coc3', 'coc12', 'coc48', 'cstm1', 'cstm4', 'cstm16', 
		'ct1', 'ct3', 'ds', 'e1', 'e3', 'ls', 'ml', 'oc3', 'pip', 'se', 'si',  'so', 'stm1', 'stm4', 'stm16',
		't1', 't3',    ),
	"MONITORING": ('dfc', ),
}

# -----------------------------------------------------------------------------
#                              Common Classes                                 #
# -----------------------------------------------------------------------------


def get_username():
	"""input username prompt

	Returns:
		str: entered username
	"""	
	return input("Enter Username: ")

def get_password():
	"""input password prompt

	Returns:
		str: entered password
	"""	
	return getpass("Enter Password: ")


class Default():
	"""Default class representing class docString template"""
	def __str__(self): return self.__doc__
	def _repr(self):
		fields = signature(self.__init__).parameters
		values = ", ".join(repr(getattr(self, f)) for f in fields)
		return f'{type(self).__name__}({values})'



class Container(ABC):
	"""Abstract base class providing template for standard dunder 
	methods template.  Object should contain objVar property
	"""	

	@abstractproperty
	@property
	def objVar(self): pass
	def __bool__(self): return True if self.objVar else False
	def __len__(self): return len(self.objVar)
	def __dir__(self): return self.objVar # sorted
	def __getitem__(self, i): return self.objVar[i]
	def __setitem__(self, i, v): self.objVar[i] = v
	def __delitem__(self, i): del(self.objVar[i])
	def __contains__(self, i): return i in self.objVar
	def __reversed__(self): 
		if isinstance(self.objVar, dict):
			for k in reversed(tuple(self.objVar.keys())):
				yield (k,self[k])
		else:
			return reversed(self.objVar)
		
	def __missing__(self, i): raise Exception(f'[-] key {i} unavailable') # only for dict subclass
	def __iter__(self):
		if isinstance(self.objVar, (list, tuple, set, str)):
			for line in self.objVar:
				yield line
		elif isinstance(self.objVar, (dict, OrderedDict)):
			for key, value in self.objVar.items():
				yield (key, value)

## TBD / NOT IMPLEMENTED YET ##
# class Numeric():
# 	"""Support Numberic objects"""
# 	def __add__(self): pass
# 	def __sub__(self): pass
# 	def __mul__(self): pass
# 	def __truediv__(self): pass
# 	def __floordiv__(self): pass
# 	def __pow__(self): pass
# 	def __lshift__(self): pass
# 	def __rshift__(self): pass
# 	def __and__(self): pass
# 	def __xor__(self): pass
# 	def __or__(self): pass

# 	def __iadd__(self): pass
# 	def __isub__(self): pass
# 	def __imul__(self): pass
# 	def __itruediv__(self): pass
# 	def __ifloordiv__(self): pass
# 	def __ipow__(self): pass
# 	def __ilshift__(self): pass
# 	def __irshift__(self): pass
# 	def __iand__(self): pass
# 	def __ixor__(self): pass
# 	def __ior__(self): pass

# 	def __neg__(self): pass
# 	def __pos__(self): pass
# 	def __abs__(self): pass
# 	def __invert__(self): pass


# -----------------------------------------------------------------------------
#                           STRING OPERATIONS                                 #
# -----------------------------------------------------------------------------
class STR(Container):
	"""Collection of static methods for string objects.
	see more...	
	"""

	@staticmethod
	def foundPos(s, sub, pos=0):
		'''Search for substring in string and return index value result

		Args:
			s (str): main string to be search within
			sub (str): substring which is to be search in to main string
			pos (int, optional): position index, search to be start from. Defaults to 0.

		Returns:
			int: find index value
		'''		
		return s.find(sub, pos)

	@staticmethod
	def found(s, sub, pos=0):
		"""Search for substring in string and return Boolean result

		Args:
			s (str): main string to be search within
			sub (str): substring which is to be search in to main string
			pos (int, optional): position index, search to be start from. Defaults to 0.

		Returns:
			bool: find or not
		"""		
		try:
			return True if s.find(sub, pos) > -1 else False
		except:
			return False

	@staticmethod
	def find_within(s, prefix, suffix=None, pos=0):
		"""finds characters between prefix and suffix substrings from string

		Args:
			s (str): main string to be search within
			prefix (str): starting substring
			suffix (str, optional): ending substring. Defaults to None.
			pos (int, optional): position index, search to be start from. Defaults to 0.

		Returns:
			tuple: (str, int) (returned string, position of returned suffix position)
		"""		
		p = STR.foundPos(s, prefix, pos=pos)+len(prefix)
		if suffix is None:
			ln = len(s)
		else:
			ln = STR.foundPos(s, suffix, pos=p+1)
		if p == -1:
			return None
		if ln == -1:
			ln = len(s)
		return (s[p:ln], ln)

	@staticmethod
	def string_within(line, prefix, suffix=None, pos=0):
		"""finds characters between prefix and suffix substrings from string

		Args:
			line (str): main string to be search within
			prefix (str): starting substring
			suffix (str, optional): ending substring. Defaults to None.
			pos (int, optional): position index, search to be start from. Defaults to 0.

		Returns:
			tuple: (str, int) (returned string, position of returned suffix position)
		"""		

		return STR.find_within(line, prefix, suffix, pos)[0]

	@staticmethod
	def suffix_index_within(line, prefix, suffix=None, pos=0):
		"""finds characters between prefix and suffix substrings from string

		Args:
			line (str): main string to be search within
			prefix (str): starting substring
			suffix (str, optional): ending substring. Defaults to None.
			pos (int, optional): position index, search to be start from. Defaults to 0.

		Returns:
			int: index of suffix
		"""	
		return STR.find_within(line, prefix, suffix, pos)[1]

	@staticmethod
	def find_multi(s, sub, start=0, count=None, index=True, beginwith=False):
		"""search for multiple substrings 'sub' within string 's'.
		Usage: find_multi(s, sub, [start=n, [count=c], index=True])

		Args:
			s (str): main string
			sub (str, tuple, list): sub string ( to be search within main string )
			start (int, optional): Optional: substring to be start search from index . Defaults to 0.
			count (int, optional): Optional: count of character from start index. Defaults to None.
			index (bool, optional): Optional: return index or boolean values. Defaults to True.
			beginwith (bool, optional): Optional: check if substring is at beginning. Defaults to False.

		Returns:
			list: list of indexes/bool
		"""		
		count = len(s) if count is None else count+start
		if isinstance(sub, str):
			i = s.find(sub, start, count) 
			if index:
				if beginwith:
					return i if i == 0 else -1
				else:
					return i
			else:
				if beginwith:
					return True if i == 0 else False
				else:
					return False if i == -1 else True
		elif isinstance(sub, (tuple, list)):
			sl = []
			for x in sub:
				sl.append(STR.find_multi(s, x, start, count, index, beginwith))
			return sl
		else:
			return None

	@staticmethod
	def find_all(s, sub, start=0, count=None, beginwith=False):
		"""search for multiple substrings 'sub' within string 's' 
		Usage: find_all(s, sub, [start=n, [count=c]])

		Args:
			s (str): main string
			sub (str): sub string ( to be search within main string )
			start (int, optional): Optional: substring to be start search from index. Defaults to 0.
			count (int, optional): Optional: count of character from start index. Defaults to None.
			beginwith (bool, optional): Optional: check if substring is at beginning. . Defaults to False.

		Returns:
			bool: all matches or not
		"""		
		sl = STR.find_multi(s, sub, start, count, False, beginwith)
		try:
			return False if False in sl else True
		except:
			return sl

	@staticmethod
	def find_any(s, sub, start=0, count=None, beginwith=False):
		"""search for multiple substrings 'sub' within string 's' 
		Usage: find_any(s, sub, [start=n, [count=c]])

		Args:
			s (str): main string
			sub (str): sub string ( to be search within main string )
			start (int, optional): Optional: substring to be start search from index. Defaults to 0.
			count (int, optional): Optional: count of character from start index. Defaults to None.
			beginwith (bool, optional): Optional: check if substring is at beginning. . Defaults to False.

		Returns:
			bool: for atleast one matches
		"""		
		sl = STR.find_multi(s, sub, start, count, False, beginwith)
		try:
			return True if True in sl else False
		except:
			return sl

	@staticmethod
	def update(s, searchItem='', replaceItem=''):
		"""find n replace string s

		Args:
			s (str): main string
			searchItem (str, optional): search string. Defaults to ''.
			replaceItem (str, optional): replacement string. Defaults to ''.

		Returns:
			str: updated string
		"""		
		return s.replace(searchItem, replaceItem)

	@staticmethod
	def replace_dual_and_split(s, duo=' ', strip=None):
		"""Finds subsequent characters in string and replace those with single,
		plus, splits the string using provided character (duo).

		Args:
			s (str): main string
			duo (str, optional): characters which requires reductions if susequent. Defaults to ' '.
			strip (int, optional): values (-1=lstrip ,0=strip ,1=rstrip) . Defaults to None.

		Returns:
			list: split using dual characters
		"""		
		return STR.finddualnreplacesingle(s, duo, strip=strip).split(duo)

	@staticmethod
	def finddualnreplacesingle(s, duo=' ', strip=None):
		"""Finds subsequent characters in string and replace those with single.

		Args:
			s (str): Source string
			duo (str, optional): characters which requires reductions if susequent. Defaults to ' '.
			strip (int, optional): values (-1=lstrip ,0=strip ,1=rstrip). Defaults to None.

		Returns:
			_type_: _description_
		"""		
		while s.find(duo+duo) > -1:
			s = s.replace(duo+duo, duo)
		if strip is not None and isinstance(strip, int):
			if strip == -1:
				return s.lstrip()
			elif strip == 0:
				return s.strip()
			elif strip == 1:
				return s.rstrip()
			else:
				pass
				# print('invalid strip value detected', strip)
		else:
			pass
			# print('invalid strip value detected', strip)
		return s

	@staticmethod
	def indention(s):
		"""get string indention value

		Args:
			s (str): input string

		Returns:
			int: number of indentants
		"""		
		return len(s)-len(s.lstrip())

	@staticmethod
	def is_blank_line(s):
		"""is provided string/line a blank line

		Args:
			s (str): input string

		Returns:
			bool: boolean value for result
		"""		
		try:
			return True if len(s.strip()) == 0 else False
		except Exception: pass

	@staticmethod
	def is_hostname_line(s, host):
		"""string/line containing hostname of device

		Args:
			s (str): input string
			host (str): hostname to be find in provided string

		Returns:
			bool: boolean value for result
		"""		
		return s.find(host) == 0

	@staticmethod
	def hostname(net_connect):
		"""input paramiko netconnection, returns hostname from device.

		Args:
			net_connect (connection object): paramiko connection object

		Returns:
			str: hostname from connection
		"""		
		try:
			hns = net_connect.find_prompt()[:-1]
			atPos = STR.foundPos(hns, "@")
			if atPos > -1: hns = hns[atPos+1:]
			return hns
		except:
			pass

	@staticmethod
	def hostname_from_cli(line, command):
		"""input standard text input line, for which command was entered

		Args:
			line (str): input line string
			command (str): command

		Returns:
			str: hostname from command line
		"""		
		if not STR.found(line, command): return None
		cmdPos = STR.foundPos(line, command)
		hn = line[:cmdPos].strip()[:-1]
		return hn

	@staticmethod
	def shrink_if(intName, length=2):
		"""Interface Name shortening, input length will decide number of 
		charactes to be included in shortened output

		Args:
			intName (str): interface
			length (int, optional): interface identifier prefix length. Defaults to 2.

		Returns:
			str: short name of interface
		"""		
		if not intName: return ""
		if intName.lower().startswith("tw"): length=3
		iBW = intBeginWith.match(intName)
		return iBW.group()[:length]+intName[iBW.span()[1]:]

	@staticmethod
	def if_prefix(intName):
		"""Interface beginning Name

		Args:
			intName (str): interface

		Returns:
			str: interface prefix
		"""		
		if not intName: return ""
		iBW = intBeginWith.match(intName)
		return intName[iBW.start(): iBW.end()]

	@staticmethod
	def if_suffix(intName):
		"""Interface ending ports

		Args:
			intName (str): interface

		Returns:
			str: interface suffix
		"""		
		if not intName: return ""
		try:
			iBW = intBeginWith.match(intName)
			return intName[iBW.end():]
		except:
			return ""

	@staticmethod
	def if_standardize(intName, expand=True):
		"""standardize the interface for uneven length strings.
		expand will give fulllength, otherwise it will shrink it to its standard size given

		Args:
			intName (str): interface
			expand (bool, optional): expansion of interface. Defaults to True.

		Returns:
			str: standardized interface
		"""		
		if not intName: return intName
		intName = intName.replace(" ", "")
		pfx = STR.if_prefix(standardize_if(intName))
		sfx = STR.if_suffix(intName)
		for _, inttype_length in CISCO_IFSH_IDENTIFIERS.items():
			for int_type, length in inttype_length.items():
				if int_type.lower().startswith(pfx.lower()):
					if expand:
						return f"{int_type}{sfx}"
					else:
						return f"{int_type[:length]}{sfx}"
		return intName

	@staticmethod
	def intf_standardize_or_null(intName, intf_type=None, expand=True):
		"""standardize the interface for uneven length strings.
		expand will give fulllength, otherwise it will shrink it to its standard size given
		for incorrect interface returns blank (None)

		Args:
			intName (str): interface
			expand (bool, optional): expansion of interface. Defaults to True.

		Returns:
			str: standardized interface or blank 
		"""		
		try:
			return standardize_if(intName)
		except:
			return ""

	@staticmethod
	def update_str(s, searchItem='', replaceItem=''):
		"""Updates line for search item with replace item
		(Find/Repalace)

		Args:
			s (str): input string
			searchItem (str, optional): search item. Defaults to ''.
			replaceItem (str, optional): replacement item. Defaults to ''.

		Returns:
			str: updated string
		"""		
		return s.replace(searchItem, replaceItem)

	@staticmethod
	def get_logfile_name(folder, hn, cmd='', ts='', separator="_@_", extn='.log'):
		"""return log file name for the command on device with/wo provided time_stamp

		Args:
			folder (str): path to where file should be saved
			hn (str): file name starting with provided host-name
			cmd (str, optional): file name containing additional commands string. Defaults to ''.
			ts (str, optional): file name containing additional time stamp. Defaults to ''.
			separator (str, optional): hn-cmd-ts separator . Defaults to "_@_".
			extn (str, optional): extension of filename. Defaults to '.log'.

		Returns:
			str: filename along with full path
		"""		
		if ts: ts = separator + ts
		cmd += ts
		if cmd:
			replaceCandidates = ('|',  '\\', '/', ':', '*', '?', '"', '<', '>')
			for x in replaceCandidates:
				cmd = STR.update_str(cmd, x, "_")
			cmd = separator + cmd
		if folder[-1] not in ( "/", "\\"):
			folder += "/" 
		return folder+hn+cmd+extn

	@staticmethod
	def string_concate(s, s1, conj=''):
		"""Concatenate strings s and s1 with conjuctor conj

		Args:
			s (str): input string
			s1 (str): adder string
			conj (str, optional): conjuctor. Defaults to ''.

		Returns:
			str: updated string
		"""		
		return s + s1 if s == '' else s + conj + s1

	@staticmethod
	def right(strg, n):
		"""N-number of characters from right side of string

		Args:
			strg (str): input string
			n (int): number of characters from right

		Returns:
			str: string portion from right
		"""		
		l = len(strg)
		return strg[l-n:l]
		
	@staticmethod
	def mid(strg, pos, n=0):
		"""N-number of characters from position in string; default n is till end

		Args:
			strg (str): input string
			pos (int): position from where slice to begin
			n (int): number of characters from from slice(pos)

		Returns:
			str: string portion from middle
		"""		
		l = len(strg)
		if n > 0 :
			return strg[pos-1:pos+n-1]
		else:
			return strg[pos-1:]

	@staticmethod
	def delete_trailing_remarks(s):
		"""Deletes trailing remarks from Juniper config line/string

		Args:
			s (str): number of characters from right

		Returns:
			str: updated string
		"""		
		terminal = s.find(";")
		br_open = s.find("{")
		br_close = s.find("}")
		if s.find("##") > max(terminal, br_open, br_close) :
			s = s[:s.find("##")].rstrip()
			return s.rstrip()
		endingpos = STR.foundPos(s, ";")
		if endingpos < 0: endingpos = STR.foundPos(s, "{")
		if endingpos < 0: endingpos = STR.foundPos(s, "}")
		if endingpos > -1: return s[:endingpos+1]
		return s.rstrip()

	@staticmethod
	def to_list(s):
		"""Returns list for the provided string - s, 
		splits string by lines

		Args:
			s (str): multiline input string

		Returns:
			list: splitted lines
		"""		
		s = s.split("\n")
		for i, x in enumerate(s):
			s[i] = x + "\n"
		return s

	@staticmethod
	def to_set(s):
		"""Return set of values for the provided string - s.
		splits string by lines and comma

		Args:
			s (str): multiline input string

		Returns:
			set: splitted lines/items
		"""		
		if isinstance(s, str):
			_s = []
			for _ in s.split('\n'):
				_s.extend(_.split(','))
			return set(LST.remove_empty_members((_s)))
		else:
			return set(s)

	@staticmethod
	def header_indexes(line):
		"""input header string line of a text table.
		returns dictionary with key:value pair where 
		keys are header string and value are string index (position) of string in line

		Args:
			line (str): input header string

		Returns:
			dict: header with its index numbers
		"""		
		exceptional_headers = {}
		headers = OrderedDict()
		prev_k = None
		for k in STR.replace_dual_and_split(line.rstrip()):
			k = k.strip()
			key = k
			if key in exceptional_headers: key = "__"+key
			headers[key] = [STR.foundPos(line, k), None]
			if prev_k is not None:
				headers[prev_k][1] = STR.foundPos(line, k)
			prev_k = key
		headers[key][1] = 90
		return headers

	@staticmethod
	def header_indexes_using_splitby(line, split_by="  "):
		"""input header string line of a text table.
		returns dictionary with key:value pair where 
		keys are header string and value are string index (position) of string in line

		Args:
			line (str): input header string
			split_by (str): string using which line is to be broken

		Returns:
			dict: header with its index numbers
		"""		
		exceptional_headers = {}
		headers = OrderedDict()
		prev_k = None
		spl_line = LST.remove_empty_members(line.split(split_by))
		for k in spl_line:
			k = k.strip()
			key = k
			if key in exceptional_headers: key = "__"+key
			headers[key] = [STR.foundPos(line, k), None]
			if prev_k is not None:
				headers[prev_k][1] = STR.foundPos(line, k)
			prev_k = key
		headers[key][1] = 90
		return headers

	@staticmethod
	def prepend_bgp_as(bgp_as, n):
		"""`n` number of BGP AS Number prepending string.

		Args:
			bgp_as (str): bgp as number
			n (int): to repeat with

		Returns:
			str: as-path prepend string
		"""		
		s = ''
		for x in range(n): s += str(bgp_as) + " "
		return s[:-1]

	@staticmethod
	def ending(line, c): 
		"""check if line ends with c or not, same as native string.endswith()
		addition is it first strips the line and then checks

		Args:
			line (str): input string
			c (str): condition string

		Returns:
			bool: boolean value for result
		"""		
		return line.strip().endswith(c)

	@staticmethod
	def starting(line, c): 
		"""check if line starts with c or not, same as native string.startswith()
		addition is it first strips the line and then checks

		Args:
			line (str): input string
			c (str): condition string


		Returns:
			bool: boolean value for result
		"""		
		return line.strip().startswith(c)

# -----------------------------------------------------------------------------

def interface_type(ifname):
	"""get the interface type from interface string

	Args:
		ifname (str): interface name/string

	Raises:
		ValueError: raise error if input missing

	Returns:
		tuple: tuple with interface type (e.g PHYSICAL, VLAN...) and sub interface type 
		(e.g FastEthernet, .. ). None if not detected
	"""    	
	iname = ''
	for i in ifname:
		if not i.isdigit(): iname += i
		else: break
	ifname = iname
	if ifname: 
		for int_type, int_types in  CISCO_IFSH_IDENTIFIERS.items():
			for sub_int_type in int_types:
				if sub_int_type.startswith(ifname):
					return (int_type, sub_int_type)
	return ("", "")

def standardize_if(ifname, expand=False):
	"""standardized interface naming

	Args:
		ifname (str): variable length interface name
		expand (bool, optional): expand will make it full length name. Defaults to False.

	Raises:
		ValueError: if missing with mandatory input
		TypeError: if invalid value detected
		KeyError: if invalid shorthand key detected		

	Returns:
		str: updated interface string
	"""    	
	if not ifname:
		raise ValueError("Missing mandatory input ifname")
	if not isinstance(expand, bool): 
		raise TypeError(f"Invalid value detected for input expand, "
		f"should be bool.")
	if not isinstance(ifname, str): 
		raise TypeError(f"Invalid value detected for input ifname, "
		f"should be str.")
	srcifname = ''
	for i in ifname:
		if not i.isdigit(): srcifname += i
		else: break
	if not srcifname: return None
	try:
		it = interface_type(srcifname)
		if it: 
			int_type, int_pfx = it[0], it[1]
		else:
			return ifname
	except:
		raise TypeError(f"unable to detect interface type for {srcifname}")
	try:
		shorthand_len = CISCO_IFSH_IDENTIFIERS[int_type][int_pfx]
	except:
		if get_juniper_int_type(ifname): return ifname
		raise KeyError(f"Invalid shorthand Key detected {int_type}, {int_pfx}")
	if expand:  return int_pfx+ifname[len(srcifname):]
	return int_pfx[:shorthand_len]+ifname[len(srcifname):]

# -----------------------------------------------------------------------------




# -----------------------------------------------------------------------------
#                    FILE OPERATIONS/ CONVERSIONS                             #
# -----------------------------------------------------------------------------
class IO():
	"""Collection of static methods for IO objects.
	see more...	
	"""

	@staticmethod
	def copy_text_file(file):
		"""copy file.txt to file-copy.txt

		Args:
			file (str): file name
		"""	
		dst = file[:-4] + "-copy.txt"
		with open(file, 'r') as sf:
			with open(dst, 'w') as dt:
				dt.write(sf.read())

	@staticmethod
	def file_list_for_time_stamp(hn, ts, folder, splitter="_@_" ):
		"""collection of files from given folder where hostname (hn) 
		and timestamp (ts) found in the file name.

		Args:
			hn (str): hostname
			ts (str): time-stamp
			folder (str): folder ptah
			splitter (str, optional): splitter. Defaults to "_@_".

		Returns:
			set: files from log files
		"""		
		files = set()
		for file in os.listdir(folder):
			if not splitter in file: continue
			if hn in file and ts in file:
				files.add(file)
		return files

	@staticmethod
	def devices_on_log_files(folder, splitter="_@_"):
		"""collection of files from given folder where file extensions are .log

		Args:
			folder (str): folder path
			splitter (str, optional): splitter. Defaults to "_@_".

		Returns:
			set: devices names from log files
		"""		
		devices = set()
		for file in os.listdir(folder):
			if not splitter in file: continue
			hn = file.split(splitter)
			if hn[0][-4:] == '.log': hn[0] = hn[0][:-4]
			devices.add(hn[0])
		return devices

	@staticmethod
	def timestamps_for_device(devname, folder, splitter="_@_"):
		"""collection of time stamps of files from given folder
		for given hostnames.

		Args:
			devname (str): hostname
			folder (str): folder path
			splitter (str, optional): splitter. Defaults to "_@_".

		Returns:
			set: time stampls from log files.
		"""		
		stamps = set()
		for file in os.listdir(folder):
			if not splitter in file: continue
			if devname in file:
				stamp = file.split(splitter)
				if stamp[-1][-4:] == '.log': stamp[-1] = stamp[-1][:-4]
				stamps.add(stamp[-1])
		return stamps

	@staticmethod
	def file_to_str(file):
		"""Returns string output content of the provided file 

		Args:
			file (str): input file

		Returns:
			str: content of file
		"""		
		with open(file, 'r') as f: 
			s = f.read()
		return s

	@staticmethod
	def file_to_list(file):
		"""Returns list output content of the provided file 

		Args:
			file (str): input file

		Returns:
			list: content of file
		"""		
		file = file.strip()
		if file is None: return None
		with open(file, 'r') as f:
			lines = f.readlines()
		return lines

	@staticmethod
	def csv_to_tuple(csv):
		"""Returns tuple from the provided comma separated text values 

		Args:
			csv (str): input string

		Returns:
			tuple: comma separated values
		"""		
		if csv.find('"') and not csv.find('\"'):
			ln = csv.lstrip().split('"')
			return tuple([x for i, x in enumerate(ln) if i % 2 != 0])
		else:
			return tuple(csv.split(','))

	@staticmethod
	def to_file(filename, matter):
		"""Creates a file with matter

		Args:
			filename (str): filename with path to be creaed.
			matter (str, list, tuple): matter to write to new created file.
		"""		
		with open(filename, 'w') as f:
			if isinstance(matter, str):
				f.write(matter)
			elif isinstance(matter, (list, tuple, set)):
				f.write("\n".join(matter))
		return filename

	@staticmethod
	def add_to_file(filename, matter, cr=True):
		"""Writes List/text to output filename.

		Args:
			filename (str): input file
			matter (str, tuple, list): matter to write to new created file.
			cr (bool, optional): carriage return to add at end of each string/line. Defaults to True.

		Returns:
			_type_: _description_
		"""	
		if not filename: return None
		if isinstance(matter, str):
			if cr and matter and matter[-1] != "\n": matter += "\n"
			with open(filename, 'a') as f:
				f.write(matter)
		elif isinstance(matter, (list, tuple ,set)):
			for i in matter:
				IO.add_to_file(filename, i)

	@staticmethod
	def update(file, find_item, replace_item):
		"""Find and Replace on provided file and saves file

		Args:
			file (str): input file
			find_item (str): search item
			replace_item (str): replacement item
		"""		
		with open(file, 'r') as f:
			filedata = f.read()
		replace_item = str(replace_item)
		if replace_item == 'nan': replace_item = '' 
		newdata = filedata.replace(find_item, str(replace_item))
		with open(file, 'w') as f:
			f.write(newdata)

	@staticmethod
	def jinja_verification(folder):
		"""check all text files from provided folder for verification of jinja strings descrepencies

		Args:
			folder (str): folder to check all jinja files from

		Returns:
			str: verification outcomes
		"""		
		s = ''
		for file in os.listdir(folder):
			goahead = {'GOAHEAD FOR': 0, 'GOAHEAD END': 0,}
			repeatfor = {'REPEAT EACH': 0, 'REPEAT STOP': 0,}
			if not file.endswith(".txt"): continue
			with open(folder + "/" +  file, 'r') as f:
				rf = f.read()
				for k, v in goahead.items(): goahead[k] = rf.count(k)
				for k, v in repeatfor.items(): repeatfor[k] = rf.count(k)
			bg, eg = goahead['GOAHEAD FOR'], goahead['GOAHEAD END']
			br, er = repeatfor['REPEAT EACH'], repeatfor['REPEAT STOP']
			if bg != eg or br != er: s += f'Descrepencies found in file: <{file}>\n'
			if bg != eg: s += f"\tGOAHEAD conditions : begins {bg} v/s ends {eg}\n"
			if br != er: s += f"\tREPEAT conditions : begins {br} v/s ends {er}\n\n"
		return s

# -----------------------------------------------------------------------------
#                             LIST MODIFICATIONS                              #
# -----------------------------------------------------------------------------

class LST():
	""" Collection of static methods for list objects.
	see more...	
	"""

	@staticmethod
	def remove_empty_members(lst):
		"""house keeping of list, removes empty members from list

		Args:
			lst (list): input list

		Returns:
			list: updated list
		"""		
		empty_members = ('', None, 'N/A', 'nil', [])
		tmp_lst = [m for m in lst if not m in empty_members]
		return tmp_lst

	@staticmethod
	def expand_vlan_list(vlan_list):
		"""takes input vlan list, expands it's ranges if any within

		Args:
			vlan_list (list): input vlans list

		Raises:
			Exception: Invalid vlan number

		Returns:
			list: list of vlans (individual)
		"""		
		exp_vl_list = set()
		for v in vlan_list:
			if not v: continue
			try:
				vl = int(v)
				exp_vl_list.add(vl)
				continue
			except:
				s, e = v.split("-")
				try:
					s, e = int(s), int(e)
					r = set(range(s, e+1))
					exp_vl_list = exp_vl_list.union(r)
				except:
					raise Exception(f"[-] Invalid vlan number.  Expected int got {type(s)}, {type(e)}")
		return exp_vl_list

	@staticmethod
	def convert_vlans_list_to_range_of_vlans_list(vlan_list):
		"""converts list of individual vlans to a list of range of vlans

		Args:
			vlan_list (str): input list

		Returns:
			list: list of vlans (with ranges)
		"""		
		vlans_dict, vlans_list, prev, last_key = {}, [], "", ""
		vlan_list = sorted(LST.expand_vlan_list(vlan_list))
		for i, vlan in enumerate(vlan_list):
			if not vlan: continue
			if i == 0:
				prev = vlan
				last_key = vlan
				continue
			if vlan == prev + 1: 
				prev = vlan
				continue
			else:
				vlans_dict[last_key] = prev
				prev = vlan
				last_key = vlan
		else:
			vlans_dict[last_key] = prev
		
		for k, v in vlans_dict.items():
			if k == v:
				vlans_list.append(str(k))
			else:
				vlans_list.append(str(k) + "-" + str(v))    
		return vlans_list

	@staticmethod
	def list_variants(input_list):
		"""list of vlans in different format list of vlans, space separated string, comma separated string,		

		Args:
			input_list (list): input list

		Returns:
			dict: list variants (str, csv, ssv)
		"""		
		str_list = [str(_) 
			for _ in LST.convert_vlans_list_to_range_of_vlans_list(input_list)]
		ssv_list = " ".join(str_list)
		csv_list = ",".join(str_list)
		return {
			'str_list': str_list,
			'ssv_list': ssv_list,
			'csv_list': csv_list,			
		}

	@staticmethod
	def list_of_devices(list_of_files):
		"""get hostnames (first index item) from list of files.

		Args:
			list_of_files (list): input file list

		Returns:
			set: devices from file list
		"""		
		devices = set()
		for file in list_of_files:
			if not file.strip(): continue
			f = ".".join(os.path.basename(file).split(".")[:-1])
			hn = f.split("_")[0]
			if not hn in devices: devices.add(hn)
		return devices

	@staticmethod
	def split(lst, n):
		"""yield provided list with group of n number of items

		Args:
			lst (list): list of items
			n (int): items per group 

		Yields:
			list generator: group of items
		"""		
		s = 0
		lst = tuple(lst)
		for _ in range(s, len(lst), n):
			yield lst[_: s+n]
			s += n

	@staticmethod
	def list_to_octet(lst):
		"""joins and return string with provided list with '.', helpful in created ipv4 string with list of 4 numeric items.  Doesn't verify correctness of ip. any number can be concatenated with any numbers of instances.

		Args:
			lst (list): input ip address splitted by "."

		Returns:
			str: concatenated ip address
		"""		
		"""
		
		Returns str
		"""
		l = ''
		for x in lst: l = str(x) if l == '' else l +'.'+ str(x)
		return l

	@staticmethod
	def flatten(lst):
		"""flattens nested list to single list

		Returns:
			list: flattened list
		"""		
		l = []
		for _ in lst:
			if isinstance(_, str):
				l.append(_)
			elif isinstance(_, (set, tuple, list)):
				l.extend( LST.flatten(_) )
		return l

	@staticmethod
	def longest_str_len(lst):
		"""returns length of longest string from provided lst , members shoudl be of string type

		Args:
			lst (list): list of strings

		Returns:
			int: length of maximum length command
		"""		
		if lst:
			return max(len(str(_)) for _ in lst)
		else:
			return 0


# -----------------------------------------------------------------------------
#                          DICTIONARY MODIFICATIONS                           #
# -----------------------------------------------------------------------------

class DIC():
	"""Collection of static methods for dictionary objects.
	see more...	
	"""

	# INTERNAL : update dictionary d for provided keyvalue pairs
	# param: d: dest dictionary
	# param: kv: src dictionary with key value pairs
	# --> updated destn dict
	@staticmethod
	def __update_keyValue(d, kv):
		if isinstance(d, dict):
			for k, v in kv.items():
				if isinstance(v, dict):
					for x, y in v.items():
						d = DIC.merge_dict(d, kv)
				else:
					d[k] = v
		return d

	@staticmethod
	def merge_dict(dx, dy):
		"""Merges two dictionaries for identical keys 

		Args:
			dx (dict): first dictionary
			dy (dict): second dictionary

		Returns:
			dict: merged dictionary
		"""		
		for k, v in dy.items():
			try:
				dx[k] = DIC.__update_keyValue(dx[k], dy[k])
			except:
				dx[k] = dy[k]
		return dx

	@staticmethod
	def recursive_dic(dic, indention=0):
		"""convert dictionary (dic) to string. recursive dictionary increases indention. (deprycated, will be replaced with `dict_to_str`)

		Args:
			dic (dict): input dictionary
			indention (int, optional): number of spaces. Defaults to 0.

		Returns:
			str: Multiline string
		"""		
		s = ""
		if isinstance(dic, dict):
			for k, v in dic.items():
				s += f"{' '*indention}{k}\n"
				indention += 1
				s += DIC.recursive_dic(v, indention)
				indention -= 1
		elif isinstance(dic, (tuple,list,set)):
			for x in dic: 
				if x: s += str(x)+'\n'
		elif isinstance(dic, str):
			if dic: s+= f"  {' '*indention}{dic}\n"
		return s

	@staticmethod
	def dict_to_str(dic, indention=0):
		"""convert dictionary (dic) to string. recursive dictionary increases indention.

		Args:
			dic (dict): input dictionary
			indention (int, optional): number of spaces. Defaults to 0.

		Returns:
			str: Multiline string
		"""		
		LST.recursive_dic(dic, indention)

# -----------------------------------------------------------------------------
#                         DICTIONARY DIFFERECES                               #
# -----------------------------------------------------------------------------

class DifferenceDict(dict):
	"""Template class to get difference in two dictionary objects.
	use dunder +/- for adds/removes.	
	"""

	missing = "- "
	additive = "+ "

	def __init__(self, d):
		self.d = d

	def __sub__(self, d): return self.get_change(d, self.missing)
	def __add__(self, d): return self.get_change(d, self.additive)

	def get_change(self, d, change):
		"""compare current object/dict with provided new object/dict (ie: d) 
		and return differences based on change required ("- "/"+ ")

		Args:
			d (dict): dictionary of differences
			change (str): change type from ("- "/"+ ")  i.e. removed/added

		Returns:
			_type_: _description_
		"""		
		"""
		"""
		if isinstance(d, DifferenceDict):
			return dict_differences(self.d, d.d, change)
		elif isinstance(d, dict):
			return dict_differences(self.d, d, change)

# INTERNAL / RECURSIVE
# returns differences for provided subnet/change
# input subject can be of string/int/float/set/dictionary
# input change is change type prefix
# return value type depends on input subject type.
def _get_differences(subject, change):
	if isinstance(subject, (str, int, float)):
		diff = change + str(subject)
	elif isinstance(subject, set):
		diff = set()
		for item in subject:
			df = _get_differences(item, change)
			diff.add(df)
	elif isinstance(subject, dict):
		diff = dict()
		for key, value in subject.items():
			key = change + str(key)
			if value:
				diff[key] = _get_differences(value, change)
			else: 
				diff[key] = ''
	else:
		raise Exception(f"[-] InvalidSubjectTypeError: {type(subject)}:{subject}")
	return diff


def dict_differences(d1, d2, change):
	"""returns differences for provided two dictionaries 
	input d1, d2 type: string/int/float/set/dictionary
	input change is change type prefix (ex: " -", " +")
	return value type depends on input d1, d2 type.

	Args:
		d1 (str, int, float, set, dict): input 1
		d2 (str, int, float, set, dict): input 2
		change (str):  change type from ("- "/"+ ")  i.e. removed/added

	Raises:
		Exception: TypeMismatch

	Returns:
		dict: differences in dictionary format
	"""	
	diff = {}
	if d1 == d2: return None
	if (not (isinstance(d1, (dict, set)) or isinstance(d2, (dict, set))) and
		type(d1) != type(d2)): 		
		raise Exception(f"[-] TypeMismatch- d1:{type(d1)}d2:{type(d2)} - {d1}{d2}")
	if isinstance(d1, dict):
		for k_d1, v_d1 in d1.items():
			if k_d1 not in d2: 
				diff.update( _get_differences({k_d1: v_d1}, change) )
				continue
			if v_d1 == d2[k_d1]: continue
			diff[k_d1] = dict_differences(v_d1, d2[k_d1], change)
	elif isinstance(d1, set):
		diff = _get_differences(d1.difference(d2), change)
	else:
		if d1:
			diff = _get_differences(d1, change)

	return diff

# -----------------------------------------------------------------------------
#                         Common Dictionary Methods                           #
# -----------------------------------------------------------------------------
class DictMethods():
	"""PAPA DUNDER EXTENSIONS FOR DICTIONARY OBJECTS

	[self.dic is abstract property which gets iterates over]
	"""

	def __iter__(self):
		for k, v in self.dic.items():
			yield (k, v)

	def __getitem__(self, item):
		try:
			return self.dic[item]
		except KeyError:
			return None

	def __get__(self, key, item):
		try:
			return self[key][item]
		except KeyError:
			return None

	def __setitem__(self, item, value):
		self.dic[item] = value

	def __delitem__(self, srno):
		try:
			for k in sorted(self.dic.keys()):
				if k <= srno: continue
				self.dic[k-1] = self.dic[k]
			del(self.dic[k])
		except:
			raise KeyError

	def append(self, item, value):
		"""appends value to self[item] dictionary. create new list if no value found for item, appends to list if available.

		Args:
			item (str, int): key of dictionary
			value (list): value to be added to dictionary item

		Raises:
			Exception: WrongInput
		"""		
		try:
			if not self.dic.get(item):
				self.dic[item] = []
			elif isinstance(self.dic[item], (str, int)):
				self.dic[item] = [self.dic[item],]
			self.dic[item].append(value)
		except:
			raise Exception


# -----------------------------------------------------------------------------
#                              LOG OPERATIONS                                 #
# -----------------------------------------------------------------------------

class LOG():
	"""Collection of static methods for logging.
	see more...	
	"""

	@staticmethod
	def time_stamp():
		"""current time stamp (for log purpose)

		Returns:
			str: current datetime string
		"""		
		return str(datetime.datetime.now())[:19]

# -----------------------------------------------------------------------------
#                              D-B OPERATIONS                                 #
# -----------------------------------------------------------------------------

class DB():
	"""Collection of static methods for Database.
	see more...	
	"""

	@staticmethod
	def read_excel(file, sheet='Sheet1', **kwargs):
		"""reads a sheet from an excel

		Args:
			file (str): input excel file
			sheet (str, optional): sheet name. Defaults to 'Sheet1'.

		Returns:
			DataFrame: pandas Dataframe Object
		"""		
		deprycation_warning("class: DB")
		return pd.read_excel(file, sheet_name=sheet, **kwargs)



# ------------------------------------------------------------------------------
# Excel Data WRITE Class, use with context manager
# ------------------------------------------------------------------------------
class XL_WRITE():
	"""Excel file generate
	Deprycated: use methods available in nettoolkit.nettoolkitdb ( append_to_xl, write_to_xl) instead.
	This will be removed in future version

	Args:
		hostname (str): excel file
		folder (str): folder path
		index (bool, optional): write with index or not. Defaults to False.

	Returns:
		XL_WRITE: object instance
	"""	

	# Object Initializer
	def __init__(self, hostname, folder, index=False, **sht_df):
		"""initializer
		"""		
		deprycation_warning("class: XL_WRITE")
		i = 0
		self.hostname = hostname
		self.folder = folder
		while True:
			try:
				self.__create_excel(hostname, index, **sht_df)
				break
			except PermissionError:
				i += 1
				hostname = self.hostname+" ("+str(i)+")"
			except Exception as e:
				print(e)
				break

	def __repr__(self): return self.op_file

	# write to Excel/ INTERNAL
	def __create_excel(self, hostname, index, **sht_df):
		try:
			n = 0
			XL_READ(self.folder + '/'+hostname+'.xlsx', 'tables')
			while True:
				n += 1
				XL_READ(self.folder + '/'+hostname+'-'+str(n)+'.xlsx', 'tables')
		except:
			if n == 0:
				op_file = self.folder + '/'+hostname+'.xlsx'
			else:
				op_file = self.folder + '/'+hostname+'-'+str(n)+'.xlsx'
			self.op_file = op_file
			with pd.ExcelWriter(op_file) as writer_file:
				for sht_name, df in sht_df.items():
					df.to_excel(writer_file, sheet_name=sht_name, index=index)


# ------------------------------------------------------------------------------
# Excel Data Read Class
# ------------------------------------------------------------------------------
class XL_READ:
	"""Excel file read
	DEPRYCATED METHOD -- use - methods available in  nettoolkit.nettoolkitdb ( read_xl_all_sheet, read_an_xl_sheet, ) instead.
	This will be removed in future version

	Args:
		xl (str): Excel file name
		shtName (str, optional): sheet name. Defaults to 'Sheet1'.

	Returns:
		XL_READ: object instance

	Yields:
		tuple: sheetname, dataframe of the sheet
	"""	

	def __init__(self, xl, shtName='Sheet1'):
		"""initializer
		"""		
		deprycation_warning("class: XL_READ")
		self.df = pd.read_excel(xl, sheet_name=shtName)

	def __repr__(self):
		return 'Excel data reprezenting class as DataFrame Object - obj.df'

	def __len__(self): return self.df.last_valid_index()+1

	def __iter__(self):
		for header, value in self.df.items(): yield (header, value)		

	def __getitem__(self, key): return self.df[key]
		

	def filter(self, df=None, **kwarg):
		"""Filter Records

		Args:
			df (DataFrame, optional): pandas DataFrame. Defaults to None.

		Returns:
			DataFrame: filtered DataFrame
		"""		
		tmpdf = self.df if df is None else df
		for k, v in kwarg.items():
			try:
				tmpdf = tmpdf[tmpdf[k]==v]
			except: pass
		return tmpdf

	def column_values(self, column, **kwarg):
		"""selected column output, after filters applied

		Args:
			column (str, list): a single column name or , list of column names

		Returns:
			DataFrame: filtered columns
		"""		
		return self.filter(**kwarg)[column]




# -----------------------------------------------------------------------------
#                           Execution secquences                              #
# -----------------------------------------------------------------------------

class Multi_Execution(Default):
	"""Template methods for multi-threaded executions.
	[self.items items are eligible threaded candidates]
	"""

	max_connections = 100

	def __str__(self): return self._repr()

	def __init__(self, items=None):
		self.items = items

	def execute_steps(self, multi_thread=True):
		"""steps defining executions

		Args:
			multi_thread (bool, optional): Multithread or Sequencial. Defaults to True.
		"""		
		self.start(multi_thread)

	def start(self, multi_thread=True):
		"""starting up executins either threaded/sequencial

		Args:
			multi_thread (bool, optional): Multithread or Sequencial. Defaults to True.

		Returns:
			None: None
		"""		
		if not self.items: return None 
		if multi_thread:
			self.execute_mt()
		else: 
			self.execute_sequencial()

	def end(self):
		"""Closure process"""		
		pass

	def get_devices(self):
		"""get devices names from list of files"""
		self.devices = LST.list_of_devices(self.files)

	def execute_mt(self):
		"""threaded execution in groups 
		(self.max_connections defines max threaded processes) 
		"""
		for group, items in enumerate(LST.split(self.items, self.max_connections)):
			self.execute_threads_max(items)

	def execute_threads_max(self, item_list):
		"""threaded execution of a group

		Args:
			item_list (list, set, tuple): items to be iterated on
		"""		
		ts = []
		for hn in item_list:
			t = threading.Thread(target=self.execute, args=(hn,) )
			t.start()
			ts.append(t)
		for t in ts: t.join()

	def execute_sequencial(self):
		"""sequencial execution of items
		"""
		for hn in self.items: self.execute(hn)

	@abstractclassmethod
	def execute(self, hn): 
		"""abstract class method, to be executed for each item in self.items

		Args:
			hn (str, int, float): individual items to be executed for each
		"""		
		pass



def get_juniper_int_type(intf):
	"""returns juniper interface type

	Args:
		intf (str): juniper interface

	Returns:
		str: interface type (ge, xe, etc)
	"""	
	int_type = ""
	for k, v in JUNIPER_IFS_IDENTIFIERS.items():
		if intf.startswith(v):
			int_type = k
			break
	return int_type

def get_cisco_int_type(intf):
	"""returns cisco interface type

	Args:
		intf (str): cisco interface

	Returns:
		str: interface type (FastEthernet, GigEthernet, etc..)
	"""	
	return interface_type(intf)[0].lower()


def get_device_manu(intf):
	"""returns device type from provided interface

	Args:
		intf (str): interface

	Returns:
		device type: manufacturer (cisco, juniper)
	"""	
	jit = get_juniper_int_type(intf)
	cit = get_cisco_int_type(intf)
	if jit.lower() == 'physical': return "juniper"
	if cit.lower() == 'physical': return "cisco"
	return ""