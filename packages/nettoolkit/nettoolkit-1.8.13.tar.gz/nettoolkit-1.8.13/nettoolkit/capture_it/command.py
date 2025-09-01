# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
from nettoolkit.nettoolkit_common import STR, IO, printmsg
from .common import cmd_line_pfx


# -----------------------------------------------------------------------------
# Command Execution on a conn(connection) object, store to file
# -----------------------------------------------------------------------------

class COMMAND():
	"""CAPTURE OUTPUT FOR GIVEN COMMAND - RETURN CONTROL/OUTPUT 

	Args:
		conn (conn): connection object
		cmd (str): a command to be executed
		parsed_output(bool): Need to parse output and generate excel or not.

	Properties:
		cmd (str): command executed
		commandOP, output (str) - command output
		fname (filename): full filename with path where output stored
	"""    	

	# INITIALIZE class vars
	def __init__(self, conn, cmd, parsed_output, standard_output,
		del_old_file
		):
		"""initialize a command object

		Args:
			conn (conn): connection object
			cmd (str): a command to be executed
			standard_output(bool): write output as standard capture or capture_it format.
			parsed_output(bool): Need to parse output and generate excel or not.
		"""    		
		self.conn = conn
		self.cmd = cmd
		self.parsed_output = parsed_output
		self.standard_output = standard_output
		self.del_old_file = del_old_file    ## internal use only
		self._commandOP(conn)


	def _op_to_file(self, cumulative=False):
		"""store output of command to file, cumulative (True,False,both) to store output in a single file, individual files, both

		Args:
			cumulative (bool, optional): True,False,both. Defaults to False.

		Returns:
			str: file name where output get stored
		"""
		if cumulative is True or (isinstance(cumulative, str) and cumulative.lower() == 'both'):
			self.cumulative_filename = self.add_to_file(self.commandOP)    # add to file
			self.fname = self.cumulative_filename
			self.conn._device_conn_log(display=True, msg=f"[+] {self.conn.hn.ljust(len(self.conn.hn)+2)} : INFO : {self.cmd.ljust(self.conn.max_cmd_len+2)} >> {self.fname}")
		if cumulative is False or (isinstance(cumulative, str) and cumulative.lower() == 'both'):
			self.fname = self.send_to_file(self.commandOP)    # save to file
			self.conn._device_conn_log(display=True, msg=f"[+] {self.conn.hn.ljust(len(self.conn.hn)+2)} : INFO : {self.cmd.ljust(self.conn.max_cmd_len+2)} >> {self.fname}")
		if cumulative is None:
			pass


	# Representation of Command object
	def __repr__(self):
		return f'object: Output for \n{self.conn} \ncommand: {self.cmd}'

	# RETURNS ---> Command output
	@property
	def commandOP(self):
		'''command output'''
		return self.output

	# capture output from connection
	def _commandOP(self, conn):
		self.output = ''

		op = self.conn.net_connect.send_command(
			self.cmd, 
			read_timeout=30, 
			delay_factor=self.conn.delay_factor,
			use_textfsm=self.parsed_output,
		)

		# exclude missed ones
		if any([								
			STR.found(op,'Connection refused')
			]):                                 ### ADD More as needed ###
			self.conn._device_conn_log(display=True, msg=f"[-] {self.conn.hn} : ERROR: Connection was refused by remote host..")
			return None

		self.output = op

	# send output to textfile
	def send_to_file(self, output):
		"""send output to a text file

		Args:
			output (str): captured output

		Returns:
			str: filename where output got stored
		"""    		
		fname = STR.get_logfile_name(self.conn.capture_path, hn=self.conn.hn, cmd=self.cmd, ts=self.conn.conn_time_stamp)

		IO.to_file(filename=fname, matter=output)
		return fname

	# send output to textfile
	def add_to_file(self, output):
		"""add output to a text file

		Args:
			output (str): captured output

		Returns:
			str: filename where output got appended
		"""    		
		banner = self.banner if self.banner else ""

		cmd_header = self.get_cmd_banner()
		
		fname = STR.get_logfile_name(self.conn.capture_path, hn=self.conn.hn, cmd="", ts="")
		if self.del_old_file: delete_file_ifexist(fname)

		IO.add_to_file(filename=fname, matter=banner+cmd_header+output)
		return fname

	def get_cmd_banner(self):
		if self.standard_output:
			cmd_header = f"\n{self.conn.net_connect.find_prompt()}{self.cmd}\n"
		else:
			rem = "#" if self.conn.devtype == 'juniper_junos' else "!"
			cmd_header = f"\n{rem}{'='*80}\n{rem}{cmd_line_pfx}{self.cmd}\n{rem}{'='*80}\n\n"
		return cmd_header


def delete_file_ifexist(fname):
	"""deletes file

	Args:
		fname (str): file name with full path.
	"""    	
	try:
		os.remove(fname)
	except:
		pass
