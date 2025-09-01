
CMD_LINE_START_WITH = "output for command: "


class DevicePapa():
	"""Parent class defining common methods/properties of device

	Args:
		file (str): file name
	"""    	

	def __init__(self, file):
		"""initialize the object by providing filename.
		"""    		
		self.file = file

	def _run_parser(self, parse_func, op_list, *arg, **kwarg):
		if not parse_func: return None
		return parse_func(op_list, *arg, **kwarg)

