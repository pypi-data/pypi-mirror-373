
# ---------------------------------------------------------------------------
# IMPORT
# ---------------------------------------------------------------------------
from jumpssh import SSHSession
from dataclasses import dataclass, field


# ======================================================================================================
#  Jump Server Object 
# ======================================================================================================
@dataclass
class JumpServer():
	server: str = '' 
	server_login_username: str = ''
	server_private_key_file: str = field(default=None)
	server_login_password: str = field(default=None)

	def __post_init__(self):
		self.create_server_session()
		self.connect_server()

	# ssh session :  laptop to jump server
	def create_server_session(self):
		try:
			if self.server_private_key_file is not None:
				print(f"[+] Logging server {self.server} with username {self.server_login_username}, using PSK")
				self.session_obj = SSHSession(host=self.server,  username=self.server_login_username, private_key_file=self.server_private_key_file)
			else:
				print(f"[+] Logging server {self.server} with username {self.server_login_username}, using password {self.server_login_password}")
				self.session_obj = SSHSession(host=self.server,  username=self.server_login_username, password=self.server_login_password)
			#
		except Exception as e:
			print(f"[-] Error Establising ssh session for server {self.server} using username {self.server_login_username}\n{e}")
			quit()

	def connect_server(self):
		self.server_session = self.session_obj.open()
		print(f"[+] Logging server {self.server}... Successful")

	def erase_hostkey(self, host):
		try:
			print(f"  [~] Erasing stored public key for {host}")
			return self.server_session.get_cmd_output(f"ssh-keygen -R {host}")
			print(f"  [+] Erasing stored public key for {self.device}... Completed")
		except:
			print(f"  [-] Erasing stored public key for {self.device}... Failed")
			return False

	def get_cmd_output(self, cmd):
		return self.server_session.get_cmd_output(cmd)

	def get_remote_session(self,*args, **kwargs):
		return self.server_session.get_remote_session(*args, **kwargs)

# ======================================================================================================
if __name__ == '__main__':
	pass
# ======================================================================================================
