
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import paramiko
from time import sleep
from nettoolkit.nettoolkit_common import STR


# -----------------------------------------------------------------------------
class DeviceType():
	"""Deprycated"""    	

	def __init__(self, dev_ip, un, pw):
		print("DEPRYCATION WARNING: nettoolkit.capture_it._detection.DeviceType is deprycated."
			"Your code is failing. Start using nettoolkit.detect.detection.DeviceType instead."
			)
# -----------------------------------------------------------------------------


def quick_display(dev_ip, auth, cmds, wait):
	"""quick display of  command(s) output on console screen. No log capture.

	Args:
		dev_ip (str): ip address of a device
		auth (dict): authentication dictionary format = { 'un': username, 'pw': password, 'en': enablepassword }
		cmds (str, list): a single show command or list of show commands
		wait (int): seconds to wait before taking output. (default=3) increase value if expected command output lengthy.

	Returns:
		None
	"""	
	with paramiko.SSHClient() as ssh:
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			ssh.connect(dev_ip, username=auth['un'], password=auth['pw'])
		except (paramiko.SSHException, 
				paramiko.ssh_exception.AuthenticationException, 
				paramiko.AuthenticationException
				) as e:
			print(f"[-] {dev_ip}: Device SSH Connection Failure - using username {auth['un']}")
			return None

		if isinstance(cmds, str):
			cmds = [cmds,]

		with ssh.invoke_shell() as remote_conn:
			prompt = remote_conn.recv(1000).decode('UTF-8')[-1]
			if prompt != "#":
				remote_conn.send('\nen\n')
				sleep(1)
				remote_conn.send(f'{auth["en"]}\n')
				sleep(1)

			for cmd in cmds:
				remote_conn.send(f'ter len 0 \n{cmd}\n')
				sleep(wait)
				s = remote_conn.recv(50000000).decode('UTF-8')
				s = s.replace("\r", "")
				print(s)

	return None
