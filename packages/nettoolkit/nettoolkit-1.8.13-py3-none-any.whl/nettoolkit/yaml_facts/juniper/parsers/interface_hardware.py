"""juniper show chassis hardware command output parser """

# ------------------------------------------------------------------------------
from .common import *
# ------------------------------------------------------------------------------

def get_chassis_hardware(cmd_op):
	"""parse output of : show chassis hardware

	Args:
		command_output (list): command output

	Returns:
		dict: interface level parsed output dictionary
	"""    	
	op_dict = {}
	try:
		parsed_data_dict_list = parse_to_dict_using_ntc('show chassis hardware', cmd_op)
		parsed_data = parse_to_list_using_ntc('show chassis hardware', cmd_op)
	except:
		op_dict = get_chassis_hardware_iterative(cmd_op)
		return {'interfaces': {'physical_media': op_dict}}
	#
	for dic in parsed_data_dict_list:
		first_item_part_no = dic['PART']
		break
	#
	for spl in parsed_data:
		part_idx = spl.index(first_item_part_no)
		break
	#
	for spl in parsed_data:
		port = "/".join(LST.remove_empty_members(spl[:part_idx]))
		sfp_part_id = spl[part_idx]
		sfp_serial = spl[part_idx+1]
		sfp = spl[part_idx+2]
		if not op_dict.get(port):
			op_dict[port] = {}
		op_dict[port]['media_type'] = sfp 
		op_dict[port]['serial'] = sfp_serial
		op_dict[port]['part_id'] = sfp_part_id 

	return {'interfaces': {'physical_media': op_dict}}
# ------------------------------------------------------------------------------

def get_chassis_hardware_iterative(cmd_op):
	cmd_op = verifid_output(cmd_op)
	toggle = False
	JCH = JuniperChassisHardware(cmd_op)
	return JCH.ports

class JuniperChassisHardware():
	"""read the show chassis hardware output from juniper and returns port type(sfp)

	Args:
		output (list): show chassis hardware output in list
	"""

	def __init__(self, output):
		"""initialize and read output
		"""    		
		self.fpc, self.pic = '', ''
		self.port = ''
		self.ports = {}
		self._read(output)

	def _read(self, output):
		"""read the output and adds line to port info

		Args:
			output (list): show chassis hardware command output in list
		"""		
		for l in output:
			if not l.strip(): continue
			self._add(l)

	def _add(self, line):
		"""adds port info from line 

		Args:
			line (str): line outout
		"""		
		# if line.upper().find("BUILTIN") > 0: return         # Some of juniper output are incosistent so removed.
		spl = line.strip().split()
		if not spl[0].upper() in ("FPC", "PIC", "XCVR"): return
		if spl[0].upper() in ("FPC"):
			self.fpc = spl[1]
			self.pic = ''
		elif spl[0].upper() in ("PIC"):
			self.pic = self.fpc + "/" + spl[1]
		elif spl[0].upper() in ('XCVR',):
			self.port = self.pic + "/" + spl[1]
			if not self.ports.get(self.port): self.ports[self.port] = {}
			self.ports[self.port]['media_type'] = spl[-1]
			self.ports[self.port]['serial'] = spl[-2]
			self.ports[self.port]['part_id'] = spl[-3]
			self.port=''

	def get_sfp(self, port):
		"""get the SFP details for given port

		Args:
			port (str): port number only (port type to be excluded)

		Returns:
			str: SFP type
		"""    		
		for p, sfp in self.ports.items():
			spl_port = port.split("-")
			if spl_port[-1] == p:
				return sfp
		return ""

