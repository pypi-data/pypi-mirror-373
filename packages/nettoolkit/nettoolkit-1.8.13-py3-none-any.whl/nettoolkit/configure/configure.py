
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import pandas as pd
from netmiko import ConnectHandler
from itertools import zip_longest
from time import sleep
import traceback
from nettoolkit.nettoolkit_common import printmsg, STR, LST, Multi_Execution, print_banner
from nettoolkit.nettoolkit_db import read_xl_all_sheet

from nettoolkit.detect import DeviceType

# -----------------------------------------------------------------------------

class ConfigEnvironmentals(Multi_Execution):
	"""Configuration Object environmental properties. Inherits Multi_Execution
	"""
	def __init__(self, auth, log_folder, config_log, exec_log, exec_display):
		self.auth = auth
		self.log_folder = log_folder
		self.config_log = config_log
		self.exec_log = exec_log
		self.exec_display = exec_display
		self.config_env = {
			'log_folder': log_folder,
			'config_log': config_log,
			'exec_log': exec_log,
			'exec_display': exec_display,
		}


# -----------------------------------------------------------------------------

class Config_common():
	"""Common Methods and properties for Configuration classes
	"""    	

	def get_device_type(self, ip, auth):
		"""detecting device type (cisco, juniper)

		Args:
			ip (str): device ip
			auth (dict): authentication dicationary with 'un', 'pw'. 'en' keys.

		Returns:
			str: device type if detected, else None
		"""    		
		try:
			dev = DeviceType(dev_ip=ip, 
				un=auth['un'], 
				pw=auth['pw'],
			)
			self.write_exec_log(ip, f"[+] {ip} - Device Type Detection successful - {dev.dtype}")
			return dev.dtype
		except Exception as e:
			self.write_exec_log(ip, f"[-] {ip} - Device Type Detection Failed with Exception \n{e}")
			return None

	def write_config_log(self, host, log):
		"""send out the configuration log to a log file 

		Args:
			host (str): host/device name
			log (str/multiline): log to be write to
		"""    		
		if self.config_log and self.log_folder:
			self.write_exec_log(host, f"[+] writing configuration application log @ {self.log_folder}/{host}-config-apply.log")
			with open(f"{self.log_folder}/{host}-config-apply.log", 'a') as f:
				f.write(log)
			self.write_exec_log(host, f"[+] writing configuration application log @ {self.log_folder}/{host}-config-apply.log\t...done")

	def write_exec_log(self, host, s, ends='\n'):
		"""writes execution log (internal)

		Args:
			host (str): host/device name
			s (str/multiline): execution log content
			ends (str, optional): End string. Defaults to enter.
		"""    		
		if self.exec_display: print(s)
		if self.exec_log and self.log_folder:
			with open(f"{self.log_folder}/{host}-exec.log", 'a') as f:
				f.write(s+ends)


	def send_configuration(self, conf_list):
		"""sends provided list of configuration to self device connection

		Args:
			conf_list (list): configuration change list

		Returns:
			bool: success/fail
		"""    		
		self.write_exec_log(self.conn.host, f"[+] applying config to {self.device_type} // {self.conn.host} // {self.ip}")
		try:
			self.op_return = self.conn.send_config_set(conf_list)
			self.write_exec_log(self.conn.host, f"[+] applying config to {self.device_type} // {self.conn.host} // {self.ip}\t...done")
			return True
		except:
			self.write_exec_log(self.conn.host, f"[-] applying config to {self.device_type} // {self.conn.host} // {self.ip}\t...Failed")
			return False

	def get_connection(self):
		"""retrive a new connection

		Returns:
			conn: connection object
		"""    		
		try:
			conn = ConnectHandler(**self.dev_var)
			self.connectionsuccess = True
			return conn
		except:
			self.write_exec_log(self.ip, f"[-] Connection Failed to establish {self.device_type} // No connection // {self.ip}", ends="\n\n")
			self.connectionsuccess = False
			return None

	def terminate_connection(self):
		"""terminate active connection
		"""    		
		try:
			self.conn.disconnect()
		except:
			pass

	def set_hostname(self):
		"""retrive hostname from current connection
		"""    		
		try:
			self.dev_var['host'] = STR.hostname(self.conn).lower()
		except:
			self.write_exec_log(self.conn.host, f"[-] Hostname Retrival failed for device {self.ip} ")
			self.dev_var['host'] = self.ip
		self.hn = self.dev_var['host']



# ----------------------------------------------------------------------------------------------------


class Configure(Config_common):
	"""Configure class to do configuration on a Cisco IOS or Juniper Junos device
	Inherits Config_common

	Args:
		ip (str): device ip address or FQDN
		auth (dict): authentication dicationary with 'un', 'pw'. 'en' keys.
		conf_list (list, optional): configuration change list. Defaults to None. Either
		conf_file (str, optional): configuration change file. Defaults to None. Or
		log_folder (str, optional): folder where logs to be stored. Defaults to None.
		config_log (bool, optional): generate configuration log. Defaults to True.
		exec_log (bool, optional): generate execution log. Defaults to True.
		exec_display (bool, optional): on screen display execution log. Defaults to True.
	"""    	

	def __init__(self, ip, auth, 
		conf_list=None, 
		conf_file=None, 
		log_folder=None,
		config_log=True,
		exec_log=True,
		exec_display=True,
		):
		self.ip = ip
		self.auth = auth
		self.conf_list = conf_list
		self.conf_file = conf_file       # prefered
		self.log_folder = log_folder
		self.config_log = config_log
		self.exec_log = exec_log
		self.exec_display = exec_display
		self._get_conf_list_from_file()

	def _get_conf_list_from_file(self):
		if self.conf_file:
			try:
				with open(self.conf_file, 'r') as f:
					conf_list = f.readlines()
					conf_list = [ _.rstrip() for _ in conf_list ]
			except:
				self.write_exec_log(self.conn.host, f"[-] Error Reading file {self.conf_file}", ends="\n\n")
				return None
			if self.conf_list and conf_list:
				_d = input(f"[-] DUAL INPUT DETECTED, conf_list as well as conf_file. configuration file will override list. Continue [Y/N]")
				if _d.upper() != 'Y': quit()
			if conf_list:
				self.conf_list = conf_list

	def apply(self):
		"""apply the configuration to active connection
		"""    		
		if not self.conf_list:
			self.write_exec_log(self.conn.host, f"[-] No configurations to apply for {self.ip} // configuration=[{self.conf_list}]")
		if isinstance(self.conf_list, str):
			self.conf_list = [self.conf_list, ]
		self.device_type = self.get_device_type(self.ip, self.auth)
		self.dev_var = {'device_type': self.device_type, 
			'ip': self.ip,
			'username': self.auth['un'],
			'password': self.auth['pw'],
			'secret': self.auth['en'] if self.auth.get('en') else self.auth['pw'],
		}
		self._start_push()

	def _start_push(self):
		if self.device_type == 'juniper_junos':  self.juniper_push()
		elif self.device_type == 'cisco_ios':  self.cisco_push()
		else: print(f"[-] Undetected device {self.ip}")

	## -------------- Juniper ------------------

	def juniper_push(self):
		"""method defining configuration push for Juniper devices 

		Returns:
			bool/None: False if unable to connect, None after connection terminate
		"""    		
		if self.conf_list[-1] != 'commit check': 
			self.conf_list.append("commit check")
		#
		self.conn = self.get_connection()
		if not self.connectionsuccess: return False
		self.set_hostname()
		#
		send_conf = self.send_configuration(self.conf_list)
		if not send_conf:
			self.write_exec_log(self.conn.host, f"[-] Termination without configuration apply for {self.device_type} // {self.conn.host} // {self.ip}", ends="\n\n")
			self.terminate_connection()
			return None
		self.write_config_log(self.conn.host, self.op_return)
		#
		check = self.juniper_verify_push_op(self.op_return)
		if not check: 
			self.write_exec_log(self.conn.host, f"[-] ERROR: Termination without configuration apply for {self.device_type} // {self.conn.host} // {self.ip}", ends="\n\n")
			self.terminate_connection()
			return None
		#
		commit_return = self.juniper_commit()
		self.juniper_verify_commit_op(commit_return)
		#
		self.terminate_connection()


	def juniper_verify_push_op(self, op):
		"""verifications on juniper configuration push output

		Args:
			op (multiline str): configuaration log output

		Returns:
			bool: success or syntex error
		"""    		
		check = False
		self.write_exec_log(self.conn.host, f"[+] checking applied configuration for {self.device_type} // {self.conn.host} // {self.ip}")
		for line in op.splitlines():
			if line.strip().startswith('syntax error'): break
			check = line == "configuration check succeeds"
			if check: break
		if check:
			self.write_exec_log(self.conn.host, f"[+] checking applied configuration for {self.device_type} // {self.conn.host} // {self.ip}\t...done" )
		else:
			self.write_exec_log(self.conn.host, f"[-] checking applied configuration for {self.device_type} // {self.conn.host} // {self.ip}\t...Failed\n.  Re-Check configuration manually before commit\nGot:\n{self.op_return}")
		return check

	def juniper_verify_commit_op(self, op):
		"""verification of commit

		Args:
			op (multiline str): configuaration log output
		"""    		
		self.write_exec_log(self.conn.host, f"[+] verifying configuration commit to {self.device_type} // {self.conn.host} // {self.ip}")
		check = 0
		for line in op.splitlines():
			if (line.strip().startswith("configuration check succeeds") 
				or line.strip().startswith("commit complete")
				):
				check+=1 
		#
		if check == 2:
			self.write_exec_log(self.conn.host, f"[+] verifying configuration commit to {self.device_type} // {self.conn.host} // {self.ip}\t...done")
		else:
			self.write_exec_log(self.conn.host, f"[-] verifying configuration commit to {self.device_type} // {self.conn.host} // {self.ip}\t...Failed\nGot\n{op}")

	def juniper_commit(self):
		"""commiting the pushed juniper configurations.

		Returns:
			bool: success or fail
		"""    		
		self.write_exec_log(self.conn.host, f"[+] commiting configurations to {self.device_type} // {self.conn.host} // {self.ip}")
		try:
			commit_return = self.conn.commit()
			self.write_exec_log(self.conn.host, f"[+] commiting configurations to {self.device_type} // {self.conn.host} // {self.ip}\t...done")
			return commit_return
		except:
			self.write_exec_log(self.conn.host, f"[-] commiting configurations to {self.device_type} // {self.conn.host} // {self.ip}\t...failed\nGot\n{commit_return}")
			return False

	## -------------- Cisco ------------------

	def cisco_enable(self):
		"""method to enable device mode
		"""    		
		if any( [
			self.device_type == 'cisco_ios'
			] ):
			for tries in range(3):
				try:
					if self.conn.check_enable_mode():
						break
					self.conn.enable(cmd="enable")
					break
				except:
					self.write_exec_log(self.hn, f"[-] {self.hn} - enable failed on attemp {tries}")
					continue

	def cisco_push(self):
		"""method defining configuration push for Cisco devices 

		Returns:
			bool/None: False if unable to connect, None after connection terminate
		"""    		
		self.conn = self.get_connection()
		if not self.connectionsuccess: return False
		self.set_hostname()
		self.cisco_enable()
		#
		send_conf = self.send_configuration(self.conf_list)
		if not send_conf:
			self.write_exec_log(self.conn.host, f"[-] Termination without configuration apply for {self.device_type} // {self.conn.host} // {self.ip}", ends="\n\n")
			self.terminate_connection()
			return None
		#
		self.write_config_log(self.conn.host, self.op_return)
		#
		error = self.cisco_verify_push_op(self.op_return)
		if error: 
			self.write_exec_log(self.conn.host, f"[-] ERROR: Termination without configuration apply for {self.device_type} // {self.conn.host} // {self.ip}", ends="\n\n")
			self.terminate_connection()
			return None
		#
		_return = self.cisco_commit()
		self.terminate_connection()


	def cisco_verify_push_op(self, op):
		"""verifications on cisco configuration push output

		Args:
			op (multiline str): configuaration log output

		Returns:
			bool: success or syntex error
		"""    		
		error = False
		self.write_exec_log(self.conn.host, f"[+] checking applied configuration for {self.device_type} // {self.conn.host} // {self.ip}" )
		for line in op.splitlines():
			error = line.strip().startswith("^")
			if error: break
		#
		if error:
			self.write_exec_log(self.conn.host, f"[-] checking applied configuration for {self.device_type} // {self.conn.host} // {self.ip}\t...Failed\n.  Re-Check configuration manually and reapply\nGot:\n{self.op_return}")
		else:
			self.write_exec_log(self.conn.host, f"[+] checking applied configuration for {self.device_type} // {self.conn.host} // {self.ip}\t...done")
		return error


	# save config
	def cisco_commit(self):
		"""write mem on cisco device

		Returns:
			bool: success or fail
		"""    		
		self.write_exec_log(self.conn.host, f"[+] saving configurations for {self.device_type} // {self.conn.host} // {self.ip}")
		try:
			_return = self.conn.save_config()
			self.write_exec_log(self.conn.host, f"[+] saving configurations for {self.device_type} // {self.conn.host} // {self.ip}\t...done")
			return _return
		except:
			self.write_exec_log(self.conn.host, f"[+] saving configurations for {self.device_type} // {self.conn.host} // {self.ip}\t...failed\nGot\n{_return}")
			return False

# ----------------------------------------------------------------------------------------------------

class GroupsConfigure(Multi_Execution):
	"""Configure class to do configuration on a multiple group of devices at a time.
	Inherits Multi_Execution

	Args:
		auth (dict): authentication dicationary with 'un', 'pw'. 'en' keys.
		devices_config_dict (dict, optional): {device:[list of config], } . Defaults to {}.
		config_by_order (bool, optional): if True follows execution in provided order_list entries. Defaults to True.
		order_list (list, optional): order list in which execution to be done. Defaults to [].
		dev_apply_at_dict (dict, optional): time to apply config at (under implementation). Defaults to {}.
		log_folder (str, optional): folder where logs to be stored. Defaults to None.
		config_log (bool, optional): generate configuration log. Defaults to True.
		exec_log (bool, optional): generate execution log. Defaults to True.
		exec_display (bool, optional): on screen display execution log. Defaults to True.
		configure (bool, optional): configure or it is for test only. Defaults to False.
	"""    	

	def __init__(self, auth,
		devices_config_dict={},
		config_by_order=True,
		order_list=[],
		dev_apply_at_dict={},
		log_folder=None,
		config_log=True,
		exec_log=True,
		exec_display=True,
		configure=False,
		):
		self.auth = auth
		self.devices_config_dict = devices_config_dict
		self.order_list = order_list
		self.dev_apply_at_dict = dev_apply_at_dict
		self.config_by_order = config_by_order
		self.config_env = {
			'log_folder': log_folder,
			'config_log': config_log,
			'exec_log': exec_log,
			'exec_display': exec_display,
		}
		self.configure = configure

	@printmsg(pre=f'{"-"*40}\n[+] INFO: A Group Configuration, Called...', post=f'{"-"*43}' )
	def __call__(self):
		self._verify_inputs()
		if self.config_by_order: self.configure_by_orderlist()

	@printmsg(pre='[+] INFO: Verifying inputs...',)
	def _verify_inputs(self):
		self._get_dev_conf_dict_ip_list()
		self._get_order_list()
		self.remove_empty_config_lines()

	@printmsg(pre='[+] INFO: configuring devices in order by order_list...',
			 post='[+] INFO: configuration of this order_list completed...' )
	def configure_by_orderlist(self):
		"""configure devices as per sequence provided in order_list
		"""    		
		for i, order in enumerate(self.order_list):
			if isinstance(order, (list, set, tuple)):
				self.items = order
				self.start()
			elif isinstance(order, str):
				self.execute(order)

	def execute(self, ip):
		"""executor

		Args:
			ip (str): device ip or FQDN
		"""    		
		conf_list = self.devices_config_dict[ip]['cmds_list']
		print(f"[+] \t\tStarting Configuration on: {ip}")
		if self.configure:
			CFG = Configure(ip, self.auth, 
				conf_list=conf_list,
				**self.config_env
			)
			CFG.apply()
		else:
			print(f"[-] \t\tConfiguration skipped as `configure` parameter is set to `{self.configure}`",
				 ", change it True in order to start configure process.")


	def _get_dev_conf_dict_ip_list(self):
		for ip, value in self.devices_config_dict.items():
			if not isinstance(value, dict):
				raise Exception(f"[-] ERROR: Incorrect input: configuration parameters in devices_config_dict",
					f"Expected `dict` got {type(value)} for {ip}")
			if 'cmds_list' in value and 'cmd_file' in value:
				print(f"[-] WARNING: Dual configuration input detected for ip {ip}"
					'file input will be prefered and considered')
			if 'cmd_file' in value:
				if not isinstance(value['cmd_file'], str):
					raise Exception(f"[-] CRITICAL: Incorrect input: command file name for ip {ip}: {value['cmd_file']}")
				try:
					with open(value['cmd_file'], 'r') as f:
						value['cmds_list'] = f.readlines()
						value['cmds_list'] = [ _.rstrip() for _ in value['cmds_list'] ]
						del(value['cmd_file'])
					continue
				except Exception as e:
					print(f"[-] CRITICAL: Error Occured for ip {ip}: {e}")
					quit()
			if 'cmds_list' in value:
				for _ in value['cmds_list']:
					if isinstance(_, str): continue
					print(f"[-] CRITICAL: Invalid input: command detected for ip {ip},{_}, Expected `str`. got {type(_)} ")
					quit()
				continue
			print(f"[-] WARNING: No configuration input detected for ip {ip}: {value}. This device will be skipped")
			value['skip'] = True

	def _get_order_list(self):
		if not self.order_list:
			self.order_list = [{ip for ip, value in self.devices_config_dict.items() if not value.get('skip')},]
			print(f"[+] INFO: No order_list provided, cretated one \n{self.order_list}")
			return None
		if not isinstance(self.order_list, (list, tuple)):
			raise Exception(f"[-] CRITICAL: Incorrect input: order_list. expected (tuple/list), got {type(self.order_list)}")
		self._cd_to_ol()
		self._ol_to_cd()

	def _cd_to_ol(self):
		flatten_ol = set(LST.flatten(self.order_list))
		missing_ones = tuple([ip for ip, value in self.devices_config_dict.items() if not value.get('skip')  and ip not in flatten_ol])
		print(f"[+] WARNING: Device(s) missing in order list [{missing_ones}] were appened.")
		self.order_list.append(missing_ones)
		self.flatten_ol = flatten_ol.union(set(missing_ones))
		if missing_ones:
			print(f"[+] \tINFO: updated order_list={self.order_list}")

	def _ol_to_cd(self):
		removed = False
		for ol_item in self.flatten_ol:
			if ol_item not in self.devices_config_dict:
				self.remove_order_list_item(ol_item, self.order_list)
				removed = True
		if removed:
			self.order_list = LST.remove_empty_members(self.order_list)
			print(f"[+] INFO: updated order_list={self.order_list}")

	def remove_empty_config_lines(self):
		"""sanitizer: removes empty lines from configuration
		"""    		
		for ip, value in self.devices_config_dict.items():
			value['cmds_list'] = LST.remove_empty_members(value['cmds_list'])

	def remove_order_list_item(self, item, lst):
		"""sanitizer: Remove device from configuration sequence where no configuration changes provided.

		Args:
			item (str): device ip or FQDN
			lst (list): configuration change list
		"""    		
		for _ in lst:
			if isinstance(_, str):
				if _ == item:
					lst.remove(_)
					print(f"[+] WARNING: Addititional device `{_}`found in ordered list, which is missing in devices_config_dict.",
						"Removed from order_list ")
			elif isinstance(_, (set, tuple, list)):
				self.remove_order_list_item(item, _)



# ----------------------------------------------------------------------------------------------------

class ConfigureByExcel(ConfigEnvironmentals):
	"""class to do configuration based on configuration changes provided in excel.
	All listed devices in a single Excel tab will be executed at once (simultaneously).
	Multiple Excel tabs/files can be provided to execute those in sequence. 

	Inherits ConfigEnvironmentals

	Args:
		auth (dict): authentication dicationary with 'un', 'pw'. 'en' keys.
		files (list, optional): list of excel files, will be executed in provided sequence. Defaults to [].
		tab_sort_order (list, optional): Excel tabs execution order. Defaults to []. ( options: privide in list manually, `ascending`, `reversed`)
		log_folder (str, optional): folder where logs to be stored. Defaults to None.
		config_log (bool, optional): generate configuration log. Defaults to True.
		exec_log (bool, optional): generate execution log. Defaults to True.
		exec_display (bool, optional): on screen display execution log. Defaults to True.
		configure (bool, optional): configure or it is for test only. Defaults to False.
		sleep_time_between_group (int, optional): sleep time between execution of two groups of executions. Defaults to 0.
	"""    	

	def __init__(self, auth,
		files=[],
		tab_sort_order=[],
		log_folder=None,
		config_log=True,
		exec_log=True,
		exec_display=True,
		configure=False,
		sleep_time_between_group=0,
		):
		super().__init__(auth, log_folder, config_log, exec_log, exec_display)
		self.files = files
		self.tab_sort_order = tab_sort_order
		self.configure = configure
		self.sleep_time_between_group = sleep_time_between_group
		if not isinstance(files, list):
			print(f"[-] Invalid argument `files`: should be of `list` type, got `{type(files)}`")
			quit()

	def __call__(self):
		print_banner("Configure", 'red')
		self._load_dfs()
		self._define_sort_order()
		self.cmds_groups = self._get_cmds_ordered_group()
		self.run()

	@printmsg(pre='[+] INFO: \tReading Excel file and Loading tabs...', pre_ends="\t", post='Done...' )
	def _load_dfs(self):
		self.ordered_configs_df_dict_list = []
		if isinstance(self.files, list):
			for file in self.files:
				self.ordered_configs_df_dict_list.append(read_xl_all_sheet(file))

	@printmsg(pre='[+] INFO: \tDefining sort order...', pre_ends="\t", post='Done...' )
	def _define_sort_order(self):
		if self.tab_sort_order in ('ascending', 'ordered', 'alphabetical', []):
			self._set_sort_order('ascending')
		elif self.tab_sort_order in ('reversed', 'descending'):
			self._set_sort_order('descending')
		else:
			self._verify_sort_orders()

	def _set_sort_order(self, how):
		self.tab_sort_order = [
			sorted(dfd.keys()) if how == 'ascending' else list(reversed(sorted(dfd.keys())))
			for dfd in self.ordered_configs_df_dict_list 
		]

	def _verify_sort_orders(self):
		for tso, dfd in zip_longest(self.tab_sort_order, self.ordered_configs_df_dict_list):
			if tso is None or dfd is None:
				print("[-] CRITICAL: Length of Order sequences v/s excel files count mismatch, both should be with same length")
				quit()
			#
			if set(tso) == set(dfd.keys()): continue
			print(f"[-] CRITICAL: Mismatch Sheet Names with provided order, please check")
			print(f"\tSort Order = {tso}")
			print(f"\tSheets available = {dfd.keys()}")
			quit()

	@printmsg(pre='[+] INFO: \tDefining commands groups...', pre_ends="\t", post="Done...")
	def _get_cmds_ordered_group(self):
		cmds_groups = []
		for tso, dfd in zip(self.tab_sort_order, self.ordered_configs_df_dict_list):
			for tab in tso:
				cmds_group = {}
				df = dfd[tab]
				for ip in df.columns:
					cmds_group[ip] = {'cmds_list': list(df[ip])} 
				cmds_groups.append(cmds_group)
		return cmds_groups

	@printmsg(pre='[+] INFO: START: Configuing devices',
			 post='[+] INFO: END  : Configuing devices')
	def run(self):
		"""starts configuration of devices
		"""
		tso_list = LST.flatten(self.tab_sort_order)
		for i, cg in enumerate(self.cmds_groups):
			if not self.get_concurrance(i, cg, tso_list): continue
			GC = GroupsConfigure(self.auth,
				devices_config_dict = cg, 
				configure=self.configure,
				**self.config_env
			)
			GC()
			if self.sleep_time_between_group:
				sleep(self.sleep_time_between_group)

	@staticmethod
	def get_concurrance(i, cg, tso_list):
		user_concern = input(f"[+] Configuration on group of devices GROUP{i+1}: [{tso_list[i]}] :\n ({set(cg.keys())}) ready to process. \nWant to continue [y/n]")
		if user_concern.lower() == 'y':  return True
		print(f"[-] Configuration on group of devices GROUP{i+1}: [{tso_list[i]}] : Not confirmed, Aborted !!!")
		return False

