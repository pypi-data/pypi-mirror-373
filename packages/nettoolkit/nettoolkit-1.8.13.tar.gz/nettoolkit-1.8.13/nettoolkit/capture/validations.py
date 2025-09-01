# ---------------------------------------------------------------------------
# IMPORT
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Global Var
# ---------------------------------------------------------------------------
VALID_DEVICE_TYPES = ('cisco', 'juniper', 'arista')


# ======================================================================================================
#  Input Validation Class
# ======================================================================================================
class Validate(object):

	def input_server_str(self):
		if not isinstance(self.server, str):
			raise Exception(f"input error: type mismatch for input - server: expected `str` got {type(self.server)}")

	def input_server_login_username_str(self):
		if not isinstance(self.server_login_username, str):
			raise Exception(f"input error: type mismatch for input - server_login_username: expected `str` got {type(self.server_login_username)}")

	def input_devices_iterable(self):
		if not isinstance(self.devices, (list, set, tuple)):
			raise Exception(f"input error: type mismatch for input - server: expected `iterable` got {type(self.devices)}")

	def input_device_username_str(self):
		if not isinstance(self.device_username, str):
			raise Exception(f"input error: type mismatch for input - device_username: expected `str` got {type(self.device_username)}")

	def input_interactive_cmd_report_bool(self):
		if not isinstance(self.interactive_cmd_report, bool):
			raise Exception(f"input error: type mismatch for input - interactive_cmd_report: expected `bool` got {type(self.interactive_cmd_report)}")

	def input_final_cmd_report_bool(self):
		if not isinstance(self.final_cmd_report, bool):
			raise Exception(f"input error: type mismatch for input - final_cmd_report: expected `bool` got {type(self.final_cmd_report)}")

	def input_append_bool(self):
		if not isinstance(self.append, bool):
			raise Exception(f"input error: type mismatch for input - append: expected `bool` got {type(self.append)}")

	def input_missing_only_bool(self):
		if not isinstance(self.missing_only, bool):
			raise Exception(f"input error: type mismatch for input - missing_only: expected `bool` got {type(self.missing_only)}")
		if self.missing_only: self.append = True

	def input_cumulative_bool(self):
		if not self.cumulative in (True, False, 'both'):
			raise Exception(f"input error: type mismatch for input - cumulative: expected `boolean` or `both` got {type(self.cumulative)}")

	def input_max_connections_int(self):
		if not isinstance(self.max_connections, int):
			print(f"input error: type mismatch for input - max_connections: expected `int` got {type(self.max_connections)}. Setting default : 100")
			self.max_connections = 100

	def input_tablefmt_str(self):
		if not isinstance(self.tablefmt, str):
			raise Exception(f"input error: type mismatch for input - tablefmt: expected `str` got {type(self.tablefmt)}")

	def input_cmds_list_dict_dict(self):
		if not isinstance(self.cmds_list_dict, dict):
			raise Exception(f"input error: type mismatch for input - cmds_list_dict: expected `dict` got {type(self.cmds_list_dict)}")
		for device_type, commands in self.cmds_list_dict.items():
			if device_type not in VALID_DEVICE_TYPES:
				raise Exception(f"input error: Invalid device type detected - {device_type}, should be any of {VALID_DEVICE_TYPES}")
			if not isinstance(commands, (list,set,tuple)):
				raise Exception(f"input error: Invalid type of commands list detected for {device_type}. Expected `list/tuple/set` got {type(commands)}")


# ======================================================================================================
if __name__ == '__main__':
	pass
# ======================================================================================================

