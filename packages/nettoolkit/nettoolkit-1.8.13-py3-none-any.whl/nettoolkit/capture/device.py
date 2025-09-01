
# ---------------------------------------------------------------------------
# IMPORT
# ---------------------------------------------------------------------------
from nettoolkit.nettoolkit_common import STR
from dataclasses import dataclass, field
from nettoolkit.capture.exceptions import Report_Bug_cisco_CSCsq51052
from nettoolkit.capture.commands import Commands

# ======================================================================================================
#  Device Class
# ======================================================================================================
@dataclass
class Device():
	jump_host: any
	device: str
	device_username: str
	device_password: str = ''
	output_path: str = ''
	cumulative: bool=False
	interactive_cmd_report: bool=False
	final_cmd_report: bool=False
	failed_retry_count: int=2
	append:bool=False
	missing_only:bool=False
	standard_output:bool=True
	cmds_list_dict: dict = field(default_factory={})

	device_types = {
		'cisco': ('cisco', 'ios'),
		'juniper': ('juniper', 'junos'),
		'arista': ('arista', 'eos'),
	}
	remark_char_dict = {
		'cisco':   "!",
		'juniper': "#",
		'arista':  "!",
	} 

	# context load
	def __enter__(self):
		self.create_output_file()
		self.create_device_session()
		self._set_device_type()
		return self      # ip connection object

	# cotext end
	def __exit__(self, exc_type, exc_value, tb):
		try:
			self.device_session.close()
		except:
			pass
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_value, tb)

	# representation of connection
	def __repr__(self):
		return "[TBD]"

	def init_var(self):
		if self.missing_only: self.append = True

	def pre_checks_and_sets(self):
		if self.is_valid_device_type():
			self._set_remark_character()
			self._set_list_of_commands()
			return True
		return False

	def create_output_file(self):
		self.output_file = f"{self.output_path}/{self.device}.txt"
		if self.append:
			try:
				self.current_output_list = []
				self.current_output_list = self._read_input_file()
			except FileNotFoundError:
				self._create_output_file()
		else:
			self._create_output_file()

	def _create_output_file(self):
		if self.cumulative not in (True, 'both'): return
		with open(self.output_file, 'w') as f:
			f.write('')


	# ssh session :  server to device
	def create_device_session(self, attempt=0):
		connect = "re-connecting" if attempt > 0 else "connecting"  
		print(f"  [+] {connect} device {self.device} using username {self.device_username}")
		try:
			self.device_session = None
			self.device_session = self.jump_host.get_remote_session(
				self.device, 
				username=self.device_username, password=self.device_password,
			)
			print(f"  [+] connection established for {self.device}")
			return None
		except Exception as e:
			if attempt == 0:
				key_erased = self._erase_knownhost_key()
				if key_erased:  return self.create_device_session(attempt=1)
			if str(e).find("Incompatible version (2.99 instead of 2.0)") > 1:
				Report_Bug_cisco_CSCsq51052(self.device)
			return False

	def _erase_knownhost_key(self):
		return self.jump_host.erase_hostkey(self.device)

	def is_valid_session(self):
		if self.device_session: return True
		print(f"  [-] Command Execution did not happen for device {self.device}\n  [-] /// Incomplete device {self.device} ///")
		return False

	def is_valid_device_type(self):
		return self.device_type

	def _set_device_type(self):
		self.device_type = None
		if not self.is_valid_session(): return None
		cmd = 'show version'
		for i in range(1, 25):
			try:
				cmd = 'show version | no-more' if cmd == 'show version' else 'show version'
				cmd_op = self.device_session.get_cmd_output(cmd).lower()
				for dt, tpl in self.device_types.items():
					if STR.find_any(cmd_op, tpl):
						print(f"  [+] Device Type [{dt}] detected for device [{self.device}]")
						self.device_type = dt
						return dt
			except EOFError:
				pass
		print(f"  [-] Device Type not detected for device [{self.device}]")
		return None

	def _set_list_of_commands(self):
		self.list_of_cmds = self.cmds_list_dict[self.device_type]
		self.filter_captured_commands()

	def _set_remark_character(self):
		self.remark_char = self.remark_char_dict[self.device_type]

	def capture(self):
		if self.pre_checks_and_sets():
			kwargs = {'list_of_cmds':self.list_of_cmds, 
				'device': self.device, 'device_session': self.device_session, 'device_type': self.device_type,
				'output_file': self.output_file, 'remark_char': self.remark_char,
				'interactive_cmd_report': self.interactive_cmd_report, 'final_cmd_report': self.final_cmd_report,
				'failed_retry_count': self.failed_retry_count, 'missing_only': self.missing_only,
				'cumulative': self.cumulative, 'standard_output': self.standard_output,
			}
			self.commands = Commands( **kwargs )
			self.commands.capture()

	# save outputs  /// NIU /// ALL AT LAST /// more memory usage ///
	def write_output(self):
		print(f"    [+] Writing outputs for device {self.device} to file")
		s = ''
		for cmd, output in self.commands.output_dict.items():
			s += f"\n{self.remark_char} {'='*80}\n{self.remark_char} output for command: {cmd}\n{self.remark_char} {'='*80}\n"
			s += output
		with open(self.output_file, 'w') as f:
			f.write(s)

	def filter_captured_commands(self):
		if not self.missing_only: return
		# current_output_list = self._read_input_file()
		if self.current_output_list is None: return
		self.list_of_cmds = [cmd for cmd in self.list_of_cmds if not self.is_cmd_capture_available(cmd)]

	def _read_input_file(self):
		try:
			with open(self.output_file, 'r') as f:
				return f.readlines()
		except:
			return None

	def is_cmd_capture_available(self, cmd):
		for line in self.current_output_list:
			if line.startswith(f"{self.remark_char} output for command: {cmd}"):
				return True
		return False


# ======================================================================================================
if __name__ == '__main__':
	pass
# ======================================================================================================
