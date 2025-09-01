# ---------------------------------------------------------------------------
# IMPORT
# ---------------------------------------------------------------------------
from dataclasses import dataclass, field

# ======================================================================================================
#  Commands Class
# ======================================================================================================
@dataclass
class Commands():
	list_of_cmds: list = field(default_factory=[])
	device: str = ''
	device_session: any = ''
	device_type: str = ''
	output_file: str = ''
	remark_char: str = ''
	standard_output:bool=True
	missing_only: bool=False
	cumulative: bool=False
	interactive_cmd_report: bool=False
	final_cmd_report: bool=False
	failed_retry_count: int = 2

	def __post_init__(self):
		self.output_dict = {}
		self.exec_logs = [] 
		self.output_file_read = ''
		self.capture_result = {}
		if self.missing_only: 
			self.read_capture_file()
		pass

	def capture(self):
		kwargs = { 
			'device': self.device, 'device_session': self.device_session, 'device_type': self.device_type,
			'output_file': self.output_file,
			'interactive_cmd_report': self.interactive_cmd_report, 'final_cmd_report': self.final_cmd_report,
			'failed_retry_count': self.failed_retry_count, 'missing_only': self.missing_only,
			'output_file_read': self.output_file_read, 'remark_char': self.remark_char,
			'standard_output': self.standard_output,

		}
		for cmd in self.list_of_cmds:
			command = Command(cmd, **kwargs)
			command.capture()
			if self.cumulative in (True, 'both'): command.append_output_to_file()       ## Writing directly to File / ( Less Memory usage )
			if self.cumulative in (False, 'both'): command.write_output_to_file()       ## cmd individual file

			# self.output_dict[cmd] = command.output               ### For Writing file at last / end ( More memory usage )
			if self.final_cmd_report:
				self.exec_logs.extend(command.exec_log)
			self.capture_result[cmd] = command.capture_result

	def read_capture_file(self):
		with open(self.output_file, 'r') as f:
			self.output_file_read = f.read()


# ======================================================================================================
#  A Command Class
# ======================================================================================================
@dataclass
class Command():
	cmd: str
	device: str
	device_session: any
	device_type: str
	output_file: str
	missing_only: bool=False
	output_file_read: str = ''
	remark_char: str=''
	standard_output:bool=True
	interactive_cmd_report: bool=False
	final_cmd_report: bool=False
	failed_retry_count: int = 2

	def __post_init__(self):
		self.output = ''
		self.exec_log = []
		if self.device_type == 'juniper': self.cmd = self.cmd + " | no-more"
		self.capture_result = 'not initiated'

	def capture(self):
		# ------------------------ DONT CAPTURE IF ALREADY PRESENT ------------------------ #		
		if self.missing_only and self.is_cmd_capture_available():
			self.log_message(f"    [+] Capture already present for {self.device} - of command: {self.cmd}, skipped")
			self.capture_result = 'Already +nt'
			return
		# ------------------------ CAPTURE ------------------------ #
		for i in range(1, self.failed_retry_count+1):		
			self.log_message(f"    [+] Retriving output for {self.device} - of command: {self.cmd}")
			try:
				cmd_op = self.device_session.get_cmd_output(self.cmd)
				self.output = self.strip_extra_lf_characters(cmd_op)
				self.capture_result = 'success'
				return
			# ------------------------ RETRY IF FAIL TILL RETRY COUNT EXCEDED ------------------------ # 
			except EOFError:
				self.capture_result = 'failed'
				if i < self.failed_retry_count:
					self.log_message(f'    [-] Error Retriving output for {self.device} - of command: {self.cmd}, retry {i+1}')

		# ------------------------ RETRY COUNT EXCEEDED ------------------------ #
		self.capture_result = 'failed'
		self.log_message(f'    [-] Error Retriving output for {self.device} - of command: {self.cmd}, skipped since exceeded retry count')


	@staticmethod
	def strip_extra_lf_characters(cmd_op):
		return "\n".join([line.rstrip() for line in cmd_op.split("\n")])

	def log_message(self, msg):
		if self.final_cmd_report: self.exec_log.append(msg)
		if self.interactive_cmd_report: print(msg)

	def append_output_to_file(self):
		s = ''
		s += self.banner_lines
		s += self.output
		with open(self.output_file, 'a') as f:
			f.write(s)

	def write_output_to_file(self):
		op_file = ".".join(self.output_file.split(".")[:-1]) + f"-{self.cmd}.txt"
		s = ''
		s += self.banner_lines
		s += self.output
		with open(op_file, 'w') as f:
			f.write(s)

	@property
	def banner_lines(self):
		# if self.standard_output:
		# 	cmd_header = f"\n{self.device_session.find_prompt()}{self.cmd}\n"
		# else:
		cmd_header = f"\n{self.double_line}\n{self.remark_char} output for command: {self.cmd}\n{self.double_line}\n"
		return cmd_header

	@property
	def double_line(self):
		return f"{self.remark_char} {'='*80}"

	def is_cmd_capture_available(self):
		cmd_line_pos = self.output_file_read.find(self.banner_lines)
		if cmd_line_pos == -1:
			return False
		len_of_banner_lines = len(self.banner_lines)
		next_banner_line_pos = self.output_file_read.find(self.double_line, cmd_line_pos+len_of_banner_lines) 
		print(cmd_line_pos + len_of_banner_lines , next_banner_line_pos)
		if cmd_line_pos + len_of_banner_lines + 3 > next_banner_line_pos:
			return False
		return True


# ======================================================================================================
if __name__ == '__main__':
	pass
# ======================================================================================================
