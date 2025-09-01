# -----------------------------------------------------------------------------
import os
from copy import deepcopy
from nettoolkit.nettoolkit_common import *
from nettoolkit.nettoolkit_db import read_xl_all_sheet
from nettoolkit.addressing import *
from pprint import pprint
from pathlib import Path

import nettoolkit.facts_finder as ff
from collections import OrderedDict

from .exec_device import Execute_Device
from .common import exec_log
from .cap_summary import TableReport

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------
# COMMON methods and variables defining class
# -----------------------------------------------------------------------------------------------
class Execute_Common():
	"""common methods/variables declaration in a Execute Common class

	Args:
		auth (dict): authentication parameters
		capture_path (str): path to where captures to be stored
		exec_log_path (str): path to where device execution logs to be stored.


	Raises:
		Exception: raise exception if any issue with authentication or connections.
	"""	

	# set authentication and default parameters
	def __init__(self, auth, capture_path, exec_log_path):
		self._add_auth_para(auth)
		self._add_path(capture_path=capture_path, exec_log_path=exec_log_path)
		self._set_defaults()

	# verify data, start capture, write logs
	def __call__(self):
		self._verifications()
		print_banner("CaptureIT", 'blue')
		self.start()

	def _add_auth_para(self, auth):
		"""add authentication parameters to self instance
		
		Args:
			auth (dict): authentication parameters

		Returns:
			None
		"""
		if not isinstance(auth, dict):
			raise Exception(f"[-] authentication parameters needs to be passed as dictionary")
		if not auth.get('un') or auth['un'] == '':
			raise Exception(f"[-] authentication parameters missing with username `un`")
		if not auth.get('pw') or auth['pw'] == '':
			raise Exception(f"[-] authentication parameters missing with password `pw`")
		if not auth.get('en') or auth['en'] == '':
			auth['en'] = auth['pw']
		self.auth = auth

	def _add_path(self, capture_path, exec_log_path):
		"""add path parameters to self instance
		
		Args:
			path (dict): path parameters

		Returns:
			None
		"""
		## Validations
		if not isinstance(capture_path, str):
			raise Exception(f"[-] capture path parameter needs to be passed as string, got {type(capture_path)}")
		if exec_log_path and not isinstance(exec_log_path, str):
			raise Exception(f"[-] log path parameter needs to be passed as string, got {type(capture_path)}")
		cp, elp = Path(capture_path), Path(exec_log_path)
		if not (cp.exists() and cp.is_dir()):
			try:
				os.makedirs(str(cp))
			except:
				raise Exception(f"[-] Provided capture path is invalid, please check input. `{capture_path}`")
		if not (elp.exists() and elp.is_dir()):
			try:
				os.makedirs(str(elp))
			except:
				raise Exception(f"[-] Provided capture path is invalid, please check input. `{capture_path}`")
		#
		self.capture_path = capture_path 
		self.exec_log_path = exec_log_path if exec_log_path else capture_path
			

	def _set_defaults(self):
		"""setting the default value for optional user input parameters
		"""		
		self.cumulative = True
		self.forced_login = True
		self.parsed_output = False
		self.standard_output = False
		self.CustomClass = None
		self.CustomDeviceFactsClass = None
		self.foreign_keys = {}
		self.fg = False
		self.max_connections = 100
		self.mandatory_cmds_retries = 1
		self.missing_captures_only = False
		self.append_capture = False or self.missing_captures_only
		self.tablefmt = 'pretty'
		#
		self.cmd_exec_logs_all = OrderedDict()
		self.device_type_all = OrderedDict()
		self.failed_devices = {}

	def _verifications(self):
		"""Verification/Validation of input values
		"""
		if self.cumulative not in (True, False, 'both'):
			print(f"[-] Invalid cumulative arument found: [{self.cumulative}]. capture-log files will not be generated." )
		if not isinstance(self.max_connections, int):
			print(f"[-] Invalid number of `max_connections` defined [{self.max_connections}], default [100].")
			self.max_connections = 100

	## -------------- variable user inputs hook -------------- ##

	def dependent_cmds(self, custom_dynamic_cmd_class):
		"""Provide dependent commands via a class definition.  A new variable set of commands can be passed
		here using defined custom_dynamic_cmd_class class.  Defined class must have an abstract property called `cmds`. 
		which should return a new set/list of commands to be executed.  A good example of usage of it is - 
		derive the bgp neighbor ip addresses from show ip bgp summary output, and then create new set of commands to see
		advertised route for those neighbor ip addresses.  In this way no need to create a separate set of show commands for multiple
		devices, custom class will take care of generating additional show commands to see advertized routes based on neighbors 
		appear on bgp summary output. ( ofcouse, show ip bgp summary should be there in original show capture ) 		

		Args:
			custom_dynamic_cmd_class (_type_): _description_

		Raises:
			Exception: invalid input `custom_dynamic_cmd_class` for wront types
			Exception: mandatory property missing `cmds` for missing property in provided class
		"""	
		if not self.cumulative and custom_dynamic_cmd_class:
			print(f"[-] Cumulative should be [True] or ['both'], in order to execute custom commands. Otherwise it will be skipped.")
			self.CustomClass = None
			return None
		#
		if not hasattr(custom_dynamic_cmd_class, '__class__'):
			raise Exception(f"[-] invalid input [custom_dynamic_cmd_class],  expected instance of [class], got [{type(custom_dynamic_cmd_class)}]")
		try:
			custom_dynamic_cmd_class.cmds
		except AttributeError:
			raise Exception(f"[-] mandatory property [cmds] is missing in provided class, please implement.")
		self.CustomClass = custom_dynamic_cmd_class


	##  -------------- Some other common functions --------------  ##

	def is_valid(self, ip):
		"""Validation function to check if provided ip is valid IPv4 or IPv6 address

		Args:
			ip (str): ipv4 or ipv6 address

		Returns:
			bool: True/False based on validation success/fail
		"""    		
		try:
			return ip and Validation(ip).version in (4, 6)
		except:
			print(f'[-] Device Connection: {ip} :: Skipped due to bad Input')
			return False


	## -------------- generate Facts usings Facts-Finder hook -------------- ##

	def generate_facts(self, CustomDeviceFactsClass=None, foreign_keys={}):
		"""generate excel facts -clean.xlsx file using facts finder

		Args:
			CustomDeviceFactsClass (class, optional): class definition for the modification of excel facts with custom properties. Defaults to None.
			foreign_keys (dict, optional): custom keys(aka: custom columns) here in order to accept them and display in appropriate order. Defaults to {}.

		Raises:
			Exception: Invalid type: foreign_keys if recieved in format other than dict.
		"""		
		self.fg = True if self.cumulative else False
		if not self.fg and CustomDeviceFactsClass:
			print(f"[-] Cumulative should be [True] or [`both`] in order to generate facts. Otherwise it will be skipped.")
			return None
		self.CustomDeviceFactsClass = CustomDeviceFactsClass
		if isinstance(foreign_keys, dict):
			self.foreign_keys = foreign_keys
		else:
			raise Exception(f'[-] Invalid type: [foreign_keys]. Required [dict] got [{type(foreign_keys)}]')


	def _ff_sequence(self, ED, CustomDeviceFactsClass, foreign_keys):
		"""facts finder execution sequences, BPC

		Args:
			ED (Execute_Device): Execute_Device class instance post capture finishes
			CustomDeviceFactsClass (class): class definition for the modification of excel facts with custom properties.
			foreign_keys (_type_): custom keys(aka: custom columns) 
		"""	
		info_banner = " : INFO : Facts-Generation : "
		# -- cleate an instance --
		cleaned_fact = ff.CleanFacts(
			capture_log_file=ED.cumulative_filename, 
			capture_parsed_file=None,
			convert_to_cit=False,
			skip_txtfsm=True,
			new_suffix='-clean',
			use_cdp=False,
		)
		# ------------------------------------------------------------------------
		try:
			hn = ED.hostname
			# -- execute it --
			print(f"[+] {hn}{info_banner}Starting Data Cleaning...")
			cleaned_fact()
			print(f"[+] {hn}{info_banner}Data Cleaning done...")
		except:
			print(f"[-] {hn}{info_banner}Data Cleaning failed, facts will NOT be generated !!!")
			return None
		# ------------------------------------------------------------------------
		if CustomDeviceFactsClass:
		# -- custom facts additions --
			try:
				print(f"[+] {hn}{info_banner}starting Custom Data Modifications...")
				ADF = CustomDeviceFactsClass(cleaned_fact)
				ADF()
				ADF.write()
				print(f"[+] {hn}{info_banner}Custom Data Modifications done...")
			except:
				print(f"[-] {hn}{info_banner}Custom Data Modifications failed, custom facts will NOT be added !!")
				pass
		# ------------------------------------------------------------------------
		try:
			# -- rearranging tables columns --
			print(f"[+] {hn}{info_banner}Column Rearranging..., ")
			ff.rearrange_tables(cleaned_fact.clean_file, foreign_keys=foreign_keys)
			print(f"[+] {hn}{info_banner}Column Rearrangemnet done...")
		except:
			print(f"[-] {hn}{info_banner}Column Rearrangemnet failed, facts columns may not be in proper order !")
			pass
		# ------------------------------------------------------------------------
		print(f"[+] {hn}{info_banner}Facts-Generation Tasks Finished !!! {hn} !!")
		# ------------------------------------------------------------------------

	def log_summary(self, *, onscreen, to_file=None, excel_report_file=None):
		"""display and write log summary to output file(s)

		Args:
			onscreen (bool): Display report on screen
			to_file (str, optional): text file name to store summary report. Defaults to None.  (Deprycated, and fn removed..)
			excel_report_file (str, optional): excel file name to store summary report. Defaults to None.
		"""
		self.show_failures
		ER = TableReport(
			self.all_cmds,
			self.cmd_exec_logs_all,
			self.host_vs_ips,
			self.device_type_all,
		)
		ER()
		if onscreen: ER.show(tablefmt=self.tablefmt)
		if excel_report_file: ER.write_to(excel_report_file)


	@property
	def show_failures(self):
		"""Displays failure summary
		"""    		
		if not self.failed_devices: return
		banner = f"\n! {'='*20} [ FAILED DEVICES LIST ] {'='*20} !\n"
		print(banner)
		pprint(tuple(self.failed_devices.keys()))
		print(f"\n! {'='*72} !\n")
		#
		banner = f"\n! {'='*20} [ FAILED DEVICES AND REASONS ] {'='*20} !\n"
		print(banner)
		pprint(self.failed_devices)
		print(f"\n! {'='*72} !\n")

	def _execute(self, ip, cmds):
		"""execution function for a single device. hn == ip address in this case.

		Args:
			ip (str): ip address of a reachable device
		"""
		self.append_capture = self.append_capture or self.missing_captures_only
		# - capture instance -
		dev_exec_kwargs = {
			'ip': ip,
			'auth': self.auth, 
			'cmds': cmds, 
			'capture_path': self.capture_path, 
			'cumulative': self.cumulative,
			'forced_login': self.forced_login, 
			'parsed_output': self.parsed_output,
			'standard_output': self.standard_output,
			'CustomClass': self.CustomClass,
			'fg': self.fg,
			'mandatory_cmds_retries': self.mandatory_cmds_retries,
			'append_capture': self.append_capture,
			'missing_captures_only': self.missing_captures_only,		
		} 
		ED = Execute_Device(**dev_exec_kwargs)
		###
		self.update_other_properties(executed_device=ED, ip=ip)
		self.update_all_cmds(executed_device=ED)
		self.generate_clean_facts_file(executed_device=ED)
		self.write_exec_log(executed_device=ED)

	def update_other_properties(self, executed_device, ip):
		"""update other properties of the current object 

		Args:
			executed_device (Execute_Device): Device Execution object instance
			ip (str): device ip address or FQDN
		"""	
		if executed_device.dev:
			self.cmd_exec_logs_all[executed_device.hostname] = executed_device.cmd_exec_logs
			self.device_type_all[executed_device.hostname] =  executed_device.dev.dtype
			self.host_vs_ips[executed_device.hostname] = ip
		else:
			self.failed_devices[ip] = executed_device.failed_reason

	# - update all cmds
	def update_all_cmds(self, executed_device):
		"""update executed commands for all commands dictionary 

		Args:
			executed_device (Execute_Device): Device Execution object instance
		"""	
		if not executed_device.dev: return
		dt = executed_device.dev.dtype
		if not self.all_cmds.get(dt):
			self.all_cmds[dt] = []
		self.all_cmds[dt].extend(list(executed_device.all_cmds[dt]))

	# - facts generations -
	def generate_clean_facts_file(self, executed_device):
		"""generate facts-generator clean file  

		Args:
			executed_device (Execute_Device): Device Execution object instance
		"""	
		if self.fg and executed_device.dev: 
			self._ff_sequence(executed_device, self.CustomDeviceFactsClass, self.foreign_keys)

	# - write exec log -
	def write_exec_log(self, executed_device):
		"""write/display execution log file for the devices  

		Args:
			executed_device (Execute_Device): Device Execution object instance
		"""	
		ts = LOG.time_stamp().replace(":", "-")
		try:
			exec_log_file = f'{self.exec_log_path}/{executed_device.hostname}-exec-{ts}.log'
			exec_log(msg=executed_device.tmp_device_exec_log, to_file=exec_log_file)
		except:
			print(f"[-] {executed_device.ip} - Fatal - Unable to write execution log. Below is summary of execution\n(\n")
			print(executed_device.tmp_device_exec_log, "\n)")


# -----------------------------------------------------------------------------------------------
# Execute class - capture_it - for common commands to all devices
# -----------------------------------------------------------------------------------------------

class Execute_By_Login(Multi_Execution, Execute_Common):
	"""Execute the device capture by logging in to device.

	Args:
		ip_list (set, list, tuple): set of ip addresses to be logging for capture
		auth (dict): authentication parameters ( un, pw, en)
		cmds (set, list, tuple): set of commands to be captured
		path (str): path where output(s), logs(s) should be stored.

	Properties:

		* cumulative (bool, optional): True: will store all commands output in a single file, False will store each command output in differet file. Defaults to False. and 'both' will do both.
		* forced_login (bool, optional): True: will try to ssh/login to devices even if ping respince fails. False will try to ssh/login only if ping responce was success. (default: False)

		* max_connections (int, optional): 100: manipulate how many max number of concurrent connections to be establish. default is 100.
		* CustomClass (class): Custom class definitition to execute additional custom commands

	Raises:
		Exception: raise exception if any issue with authentication or connections.

	"""    	

	def __init__(self, 
		ip_list, 
		auth, 
		cmds, 
		capture_path=None, 
		exec_log_path=".",
		path=".",                      ##  Backward compatible, till next major release
		):
		if capture_path is None:                                  ##  Backward compatible, till next major release
			Execute_Common.__init__(self, auth, path, exec_log_path)   ##  Backward compatible, till next major release
		else:
			Execute_Common.__init__(self, auth, capture_path, exec_log_path)
		#
		self.devices = STR.to_set(ip_list) if isinstance(ip_list, str) else set(ip_list)
		self.cmds = cmds
		self.all_cmds = {}
		self.capture_path = capture_path
		#
		self.host_vs_ips = {}
		if not isinstance(cmds, dict):
			raise Exception("[-] Commands are to be in proper dict format")
		#
		super().__init__(self.devices)

	def execute(self, ip):
		"""execution function for a single device. hn == ip address in this case.

		Args:
			ip (str): ip address of a reachable device
		"""
		self._execute(ip, deepcopy(self.cmds))




# -----------------------------------------------------------------------------------------------
# Execute class - capture_it - for selected individual commands for each device(s)
# -----------------------------------------------------------------------------------------------
class Execute_By_Individual_Commands(Multi_Execution, Execute_Common):
	"""DEPRYCATED 
	"""    	

	def __init__(self, 
		auth, 
		dev_cmd_dict, 
		capture_path=None, 
		exec_log_path=".",
		path=".",                      ##  Backward compatible, till next major release
		):
		deprycation_warning("class: Execute_By_Individual_Commands")

# -----------------------------------------------------------------------------------------------
# Execute class - capture_it - for provided Excel sheet
# -----------------------------------------------------------------------------------------------
class Execute_By_Excel(Execute_Common, Multi_Execution):

	def __init__(self, 
		auth, 
		input_file, 
		capture_path=".", 
		exec_log_path=".",
		):
		Execute_Common.__init__(self, auth, capture_path, exec_log_path)
		self.input_file = input_file
		self.get_devices_commands_dicts()
		self.remove_blank_entries()
		self._override_defaults()
		self.items = self.devices

	def _override_defaults(self):
		self.host_vs_ips = {}
		self.all_cmds = {}
		self.device_type_all = OrderedDict()
		self.fg = False
		self.CustomClass = None
		self.cumulative = True

	def __call__(self):
		print_banner("CaptureIT", 'blue')
		self._verifications()
		self.start()
		self.log_summary(onscreen=True, excel_report_file='report_summary.xlsx')

	def execute(self, ip):
		self._execute(ip, self.ip_cmd_dict[ip])

	def get_devices_commands_dicts(self):
		"""generate standard format dictionary from excel tabs
		"""    		
		cmd_cols = ('cisco_ios', 'juniper_junos', 'arista_eos')
		df_dict = read_xl_all_sheet(self.input_file)
		self.ip_cmd_dict = {}
		#
		for tab, df in df_dict.items():
			for ip in df.ips:
				if not ip: continue
				ipdict = add_blankdict_key(self.ip_cmd_dict, ip)
				for cmdcol in cmd_cols:
					add_blankset_key(ipdict, cmdcol)
					try:
						ipdict[cmdcol] = ipdict[cmdcol] | set(df[cmdcol])
					except:
						pass
		#
		self.devices = list(self.ip_cmd_dict.keys())

	def remove_blank_entries(self):
		self.ip_cmd_dict = {
			ip: { cmd_type:LST.remove_empty_members(sorted(cmds_list))  for cmd_type, cmds_list in cmds_dict.items() } 
			for ip, cmds_dict in self.ip_cmd_dict.items()
		}



# -----------------------------------------------------------------------------------------------
