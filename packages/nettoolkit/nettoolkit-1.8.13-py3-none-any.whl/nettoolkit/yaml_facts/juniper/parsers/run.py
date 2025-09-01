"""juniper protocol related common classes - parent """

# ------------------------------------------------------------------------------
from .common import *
from abc import abstractclassmethod
# ------------------------------------------------------------------------------

# ==========================================================================
#  STANDARD CLASS GATHERING INFO ON SHOW CONFIGURATION
#  Initialize by converting standard config to set config
# ==========================================================================
@dataclass
class Running():
	"""Base class for show configuration parsing common methods

	Raises:
		Exception: if necessary capture is missing in output
	"""    
	cmd_op: list[str,] = field(default_factory=[])

	def __post_init__(self):
		if self.cmd_op:	
			JS = JSet(input_list=self.cmd_op)
			JS.to_set
			self._set_cmd_op = verifid_output(JS.output)
			self.separate_logical_systems()
			self.set_cmd_op = self.logical_systems[None]
		else:
			self._set_cmd_op = []
			raise Exception(f'[-] Missing Configuration capture.. {self.cmd_op}, verify input')

	def separate_logical_systems(self):
		self.logical_systems = {None: []}
		for line in self._set_cmd_op:
			if line.startswith("set logical-systems "):
				system_name = line.split()[2]
				if not self.logical_systems.get(system_name):
					self.logical_systems[system_name] = []
				self.logical_systems[system_name].append(line)
			else:
				self.logical_systems[None].append(line)

	def iterate_logical_systems(self, hierarchy):
		self.logical_systems_dict = {}		
		sys_dict = add_blankdict_key(self.logical_systems_dict, 'logical-systems')
		for logical_system, logical_system_list in self.logical_systems.items():
			self.set_cmd_op = logical_system_list
			dic = self.start()
			if not dic: continue
			sys_dict[logical_system] = {hierarchy: dic}
		if not self.logical_systems_dict['logical-systems']: return
		if len(self.logical_systems.keys()) == 1 :
			self.logical_systems_dict =  self.logical_systems_dict['logical-systems'][None]

	@abstractclassmethod
	def start(self): pass

	def remove_parent_vrf_if_standalone(self, protocol_dict):
		if len(protocol_dict.keys()) == 1 and None in protocol_dict:
			protocol_dict = protocol_dict[None]
		return protocol_dict



# ==========================================================================
#  STANDARD CLASS GATHERING BGP PEER COMMANDS
# ==========================================================================
@dataclass
class PeerLines():
	"""Base class to filter BGP Peer lines 

	Yields:
		tuple: peer lines, splitted peer lines
	"""    	
	bgp_peer_group_lines: list[str] = field(default_factory=[])
	peer: str = ''

	def __post_init__(self):
		self._set_peer_group_lines()
		self._set_peer_group_lines_spl()

	def __iter__(self):
		for line, spl in zip(self.peer_group_lines, self.peer_group_lines_spl):
			yield (line, spl)

	@property
	def peer_group_lines(self):
		return self._peer_group_lines

	@property
	def peer_group_lines_spl(self):
		return self._peer_group_lines_spl

	def _set_peer_group_lines(self):
		self._peer_group_lines = [line for line in self.bgp_peer_group_lines if line.find(f" protocols bgp group {self.peer} ") > 0]

	def _set_peer_group_lines_spl(self):
		self._peer_group_lines_spl = [line.strip().split() for line in self.peer_group_lines ]

# ==========================================================================
#  STANDARD CLASS GATHERING INSTANCE LINES OF A PROTOCOL
# ==========================================================================
@dataclass
class VrfLines():
	"""Base class to filter a protocol instance lines

	Yields:
		str: filtered lines
	"""    	
	protocol: str = 'bgp'
	vrf: str = ''
	protocol_lines: list[str] = field(default_factory=[])
	protocol_spl_lines: list[str] = field(default_factory=[])

	def __post_init__(self):
		self._get_protocol_vrf_lines()
		self._get_bgp_peer_group_lines()
		self._get_bgp_other_lines()
		self._get_peer_groupnames()
		self()

	def __call__(self):
		if self.protocol == 'bgp':
			self._iterate_peer_groups()

	def __iter__(self):
		lines = self.bgp_peer_group_lines if self.protocol == 'bgp' else self.protocol_vrf_lines
		for x in lines:
			yield x

	def _get_protocol_vrf_lines(self):
		lns = []
		for line, spl in zip(self.protocol_lines, self.protocol_spl_lines):
			if spl[1] == 'protocols':
				if self.vrf: continue
				lns.append(line)
				continue
			if spl[2] != self.vrf: continue
			lns.append(line)
		self._protocol_vrf_lines = lns

	@property
	def protocol_vrf_lines(self):
		return self._protocol_vrf_lines

	@property
	def bgp_peer_group_lines(self):
		return self._bgp_peer_group_lines

	@property
	def bgp_other_lines(self):
		return self._bgp_other_lines

	@property
	def peer_group_names(self):
		return self._peer_group_names

	def _get_bgp_peer_group_lines(self):
		self._bgp_peer_group_lines = []
		if self.protocol == 'bgp':
			self._bgp_peer_group_lines = [ line for line in self.protocol_vrf_lines if line.find(" protocols bgp group ") > 0 ]

	def _get_bgp_other_lines(self):
		self._bgp_other_lines = []
		if self.protocol == 'bgp':
			self._bgp_other_lines = [ line for line in self.protocol_vrf_lines if line.find(" protocols bgp group ") == -1 ]

	def _get_peer_groupnames(self):
		self._peer_group_names = set()
		for line in self.bgp_peer_group_lines:
			self._peer_group_names.add( line.split(" protocols bgp group ")[-1].split()[0] )

	def _iterate_peer_groups(self):
		self.PEERs = {}
		for peer in self.peer_group_names:
			self.PEERs[peer] = PeerLines(self.bgp_peer_group_lines, peer)

# ==========================================================================
#  STANDARD CLASS GATHERING ALL PROTOCOLS LINES
# ==========================================================================
@dataclass
class jProtocolLines():
	"""Base class for all protocol lines

	Yields:
		str: protocol lines
	"""    	
	config_lines: list[str,] = field(default_factory=[])
	protocol: str = 'bgp'

	def __post_init__(self):
		self._get_protocol_set_commands()
		self._get_vrfs()
		self._iterate_vrfs()

	def __iter__(self):
		for x in self.protocol_lines:
			yield x

	def _get_protocol_set_commands(self):
		lns = []
		spl_lns = []
		for line in self.config_lines:
			if blank_line(line): continue
			if line.strip().startswith("#"): continue
			# line = line.strip()
			if line.find(f' protocols {self.protocol} ') == -1: continue
			spl = line.strip().split()
			proto_idx = spl.index('protocols')
			# if "prefix-list" in spl and spl.index('prefix-list') < proto_idx: continue
			lns.append(line)
			spl_lns.append(spl)
		self.protocol_lines = lns
		self.protocol_spl_lines = spl_lns

	def _get_vrfs(self):
		vrfs = {None,}
		for line in self.config_lines:
			spl = line.split()
			if spl[1] != 'routing-instances': continue
			vrfs.add(spl[2])
		self.vrfs = vrfs

	def _iterate_vrfs(self):
		self.VRFs = {}
		for vrf in self.vrfs:
			self.VRFs[vrf] = VrfLines(self.protocol, vrf, self.protocol_lines,  self.protocol_spl_lines)


# ==========================================================================
#  STANDARD PROTOCOL IMPLEMENTATION
#  CLASS RETURNING AN INITIALIZED PROTOCOL OBJECT
#  INHERIT TO UTILIZE ITS FUNCTIONALITY
# ==========================================================================
@dataclass
class ProtocolObject(Running):
	"""Base class to return an object for a protocol lines.

	Args:
		cmd_op (list): list of output
		protocol (str): protocol for which lines to be filtered.
	"""
	cmd_op: list[str,] = field(default_factory=[])
	protocol: str = None

	def initialize(self, protocol):
		super().__post_init__()
		self.jPtObj = jProtocolLines(self.set_cmd_op, protocol)

# ==========================================================================
