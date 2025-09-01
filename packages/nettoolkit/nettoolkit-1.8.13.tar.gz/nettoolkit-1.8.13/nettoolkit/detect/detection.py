
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import paramiko
from time import sleep
from nettoolkit.nettoolkit_common import STR


# -----------------------------------------------------------------------------
# Device Manufacturer Detection
# -----------------------------------------------------------------------------
class DeviceType():
	"""'Defines Device type ( 'cisco_ios', 'arista_eos', 'juniper_junos')

	Args:
		dev_ip (str): ip address of device
		un (str): username to login to device
		pw (str): password to login to device
	
	Properties:
		dtype (str): device type (default/or exception will return 'cisco_ios')
	"""    	

	# INITIALIZER - DEVICE TYPE
	def __init__(self, dev_ip, un, pw):
		self.dev_ip = dev_ip
		self.device_types = {'cisco': 'cisco_ios',
						'arista': 'arista_eos',
						'juniper': 'juniper_junos'}
		self.tmp_device_detection_log = ''
		self.dtype = self._device_make(dev_ip, un, pw)

	def _device_detection_log(self, display, msg):
		if display: print(msg)
		self.tmp_device_detection_log += msg +"\n"

	# device type
	@property
	def dtype(self):
		"""device type
		* 'cisco': 'cisco_ios',
		* 'arista': 'arista_eos',
		* 'juniper': 'juniper_junos'

		Returns:
			str: device type
		"""    		
		return self.device_type

	# set device type
	@dtype.setter
	def dtype(self, devtype='cisco'):
		self.device_type = self.device_types.get(devtype, 'cisco_ios')
		self._device_detection_log(display=True, msg=f"[+] {self.dev_ip} - Detected Device Type - {self.device_type}")
		return self.device_type

	# device make retrival by login
	def _device_make(self, dev_ip, un, pw):
		connection = False
		with paramiko.SSHClient() as ssh:
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			try:
				ssh.connect(dev_ip, username=un, password=pw)
				self._device_detection_log(display=True, msg=f"[+] {dev_ip} - Device SSH Connection Success - using username {un}")
				connection = True
			except (paramiko.SSHException, 
					paramiko.ssh_exception.AuthenticationException, 
					paramiko.AuthenticationException
					) as e:
				self._device_detection_log(display=True, msg=f"[-] {dev_ip} - Device SSH Connection Failure - using username {un}")
				pass
			if not connection: return None
			with ssh.invoke_shell() as remote_conn:
				remote_conn.send('\n')
				sleep(1)
				self._device_detection_log(display=True, msg=f"[+] {dev_ip} - Verifying show version output")
				remote_conn.send('ter len 0 \nshow version\n')
				sleep(2)
				output = remote_conn.recv(5000000).decode('UTF-8').lower()
				#
				for k, v in self.device_types.items():
					if STR.found(output, k): 
						self._device_detection_log(display=True, msg=f"[+] {dev_ip} - Got - {k}")
						return k

# -----------------------------------------------------------------------------
