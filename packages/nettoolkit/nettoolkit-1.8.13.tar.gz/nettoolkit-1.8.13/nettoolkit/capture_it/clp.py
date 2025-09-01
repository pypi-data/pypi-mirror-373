# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import pandas as pd
from .command import COMMAND

# -----------------------------------------------------------------------------
# Execution of Show Commands on a single device. 
# -----------------------------------------------------------------------------

class CLP():
	"""parent class for Command processing

	Args:
		conn (conn): connection object
		parsed_output(bool): Need to parse output and generate excel or not.
	"""    	
	def __init__(self, conn, parsed_output):
		"""Initialize object

		Args:
			conn (conn): connection object
			parsed_output(bool): Need to parse output and generate excel or not.
		"""   
		self.conn = conn
		self.parsed_output = parsed_output                                                
		self.cumulative_filename = None
		self.parsed_cmd_df = {}
		self.cmd_exec_logs = []
		self.hn = self.conn.hn
		self.ip = self.conn.devvar['ip']
		self.configure(False)						# fixed disable as now

	def configure(self, config_mode=False):
		"""set configuration mode

		Args:
			config_mode (bool, optional): enable/disable config commands. Defaults to False.
		"""    		
		self._configure = config_mode

	def check_config_authorization(self, cmd):
		"""check if given command is allowed or not on this device.

		Args:
			cmd (str): command to be executed

		Returns:
			bool: True/False
		"""    		
		if not self._configure and 'config' == cmd.lstrip()[:6].lower():
			self.conn._device_conn_log(display=True, msg=f"[-] {self.hn} : CRIT : error entering config mode, Mode disabled, Exiting")
			return False
		return True

	def cmd_capture(self, cmd, cumulative=False, banner=False, del_old_file=False):
		"""start command capture for given command

		Args:
			cmd (str): command to be executed
			cumulative (bool, optional): True/False/both. Defaults to False.
			banner (bool, optional): set a banner property to object if given. Defaults to False.

		Returns:
			[type]: [description]
		"""    	
		self.cmd_exec_logs.append({'command':cmd})
		cmdObj = self._cmd_capture_raw(cmd, cumulative, banner, del_old_file)
		if cmdObj is not None and self.parsed_output:
			self._cmd_capture_parsed(cmd, cumulative, banner)
		return cmdObj

	# Raw Command Capture
	def _cmd_capture_raw(self, cmd, cumulative=False, banner=False, del_old_file=False):
		try:
			cmdObj = COMMAND(conn=self.conn, cmd=cmd, parsed_output=False, standard_output=self.standard_output,
				del_old_file=del_old_file)
		except:
			self.conn._device_conn_log(display=True, msg=f"[-] {self.hn} : ERROR: error executing command {cmd}")
			self.cmd_exec_logs[-1]['raw'] = False
			return None
		try:
			cmdObj.banner = banner		
			cmdObj._op_to_file(cumulative=cumulative)
			self.cmd_exec_logs[-1]['raw'] = True
			if cumulative: self.cumulative_filename = cmdObj.cumulative_filename
			return cmdObj
		except:
			self.conn._device_conn_log(display=True, msg=f"[-] {self.hn} : ERROR: error writing output of command {cmd}  <<<<<< !!!!!!",)
			self.cmd_exec_logs[-1]['raw'] = False
			return False

	# Parsed Command Capture
	def _cmd_capture_parsed(self, cmd, cumulative=False, banner=False):
		try:
			cmdObj_parsed = COMMAND(conn=self.conn, cmd=cmd, parsed_output=True, standard_output=self.standard_output)
		except:
			self.conn._device_conn_log(display=True, msg=f"[-] {self.hn} : ERROR: error parsing command - {cmd}")
			self.cmd_exec_logs[-1]['parsed'] = False
			return None
		try:
			self.parsed_cmd_df[cmd] = pd.DataFrame(cmdObj_parsed.output)
			self.cmd_exec_logs[-1]['parsed'] = True
		except:
			self.conn._device_conn_log(display=True, 
					msg=f"[-] {self.hn} : INFO : Ntc-template parser unavailable for the output of command {cmd}, "
								f"data facts will not be available for this command")
			self.cmd_exec_logs[-1]['parsed'] = False
			return False


