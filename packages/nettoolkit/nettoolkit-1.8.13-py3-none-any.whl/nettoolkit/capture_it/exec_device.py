# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from time import sleep
from nettoolkit.nettoolkit_common import STR, LST, IP
from dataclasses import dataclass
import typing

from copy import deepcopy
import nettoolkit.facts_finder as ff
from nettoolkit.detect import DeviceType
from .conn import conn
from .captures import Captures
from .common import cmd_line_pfx

# -----------------------------------------------------------------------------
# Execution of Show Commands on a single device. 
# -----------------------------------------------------------------------------
@dataclass(init=True, repr=False, eq=False)
class Execute_Device():
	"""Execute a device capture

	Args:
		ip (str): device ip
		auth (dict): authentication parameters
		cmds (list, set, tuple): set of commands to be executed.
		capture_path (str): path where output to be stored
		cumulative (bool, optional): True,False,both. Defaults to False.
		forced_login (bool): True will try login even if device ping fails.
		parsed_output (bool): parse output and generate Excel or not.
		CustomClass(class): Custom class definition to provide additinal custom variable commands
		fg(bool): facts generation
		mandatory_cmds_retries(int): number of retries for missing mandatory commands captures
		append_capture(bool): append capture to existing file instead of creating new.
		missing_captures_only(bool): capture only missing command outputs from existing output
	"""    	
	ip                    : str
	auth                  : dict
	cmds                  : list
	capture_path          : str
	cumulative            : bool 
	forced_login          : bool
	parsed_output         : bool
	standard_output       : bool
	CustomClass           : 'typing.Any'
	fg                    : bool
	mandatory_cmds_retries: int
	append_capture        : bool
	missing_captures_only : bool

	def __post_init__(self):
		self.all_cmds = {'cisco_ios': set(), 'juniper_junos':set(), 'arista_eos': set()}
		self.cumulative_filename = None
		self.delay_factor, self.dev = None, None
		self.cmd_exec_logs = []
		self.failed_reason = ''
		self.tmp_device_exec_log = ''
		#
		self.ip = self.ip.strip()
		if not self.ip:
			self.failed_reason = f"Missing device ip: [{self.ip}]"
			self._device_exec_log(display=True, msg=f"[-] {self.failed_reason} - skipping it")
			return None
		#
		self.pinging = self._check_ping(self.ip)
		self._start_execution(self.ip)

	def _device_exec_log(self, display, msg):
		if display: print(msg)
		self.tmp_device_exec_log += msg +"\n"

	def _check_ping(self, ip):
		"""check device reachability

		Args:
			ip (str): device ip

		Returns:
			int: delay factor if device reachable,  else False
		"""    		
		try:
			self._device_exec_log(display=True, msg=f"[+] {ip} - Checking ping response")
			self.delay_factor = IP.ping_average (ip)/100 + 3
			self._device_exec_log(display=True, msg=f"[+] {ip} - Delay Factor={self.delay_factor}")
			return self.delay_factor
		except:
			self._device_exec_log(display=True, msg=f"[-] {ip} - Ping was unsuccessful")
			return False

	def _start_execution(self, ip):
		if not (self.forced_login or self.pinging): return
		if not self.pinging:
			self._device_exec_log(display=True, msg=f"[+] {ip} - Attempt login")
		dtype_result = self._get_device_type(ip)
		if not dtype_result: return
		if self.dev is None: return
		try:
			self._execute(ip)
		except:
			if self.dev.dtype != 'cisco_ios': return
			self._device_exec_log(display=True, msg=f"[-] {ip} - sleeping progress for 65 seconds due to known cisco ios bug")					
			sleep(65)
			self._execute(ip)

	def _get_device_type(self, ip):
		"""detect device type (cisco, juniper)

		Args:
			ip (str): device ip

		Returns:
			str: device type if detected, else None
		"""    		
		try:
			self.dev = DeviceType(dev_ip=ip, 
				un=self.auth['un'], 
				pw=self.auth['pw'],
			)
			self._device_exec_log(display=False, msg=self.dev.tmp_device_detection_log)
			return self.dev
		except Exception as e:			
			self.failed_reason = f"[-] [{ip}] - Device Type Detection Failed with Exception \n{e}"
			self._device_exec_log(display=True, msg=f"{'- '*40}\n{self.failed_reason}\n{'- '*40}")
			return None

	def _is_not_connected(self, c, ip):
		"""check if connection is successful

		Args:
			c (conn): connection object
			ip(str): ip address of connection

		Returns:
			conn: connection object if successful, otherwise None
		"""
		connected = True
		if STR.found(str(c), "FAILURE"): connected = None
		if c.hn == None or c.hn == 'dummy': connected = None
		return not connected

	def _execute(self, ip):
		"""login to given device(ip) using authentication parameters from uservar (u).
		if success start command captuers

		Args:
			ip (str): device ip
		"""
		self._device_exec_log(display=True, msg=f"[+] {ip} - Initializing")

		with conn(ip=ip, device=self) as c:
			if self.verify_connection(c, ip) == None: return None
			self.update_obj_properties(c)
			self.update_cmds_for_missing_captures_only(c)
			cc = self.run_cmds(c)
			self.run_facts_generation_required_commands(c, cc)
			self.run_custom_commands(c, cc)
			self.add_exec_logs(cc)
			self.write_facts_to_excel(cc)
			self.add_cmd_exec_logs(cc)

	def verify_connection(self, c, ip):
		if self._is_not_connected(c, ip):
			self.failed_reason = self.failed_reason or "Connection Failure"
			return None
		return True

	def update_obj_properties(self, c):
		self.c = c
		self.hostname = c.hn
		c.capture_path = self.capture_path
		c.dev_type = self.dev.dtype

	# -- get the missing commands list if it is to do only missing captures
	def update_cmds_for_missing_captures_only(self, c):
		if not self.missing_captures_only: return
		#
		missed_cmds = []
		if isinstance(self.cmds, dict):
			missed_cmds = self.get_missing_commands(c, set(self.cmds[self.dev.dtype]), purpose='missing')
			if missed_cmds is not None: 
				self.cmds[self.dev.dtype] = missed_cmds
		elif isinstance(self.cmds, (list, set, tuple)):
			missed_cmds = self.get_missing_commands(c, set(self.cmds), purpose='missing')
			if missed_cmds is not None: 
				self.cmds = missed_cmds
		if missed_cmds:
			self._device_exec_log(display=True, msg=f"[+] {c.hn} : INFO : Missed Cmds =  {missed_cmds}")
		elif missed_cmds is None:
			self._device_exec_log(display=True, msg=f"[+] {c.hn} : INFO : Cumulative file missing, new file will be generated.")
		else:
			self._device_exec_log(display=True, msg=f"[+] {c.hn} : INFO : No missing Command found in existing capture..")

	def run_cmds(self, c):
		cc = self.command_capture(c)
		self.get_max_cmd_length(c, self.cmds)
		cc.grp_cmd_capture(self.cmds)
		if self.cmds: 
			self.add_cmd_to_all_cmd_dict(self.cmds)
		return cc

	# -- for facts generation -- presence of mandary commands, and capture if not --
	def run_facts_generation_required_commands(self, c, cc):
		if not self.fg or not self.mandatory_cmds_retries: return
		#
		self._device_exec_log(display=True, msg=f"[+] {c.hn} : INFO : Starting with Mandatory commands capture (if any missing).")
		missed_cmds = self.check_facts_finder_requirements(c)
		self.retry_missed_cmds(c, cc, missed_cmds)
		self.add_cmds_to_self(missed_cmds)
		if missed_cmds: 
			self.add_cmd_to_all_cmd_dict(missed_cmds)

	# -- custom commands -- only log entries, no parser --
	def run_custom_commands(self, c, cc):
		if not self.CustomClass: return
		#
		self._device_exec_log(display=True, msg=f"[+] {c.hn} : INFO : Starting with custom commands capture.")
		CC = self.CustomClass(c.capture_path+"/"+c.hn+".log", self.dev.dtype)
		self.get_max_cmd_length(c, CC.cmds)
		cc.grp_cmd_capture(CC.cmds)
		self.add_cmds_to_self(CC.cmds)
		if CC.cmds: 
			self.add_cmd_to_all_cmd_dict(CC.cmds)

	# -- add command execution logs dataframe --
	def add_exec_logs(self, cc):
		cc.add_exec_logs()

	# -- write facts to excel --
	def write_facts_to_excel(self, cc):
		if not self.cumulative_filename: self.cumulative_filename = cc.cumulative_filename 
		if self.parsed_output: 
			self.xl_file = cc.write_facts()

	# -- add execution logs
	def add_cmd_exec_logs(self, cc):
		self.cmd_exec_logs = cc.cmd_exec_logs

	def add_cmd_to_all_cmd_dict(self, cmds):
		"""add command to all cmd dictionary

		Args:
			cmds (str, list, tuple, set, dict): commands in any format
		"""    	
		if self.dev.dtype not in self.all_cmds.keys():
			self.all_cmds[self.dev.dtype] = set()
		if isinstance(cmds, (set, list, tuple)):
			self.all_cmds[self.dev.dtype] = self.all_cmds[self.dev.dtype].union(set(cmds))
		elif isinstance(cmds, dict):
			for dt, _cmds in cmds.items():
				if dt != self.dev.dtype: continue
				self.add_cmd_to_all_cmd_dict(_cmds)
		elif isinstance(cmds, str):
			self.add_cmd_to_all_cmd_dict([cmds,])

	def add_cmds_to_self(self, cmds):
		"""add additional commands to cmds list

		Args:
			cmds (list): list of additinal or missed mandatory cmds to be captured 
		"""		
		if isinstance(self.cmds, list):
			for cmd in cmds:
				if cmd not in self.cmds:
					self.cmds.append(cmd)
		elif isinstance(self.cmds, set):
			for cmd in cmds:
				if cmd not in self.cmds:
					self.cmds.add(cmd)
		elif isinstance(self.cmds, tuple):
			for cmd in cmds:
				if cmd not in self.cmds:
					self.cmds = list(self.cmds).append(cmd)
		elif isinstance(self.cmds, dict):
			for cmd in cmds:
				if cmd not in self.cmds[self.dev.dtype]:
					self.cmds[self.dev.dtype].append(cmd)
		else:
			self._device_exec_log(display=True, msg=f"[-] {self.c.hn} : ERROR : Non standard command input {type(self.cmds)}\n{self.cmds}")

	def get_max_cmd_length(self, c, cmds):
		"""returns the length of longest command

		Args:
			c (conn): connection object
			cmds (str,iterable): commands list
		"""    		
		if isinstance(cmds, (list, set, tuple)):
			c.max_cmd_len = LST.longest_str_len(cmds)
		elif isinstance(cmds, dict):
			for dt, _cmds in cmds.items():
				if dt != self.dev.dtype: continue
				self.get_max_cmd_length(c, _cmds)
		elif isinstance(cmds, str):
			self.get_max_cmd_length(c, [cmds,])
		else:
			return


	def command_capture(self, c):
		"""start command captures on connection object

		Args:
			c (conn): connection object
		"""
		self._device_exec_log(display=True, msg=f"[+] {c.hn} : INFO : Starting Capture in `{'append' if self.append_capture else 'add'}` mode")

		cc = Captures(
			conn=c, 
			cumulative=self.cumulative,
			parsed_output=self.parsed_output,
			standard_output=self.standard_output,
			append_capture=self.append_capture,
			)
		return cc



	def missed_commands_capture(self, c, cc, missed_cmds, x=""): 
		"""recaptures missed commands

		Args:
			c (conn): connection object
			cc(Captures): Capture / Command line processing object
			missed_cmds (set): list/set of commands for which output to be recapture
			x (int, optional): iteration value
		"""		
		self._device_exec_log(display=True, msg=f"[+] {c.hn} - Retrying missed_cmds({x+1}): {missed_cmds}")
		self.get_max_cmd_length(c, missed_cmds)
		cc.grp_cmd_capture(missed_cmds)

	def is_any_ff_cmds_missed(self, c):
		"""checks and returns missed mandatory capture commands

		Args:
			c (conn): connection object

		Returns:
			set: missed mandatory commands
		"""		
		necessary_cmds = ff.get_necessary_cmds(self.dev.dtype)
		return self.get_missing_commands(c, necessary_cmds, purpose='factsgen')

	def check_facts_finder_requirements(self, c):
		"""checks and returns missed mandatory capture commands
		clone to is_any_ff_cmds_missed

		Args:
			c (conn): connection object

		Returns:
			set: missed mandatory commands
		"""		
		return self.is_any_ff_cmds_missed(c)

	def retry_missed_cmds(self, c, cc, missed_cmds):
		"""retry missed commands captures

		Args:
			c (conn): connection object instance
			cc(Captures): Capture / Command line processing object
			missed_cmds (set): missed commands

		Returns:
			None: No retuns
		"""		
		for x in range(self.mandatory_cmds_retries):
			if not missed_cmds: return None
			self.missed_commands_capture(c, cc, missed_cmds, x)
			missed_cmds = self.is_any_ff_cmds_missed(c)
		if missed_cmds:	
			self._device_exec_log(display=True, msg=f"[-] {c.hn} - Error capture all mandatory commands, try do manually..")

	def get_missing_commands(self, c, cmds, purpose):
		"""checks and returns missed capture commands

		Args:
			c (conn): connection object
			cmds (list): list of commands to check

		Returns:
			set: missed mandatory commands
		"""		
		try:
			file = c.capture_path+"/"+c.hn+".log"
			with open(file, 'r') as f:
				log_lines = f.readlines()
		except:
			if purpose == 'missing':
				self._device_exec_log(display=True, msg=f'[-] {c.hn} : Error: File not found {c.capture_path+"/"+c.hn+".log"}: Cumulative capture file required ')
				return []
			if purpose == 'factsgen':
				return cmds
		captured_cmds = set()
		for log_line in log_lines:
			if log_line[1:].startswith(cmd_line_pfx):
				captured_cmd = ff.get_absolute_command(self.dev.dtype, log_line.split(cmd_line_pfx)[-1])
				captured_cmds.add(captured_cmd.strip())
		missed_cmds = cmds.difference(captured_cmds)
		return list(missed_cmds)

