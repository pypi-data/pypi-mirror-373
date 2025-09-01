"""juniper bgp protocol routing instances parsing from set config  """

# ------------------------------------------------------------------------------
from .common import *
from .run import ProtocolObject
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#  bgp parser functions
# ------------------------------------------------------------------------------
def get_bgp_peer_peers(peer_dict, spl):
	if 'neighbor' not in spl: return
	dic = add_blankdict_key(peer_dict, 'peers')
	add_blankdict_key(dic, spl[5])

def get_bgp_peer_description(peer_dict, spl):
	if "description" not in spl: return
	desc_idx = spl.index("description")+1
	desc = " ".join(spl[desc_idx:]).strip()
	if desc[0] == '"': desc = desc[1:]
	if desc[-1] == '"': desc = desc[:-1]
	if desc_idx == 7:
		peer_dict = peer_dict['peers'][spl[5]]
	peer_dict['description'] = desc

def get_bgp_peer_auth(peer_dict, spl):
	if 'authentication-key' not in spl: return
	key_idx = spl.index("authentication-key")+1
	pw = " ".join(spl[key_idx:]).strip().split("##")[0].strip()
	if pw[0] == '"': pw = pw[1:]
	if pw[-1] == '"': pw = pw[:-1]
	try:
		pw = juniper_decrypt(pw)
	except: pass
	if key_idx == 7:
		peer_dict = peer_dict['peers'][spl[5]]		
	peer_dict['password'] = pw

def get_bgp_peer_peeras(peer_dict, spl):
	get_bgp_peer_common_info(peer_dict, spl, item='peer-as', sub_item_idx=7)

def get_bgp_peer_localas(peer_dict, spl):
	get_bgp_peer_common_info(peer_dict, spl, item='local-as', sub_item_idx=7)

def get_bgp_peer_multihop(peer_dict, spl):
	item, sub_item_idx = 'multihop', 7
	if item not in spl: return
	_idx = spl.index(item)+1
	if sub_item_idx == _idx:
		peer_dict = peer_dict['peers'][spl[sub_item_idx-2]]
	peer_dict[item] = spl[-1]

### // Common // ###
def get_bgp_peer_common_info(peer_dict, spl, item, sub_item_idx):
	if item not in spl: return
	_idx = spl.index(item)+1
	if sub_item_idx == _idx:
		peer_dict = peer_dict['peers'][spl[sub_item_idx-2]]
	peer_dict[item] = spl[_idx]

# ------------------------------------------------------------------------------
#  bgp extractor class
# ------------------------------------------------------------------------------

@dataclass
class BGP(ProtocolObject):
	cmd_op: list[str,] = field(default_factory=[])

	bgp_attr_functions = (
		## tbd
	)
	peer_attr_functions = [
		get_bgp_peer_peers,
		get_bgp_peer_description,
		get_bgp_peer_auth,
		get_bgp_peer_peeras,
		get_bgp_peer_localas,
		get_bgp_peer_multihop,
	]


	def __post_init__(self):
		super().initialize('bgp')

	def __call__(self):
		self.iterate_logical_systems(hierarchy='protocols')

	def start(self):
		self.add_protocol_bgp_instance_peers()
		self.protocol_bgp_dict = {'bgp': {'instances': self.protocol_instances}} if self.protocol_instances else {}
		return self.protocol_bgp_dict
			

	def add_protocol_bgp_instance_peers(self):
		self.protocol_instances = {}
		for vrf in self.jPtObj.VRFs.keys():
			VRF = self.jPtObj.VRFs[vrf]
			vd = self.get_peers_dict(peers=VRF.PEERs, vrf=vrf)
			if not vd: continue
			instance_dict = add_blankdict_key(self.protocol_instances, vrf)
			instance_dict['peers'] = vd

	def get_peers_dict(self, peers, vrf):
		peers_dict = {}
		for peer in peers.keys():
			psd = self._iterate_peer_lines(peers, peer)
			if psd: peers_dict[peer] = psd
		return peers_dict

	def _iterate_peer_lines(self, peers, peer):
		peer_dict = {}
		for line, spl in peers[peer]:
			proto_idx = spl.index('protocols')
			spl = spl[proto_idx:]
			self.iterate_peer_funcs(peer_dict, spl)
		return peer_dict

	def iterate_peer_funcs(self, peer_dict, spl):
		for f in self.peer_attr_functions:
			f(peer_dict, spl)


# ------------------------------------------------------------------------------
#  bgp parser calling function
# ------------------------------------------------------------------------------
def get_bgp_running(cmd_op):
	"""parse output of : show configurtain

	Args:
		command_output (list): command output

	Returns:
		dict: protocols bgp level parsed output dictionary
	"""    	
	B = BGP(cmd_op)
	B()
	return B.logical_systems_dict
# ------------------------------------------------------------------------------

