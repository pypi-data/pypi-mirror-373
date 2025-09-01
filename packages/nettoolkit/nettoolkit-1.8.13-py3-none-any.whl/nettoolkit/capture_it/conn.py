# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from netmiko import ConnectHandler
import traceback
from nettoolkit.nettoolkit_common import STR, LOG

from nettoolkit.detect import DeviceType

# -----------------------------------------------------------------------------

BAD_CONNECTION_MSG = ': BAD CONNECTION DETECTED, TEARED DOWN'
cisco_banner ="""
! ---------------------------------------------------------------------------- !
! This output is generated using Nettoolkit utility.
! Script written by : Aliasgar Hozaifa Lokhandwala (aholo2000@gmail.com)
! Write an email if any errors found.
! ---------------------------------------------------------------------------- !
"""
juniper_banner = """
# ---------------------------------------------------------------------------- #
# This output is generated using Nettoolkit utility.
# Script written by : Aliasgar Hozaifa Lokhandwala (aholo2000@gmail.com)
# Write an email if any errors found.
# ---------------------------------------------------------------------------- #
"""

# -----------------------------------------------------------------------------
# connection Object (2nd Connection)
# -----------------------------------------------------------------------------

class conn(object):
	"""Initiate an active connection.  
	use it with context manager to execute necessary commands on to it.

	Args:
		ip (str): ip address of device to establish ssh connection with
		un (str): username to login to device
		pw (str): user password to login to device
		en (str): enable password (For cisco)
		delay_factor (int): connection stability factor
		devtype (str, optional): device type from DeviceType class. Defaults to ''.
		hostname (str, optional): hostname of device ( if known ). Defaults to ''.

	Properties:
		hn (str): hostname
		devvar (dict) : {'ip':ip, 'host':hostname}
		devtype (str) : device type ('cisco_ios', 'arista_eos', 'juniper_junos')
	"""    	
	# Connection Initializer
	def __init__(self, 
		ip, 
		hostname='', 
		device=None,
		):
		self.tmp_device_conn_log = ''
		self.conn_time_stamp = LOG.time_stamp()
		self._devtype = device.dev.dtype    			# eg. cisco_ios
		self._devvar = {'ip': ip, 'host': hostname }	# device variables
		self.device = device
		self.__set_local_var(device.auth['un'], device.auth['pw'], device.auth['en'])	    # setting 
		self.max_cmd_len = 10
		self.banner = juniper_banner if self.devtype == 'juniper_junos' else cisco_banner
		self.delay_factor = device.delay_factor
		self.clsString = f'Device Connection: {self.devtype}/{self._devvar["ip"]}/{self._devvar["host"]}'
		self.__connect
		self.devvar = self._devvar

	def _device_conn_log(self, display, msg):
		self.device._device_exec_log(display, msg)

	# context load
	def __enter__(self):
		if self.connectionsuccess:
			self.__set_hostname
			self.clsString = f'Device Connection: {self.devtype}/{self._devvar["ip"]}/{self._devvar["host"]}'
			self._device_conn_log(display=True, msg=f"[+] {self._devvar['ip']} - conn - entered - {self.clsString}")
		else:
			self._device_conn_log(display=True, msg=f"[-] {self._devvar['ip']} - conn - entery - failed")
		return self      # ip connection object

	# cotext end
	def __exit__(self, exc_type, exc_value, tb):
		try:
			self._device_conn_log(display=True, msg=f"[+] {self._devvar['host']} : INFO : conn - terminate - {self.clsString}")
		except:
			self._device_conn_log(display=True, msg=f"[-] {self._devvar['ip']} - conn - terminate - {self.clsString}")
		self.__terminate
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_value, tb)

	# representation of connection
	def __repr__(self):
		return self.clsString

	@property
	def clsStr(self):
		return self.clsString
	@clsStr.setter
	def clsStr(self, s):
		self.clsString = s

	# RETURN --- > DEVICETYPE
	@property
	def devtype(self):
		"""device type
		* 'cisco': 'cisco_ios',
		* 'arista': 'arista_eos',
		* 'juniper': 'juniper_junos'

		Returns:
			str: device type
		"""    
		return self._devtype

	# RETURN --- > DEVICE HOSTNAME
	@property
	def hn(self):
		"""device hostname

		Returns:
			str: device hostname
		"""    
		return self._devvar['host'].lower()

	# set connection var|properties
	def __set_local_var(self, un, pw, en):
		'''Inherit User Variables'''
		self._device_conn_log(display=True, msg=f"[+] {self._devvar['ip']} - conn - setting up auth parameters")
		self._devvar['username'] = un
		self._devvar['password'] = pw
		self._devvar['secret'] = en
		if self._devtype == '':
			self._devtype = DeviceType(self._devvar['ip'], 
				self._devvar['username'], self._devvar['password'],
				).device_type 
		self._devvar['device_type'] = self._devtype

	# establish connection
	@property
	def __connect(self):
		self._device_conn_log(display=True, msg=f"[+] {self._devvar['ip']} - conn - start ConnectHandler")
		try:
			self.net_connect = ConnectHandler(**self._devvar) 
			self.connectionsuccess = True			
		except:
			self.connectionsuccess = False
		if not self.connectionsuccess: return

		self._devvar['host'] = STR.hostname(self.net_connect).lower()
		self._hn = self._devvar['host']
		if self._devvar['device_type'].lower() in ('cisco_ios', ):
			for tries in range(3):
				try:
					if self.net_connect.check_enable_mode():
						break
					self.net_connect.enable(cmd="enable")
					break
				except:
					self._device_conn_log(display=True, msg=f"[-] {self._devvar['host']} - enable failed on attemp {tries}")
					continue

	# set connection hostname property
	@property
	def __set_hostname(self):
		self._devvar['host'] = STR.hostname(self.net_connect)

	# terminate/disconnect session
	@property
	def __terminate(self):
		try:
			self.net_connect.disconnect()
		except:
			pass

	@property
	def find_prompt(self):
		try:
			return self.net_connect.find_prompt()
		except:
			print(f"Unable to retrive prompt from connection")

	@property
	def host(self):
		try:
			return self.net_connect.host
		except:
			print(f"Unable to retrive host from connection")

	@property
	def device_type(self):
		try:
			return self.net_connect.device_type
		except:
			print(f"Unable to retrive device_type from connection")

	@property
	def check_enable_mode(self):
		try:
			return self.net_connect.check_enable_mode()
		except:
			print(f"Unable to retrive check_enable_mode from connection")

	@property
	def check_config_mode(self):
		try:
			return self.net_connect.check_config_mode()
		except:
			print(f"Unable to retrive check_config_mode from connection")
