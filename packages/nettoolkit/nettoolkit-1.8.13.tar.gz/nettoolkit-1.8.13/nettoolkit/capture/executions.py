# ---------------------------------------------------------------------------
# IMPORT
# ---------------------------------------------------------------------------
from nettoolkit.nettoolkit_common import Multi_Execution
from tabulate import tabulate
import pandas as pd
from dataclasses import dataclass, field
from nettoolkit.capture.validations import Validate
from nettoolkit.capture.jump_server import JumpServer
from nettoolkit.capture.device import Device

# ---------------------------------------------------------------------------
# Global Var
# ---------------------------------------------------------------------------

# ======================================================================================================
#  Capture Class
# ======================================================================================================
@dataclass
class Captures_via_Jump_Server(Multi_Execution, Validate):
	server: str = '' 
	server_login_username: str = ''
	server_private_key_file: str = field(default=None)
	server_login_password: str = field(default=None)
	devices: list = field(default_factory=[])
	device_username: str = ''
	device_password: str = ''
	cmds_list_dict: dict = field(default_factory={})
	output_path: str='.'

	def __post_init__(self):
		super().__init__(self.devices)
		self.failed_retry_count = 2
		self.interactive_cmd_report = False
		self.final_cmd_report = True
		self.missing_only = False
		self.append = False
		self.capture_result = {}
		self.type_based_capture_result = {}
		self.max_connections = 100
		self.cumulative = True
		self.tablefmt = "pretty"
		self.standard_output = True


	def __call__(self):
		self.validate_inputs()
		self.jump_host = JumpServer(
			server=self.server,
			server_login_username=self.server_login_username,
			server_private_key_file=self.server_private_key_file,
			server_login_password=self.server_login_password
		)
		# self.open_server_session()
		self.start()
		print(f"[+] Finish all!!")

	def validate_inputs(self):
		self.input_server_str()
		self.input_server_login_username_str()
		self.input_devices_iterable()
		self.input_cmds_list_dict_dict()
		self.input_device_username_str()
		self.input_interactive_cmd_report_bool()
		self.input_final_cmd_report_bool()
		self.input_append_bool()
		self.input_missing_only_bool()
		self.input_cumulative_bool()
		self.input_max_connections_int()
		self.input_tablefmt_str()

	def execute(self, device):
		
		with Device(jump_host=self.jump_host,
					device=device,
					device_username=self.device_username,
					device_password=self.device_password,
					output_path=self.output_path,
					cumulative=self.cumulative,
					interactive_cmd_report=self.interactive_cmd_report,
					final_cmd_report=self.final_cmd_report,
					failed_retry_count=self.failed_retry_count,
					append=self.append,
					missing_only=self.missing_only,
					cmds_list_dict=self.cmds_list_dict,
					standard_output=self.standard_output,
			) as D:
			D.capture()
			self.update_reporting_dict(device, D)
			if self.final_cmd_report:
				print(f"  [+] Command Execution Log for device {device}\n{D.cmd_exec_logs}\n  [+] completed with device: {device}")

	def update_reporting_dict(self, device, D):
			### --- REPORTING DICTIONARY UPDATE --- ###
			self.capture_result[device] = D.commands.capture_result
			if not self.type_based_capture_result.get(D.device_type):
				self.type_based_capture_result[D.device_type] = {}
			self.type_based_capture_result[D.device_type].update({device: self.capture_result[device]})

	def print_report(self, tablefmt=None):
		if not tablefmt: tablefmt = self.tablefmt
		for device_type, cmd_results_dict in self.type_based_capture_result.items():
			df = pd.DataFrame(cmd_results_dict).fillna("")
			if len(df.columns) > len(df): df = df.T
			printable = tabulate(df, headers='keys', tablefmt=tablefmt)
			print(printable)

# ======================================================================================================

def capture_by_jump_server_login(
		# // Sever Parameters // #
		server, server_login_username, 
		server_private_key_file = None,
		server_login_password = None,

		# // Device Parameters // #
		devices=[], #device_username='', device_password='',
		devices_auth={'un':'', 'pw': '', 'en': ''},

		# // Commands dictionary // #
		cmds_list_dict={},

		output_path=".",

		# // Options // #
		append = False,
		missing_only = False,
		cumulative = True,
		max_connections = 100,
		tablefmt = "rounded_outline",
		failed_retry_count = 2,
		interactive_cmd_report = True,
		final_cmd_report = False,
		standard_output = True,
	):

	CJ = Captures_via_Jump_Server(
		# // Sever Parameters // #
		server=server, 
		server_login_username=server_login_username, 
		server_private_key_file=server_private_key_file, 
		server_login_password=server_login_password,

		# // Device Parameters // #
		devices=devices,
		device_username=devices_auth['un'], 
		device_password=devices_auth['pw'], 
		cmds_list_dict=cmds_list_dict,
		output_path=output_path,
	)
	CJ.interactive_cmd_report = interactive_cmd_report
	CJ.final_cmd_report = final_cmd_report
	CJ.missing_only = missing_only
	CJ.append = append or missing_only
	CJ.cumulative = cumulative
	CJ.max_connections = max_connections
	CJ.failed_retry_count = failed_retry_count
	CJ.tablefmt = tablefmt
	CJ.standard_output = standard_output

	## custom class 
	# CJ.CustomClass = XXXXXX  ## // TBD // ##

	CJ()
	CJ.print_report()



# ======================================================================================================
if __name__ == '__main__':
	pass
# ======================================================================================================
