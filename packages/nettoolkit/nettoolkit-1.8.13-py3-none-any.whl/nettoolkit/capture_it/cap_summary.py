# --------------------------------------------
# IMPORTS
# --------------------------------------------
import pandas as pd
from collections import OrderedDict
from dataclasses import dataclass
from tabulate import tabulate
from nettoolkit.nettoolkit_db import write_to_xl
from nettoolkit.nettoolkit_common import deprycation_warning

# -----------------------------------------------------------------------------
# STATIC VAR
# -----------------------------------------------------------------------------
BANNER = '> ~~~ RAW COMMANDS CAPTURE SUMMARY (aholo2000@gmail.com) ~~~ <'

# -----------------------------------------------------------------------------
class LogSummary():
	"""class generating summary report for the commands log/raw capture
	DEPRYCATED... 
	"""	

	def __init__(self, c, 
		split_cisco_juniper=True,
		on_screen_display=False, 
		write_to=None, 
		):
		deprycation_warning("class: LogSummary")
# -----------------------------------------------------------------------------
## Not implemented ## -unused
class SummaryDisplay():

	def __init__(self, d):
		deprycation_warning("class: SummaryDisplay")

# # ==========================================================================================

@dataclass
class TableReport():
	"""class defining methods and properties to write the execution log summary report to excel

	Args:
		all_cmds (dict): 
		cmd_exec_logs_all (dict): 
		host_vs_ips (dict): 
		device_type_all (dict): 
	"""    	
	all_cmds: dict
	cmd_exec_logs_all: dict
	host_vs_ips: dict
	device_type_all: dict

	def __call__(self):
		self.split_by_device_types()
		self.get_updated_cmd_exec_log()

	def split_by_device_types(self):
		"""split the device based on its device types
		"""    		
		self.new_cmd_exec_log = {}
		for hn, dt in self.device_type_all.items():
			if not self.new_cmd_exec_log.get(dt): self.new_cmd_exec_log[dt]={}
			self.new_cmd_exec_log[dt][hn]={}

	def get_updated_cmd_exec_log(self):
		"""get the updated command execution log in DFD format to write to excel

		Args:
			transpose (bool): transpose the output in excel
		"""    		
		for dt, new_d in self.new_cmd_exec_log.items():
			for device, ip in self.host_vs_ips.items():
				if self.device_type_all[device] != dt: continue
				device_cmds = set(self.all_cmds[dt])
				dev_cmd_exist = set()
				for cmd in device_cmds:
					if not new_d.get(device): 
						new_d[device] = {}
						dev_dict = new_d[device]
					for _ in self.cmd_exec_logs_all[device]:
						if _['command'].replace("| no-more ", "") != cmd: continue
						dev_dict[cmd] = 'success' if _['raw'] else 'failure'
						dev_cmd_exist.add(cmd) 
				for cmd in device_cmds.difference(dev_cmd_exist):
					dev_dict[cmd] = ''
			self.new_cmd_exec_log[dt] = pd.DataFrame(new_d)
			if len(self.new_cmd_exec_log[dt].columns) > len(self.new_cmd_exec_log[dt]):
				self.new_cmd_exec_log[dt] = self.new_cmd_exec_log[dt].T

	def show(self, tablefmt='rounded_outline'):
		## available good formats = pretty, psql, 'rounded_outline' 
		for tab, df in self.new_cmd_exec_log.items():
			printable = tabulate(df, headers='keys', tablefmt=tablefmt)
			print(printable)

	def write_to(self, file):
		"""writes execution log DFD to provided excel file.

		Args:
			file (str): excel file name with full path
		"""    		
		write_to_xl(file, self.new_cmd_exec_log, overwrite=True, index=True)
		print(f"Info:	commands capture log summary write to {file}.. done")

