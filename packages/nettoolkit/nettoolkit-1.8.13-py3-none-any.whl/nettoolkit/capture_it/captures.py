# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import pandas as pd
from nettoolkit.nettoolkit_db import append_to_xl
	
from .common import juniper_add_no_more
from .clp import CLP

# -----------------------------------------------------------------------------
# Captures Class
# -----------------------------------------------------------------------------
class Captures(CLP):
	"""Capture output 

	Args:
		dtype (str): device type
		conn (conn): connection object
		cmds (dict, set, list, tuple): set of commands or commands dictionary 
		cumulative (bool, optional): True/False/both. Defaults to False.
		parsed_output(bool): Need to parse output and generate excel or not.

	Inherits:
		CLP (class): Command Line Processing class

	"""    	

	def __init__(self, 
		conn, 
		cumulative=False, 
		parsed_output=False,
		standard_output=False,
		append_capture=False,
		):
		"""Initiate captures

		Args:
			conn (conn): connection object
			path (str): path to store the captured output
			visual_progress (int): scale 0 to 10. 0 being no output, 10 all.
			logger(list): device logging messages list
			cumulative (bool, optional): True/False/both. Defaults to False.
			parsed_output(bool): Need to parse output and generate excel or not.
			standard_output(bool): Output  in standard format or capture it format.
			append_capture(bool): Appends commands output to an existing capture file, instead of creating a new.
		"""    		
		# self.logger_list = logger_list
		super().__init__(conn, parsed_output)    # , visual_progress, logger_list)
		self.op = ''
		self.cumulative = cumulative
		self.standard_output = standard_output
		self.cumulative_filename = None
		self.del_old_file = not append_capture


	def grp_cmd_capture(self, cmds):
		"""grep the command captures for each commands	
		Unauthorized command will halt execution.

		Args:
			cmds (set, list, tuple): set of commands

		Returns:
			None: None
		"""    		
		banner = self.conn.banner
		#
		if isinstance(cmds, dict):
			commands = cmds[self.conn.dev_type] 
		if isinstance(cmds, (set, list, tuple)):
			commands = cmds 
		#
		for cmd  in commands:
			if not self.check_config_authorization(cmd): 
				self.conn._device_conn_log(display=True, msg=f"[-] CRIT : UnAuthorizedCommandDetected-{cmd}-EXECUTIONHALTED")
				return None

			# if juniper update no-more if unavailable.
			if self.conn.dev_type == 'juniper_junos': 
				cmd = juniper_add_no_more(cmd)
			#
			cc = self.cmd_capture(cmd, self.cumulative, banner, self.del_old_file)
			self.del_old_file = False
			try:
				output = cc.output
			except:
				output = f"[-] : ERROR: Error executing command {cmd}"
			cmd_line = self.hn + ">" + cmd + "\n"
			self.op += cmd_line + "\n" + output + "\n\n"
			banner = ""


	def add_exec_logs(self):
		"""adds commands execution `logs` tab to DataFrame
		"""		
		# self.logger_list.append(msg)                                 ## Removed
		self.parsed_cmd_df['logs'] = pd.DataFrame(self.cmd_exec_logs)

	def write_facts(self):
		"""writes commands facts in to excel tab
		"""
		try:
			xl_file = self.conn.capture_path + "/" + self.conn.hn + ".xlsx"
			append_to_xl(xl_file, self.parsed_cmd_df, overwrite=True)
			self.conn._device_conn_log(display=True, msg=f"[+] {self.hn} : INFO :writing facts to excel: {xl_file}...Success!")
		except:
			self.conn._device_conn_log(display=True, msg=f"[-] {self.hn} : ERROR: writing facts to excel: {xl_file}...failed!")

		return xl_file

