
from collections import OrderedDict
from functools import total_ordering
import pandas as pd

from nettoolkit.nettoolkit_common import STR, LST, IO

# from errors import incorrectinput
incorrectinput = 'INCORRECT SUBNET OR SUBNET MASK DETECTED NULL RETURNED'
SQRS = [2**x for x in range(32)]

# ----------------------------------------------------------------------------
# Module Functions
# ----------------------------------------------------------------------------

def expand(v6subnet, withMask=False):
	"""Expand the V6 subnet to its full length.

	Args:
		v6subnet (str): zipped v6 subnet

	Returns:
		str: expanded v6 subnet
	"""	
	# try:
	p = ''
	sip = v6subnet.split("/")[0].split("::")
	if withMask and len(v6subnet.split("/"))>1: mask = v6subnet.split("/")[1]
	if len(sip) == 2:
		# ~~~~~~ No padding, inserting zeros in middle ~~~~~~~
		for x in range(1, 9):
			p = STR.string_concate(p, get_hext(v6subnet, hexTnum=x), conj=':')
		v6subnet = p
	else :
		# ~~~~~~~ pad leading zeros ~~~~~~~
		lsip = sip[0].split(":")
		for x in range(8-len(lsip), 0, -1):
			p = STR.string_concate(p, '0', conj=":")
		if p != '':
			v6subnet = p + ':' + v6subnet
	if withMask:
		return f'{v6subnet}/{mask}'
	else:
		return v6subnet
	# except:
	# 	return False

def shrink(v6subnet, withMask=True):
	"""Shrinks the V6 subnet to its standard shortend length.

	Args:
		v6subnet (str): v6 subnet

	Returns:
		str: shrinked v6 subnet
	"""	
	if v6subnet.find("::") > -1: return v6subnet
	try:
		if withMask: mask = v6subnet.split("/")[1]
	except Exception as e:
		raise Exception(f"InvalidInput {v6subnet}, {withMask}\n{e}")
	s = v6subnet.split("/")[0].split(":")

	zero_count, zero_counts, zerostart = 0 , {}, False
	for i, h in enumerate(s):
		zerostart = h == '0'
		if not zerostart: 
			zero_count = 0
			continue
		zero_count += 1
		zero_counts[zero_count] = i 

	for i, x in enumerate(range(zero_counts[max(zero_counts)], zero_counts[max(zero_counts)]-max(zero_counts), -1)):
		if i == 0:
			s[x] = ':'
		else:
			del(s[x])

	for i, x in enumerate(s):
		if i == 0 or i == len(s)-1: continue
		if x == ':': s[i] = ''

	s = ":".join(s)
	if s  == ":": s = "::"
	if withMask:
		s += "/"+mask
	return s 

def get_hext(v6subnet, hexTnum, s=''):	
	"""get the a hextate of v6 subnet.

	Args:
		v6subnet (str): v6 subnet string
		hexTnum (int): hextate number

	Raises:
		Exception: Raise Exception if incorrect input

	Returns:
		str: hextate string
	"""	
	test = hexTnum == 1
	if s == '':
		s = v6subnet.split("/")[0]
	try:
		if s != '' and all([hexTnum>0, hexTnum<=8]):
			sip = s.split("/")[0].split("::")
			lsip = sip[0].split(":")
			if hexTnum <= len(lsip):
				lsiphext = lsip[hexTnum-1]
				if lsiphext: return lsip[hexTnum-1]
				return '0'
			else:
				rsip = sip[1].split(":")
				if rsip[0] == '': rsip = []
				if 8-hexTnum < len(rsip):
					return rsip[(9-hexTnum)*-1]
				else:
					return '0'
		else:
			raise Exception(incorrectinput)
			return None
	except:
		raise Exception(incorrectinput)
		return None


def bin_mask(mask):
	"""mask representation in binary (ex: 255.255.255.0)

	Args:
		mask (int): mask in number 

	Returns:
		str: mask in 8 byte format
	"""    	
	mask = int(mask)
	decmask = mask*str(1) + (32-mask)*str(0)
	o1 = str(int(decmask[ 0: 8] , 2))
	o2 = str(int(decmask[ 8: 16], 2))
	o3 = str(int(decmask[16: 24], 2))
	o4 = str(int(decmask[24: 32], 2))
	return o1+'.'+o2+'.'+o3+'.'+o4	


def invmask_to_mask(invmask):
	"""convert inverse mask to decimal mask

	Args:
		invmask (str): mask representation in inverse format (ex: 0.0.0.31)

	Returns:
		int: mask (ex: 27)
	"""	
	m = binsubnet(invmask)
	return 32 - m.count("1")


def _invalid_subnet(subnet): 
	"""invalid subnet str
	"""	
	return f"Not a VALID Subnet {subnet}"


def to_dec_mask(dotted_mask):
	"""Decimal mask representation

	Args:
		dotted_mask (str): input mask = dotted mask

	Returns:
		int: mask
	"""    	
	return bin2decmask(binsubnet(dotted_mask))


def bin2dec(binnet): 
	"""Decimal network representation / integer value

	Args:
		binnet (str): input = dotted network

	Returns:
		int: decimal number of network
	"""	
	if not binnet: return 0
	return int(binnet, 2)


def bin2decmask(binmask):
	"""Decimal mask representation / integer value

	Args:
		binmask (str): input mask = binary mask in number

	Returns:
		int: mask
	"""    	
	return binmask.count('1')


def binsubnet(subnet):
	"""convert subnet to binary:0s and 1s

	Args:
		subnet (str): subnet string (v4, v6)

	Returns:
		str: binary subnet representation ( 0s and 1s )
	"""    	
	try:
		if STR.found(subnet, "."): version, split_by, bit_per_oct = 4, ".", 8
		if STR.found(subnet, ":"): version, split_by, bit_per_oct = 6, ":", 16
		s = ''
		octs = subnet.split("/")[0].split(split_by)
		for o in octs:
			if version == 4:
				bo = str(bin(int(o)))[2:]
			elif version == 6:
				bo = str(bin(int(o, bit_per_oct)))[2:]
			lbo = len(bo)
			pzero = '0'*(bit_per_oct - lbo)
			s = s + pzero + bo
		return s
	except:
		pass


def inet_address(ip, mask):
	"""return inet address from cisco standard ip and mask format

	Args:
		ip (str): ip address
		mask (str): subnet mask

	Returns:
		str: ip/mask
	"""	
	mm = to_dec_mask(mask)
	return ip+"/"+str(mm)

def get_inet_address(line):
	"""derive the ipv4 information from provided line

	Args:
		line (str): interface config line

	Returns:
		str: ipv4 address with /mask , None if not found.
	"""    	
	if line.strip().startswith("ip address ") and not line.strip().endswith('secondary'):
		spl = line.strip().split()
		ip  = spl[2]
		if ip == 'dhcp': return ""
		return inet_address(ip, spl[3])
	return None

def get_secondary_inet_address(line):
	"""derive the secondary ipv4 information from provided line

	Args:
		line (str): interface config line

	Returns:
		str: ipv4 address with /mask , None if not found.
	"""    	
	if line.strip().startswith("ip address ") and line.strip().endswith('secondary'):
		spl = line.strip().split()
		ip  = spl[2]
		if ip == 'dhcp': return ""
		return inet_address(ip, spl[3])
	return None


def get_inetv6_address(line, link_local):
	"""derive the ipv6 information from provided line

	Args:
		line (str): interface config line

	Returns:
		str: ipv6 address with /mask , None if not found.
	"""    	
	v6idx = -2 if link_local else -1
	if line.strip().startswith("ipv6 address "):
		spl = line.split()
		ip  = spl[v6idx]
		return ip
	return None



# integer to octet
def dec2dotted_ip(n):
	"""convert decimal ip address to dotted decimal ip notation.

	Args:
		n (int): integer/decimal number

	Returns:
		str: ip address (dotted decimal format)
	"""	
	bin_bytes = bin(n)[2:]
	o4 = str(int(bin_bytes[-8:], 2))
	o3 = str(int(bin_bytes[-16:-8], 2))
	o2 = str(int(bin_bytes[-24:-16], 2))
	o1 = str(int(bin_bytes[:-24], 2))
	return o1+"."+o2+"."+o3+"."+o4

# 255 -> 24
def inv_subnet_size_to_mask(n):
	"""converts inverse subnet size to get subnet mask value

	Args:
		n (int): number of ips in a subnet excluding networkip (ex: 127)

	Returns:
		int: subnet mask (25)
	"""	
	return 32-bin(n)[2:].count('1')

def mask2subnetsize(m):
	"""get subnet size from mask

	Args:
		m (n): subnet mask

	Returns:
		int: number of ip available in given subnet
	"""	
	return 2**m

# 256 -> 24
def subnet_size_to_mask(n):
	"""converts subnet size to get subnet mask value

	Args:
		n (int): number of ips in a subnet (ex: 128)

	Returns:
		int: subnet mask (25)
	"""	
	subs = []
	for x in reversed(SQRS):
		if x > n: continue
		if x == n: 
			subs.append(n)
			break
		subs.append(x)
		subs.append(n-x)
		break
	masks = []
	for n in subs:
		n = bin(n)
		masks.append(  32- (len(n) - n.rfind('1')  -1))
	if len(masks) == 1:
		return masks[0]
	else:
		return masks

def get_subnet(address):
	"""derive subnet number for provided ipv4 address

	Args:
		address (str): ipv4 address in string format a.b.c.d/mm

	Returns:
		str: subnet zero == network address
	"""    	
	return IPv4(address).subnet_zero()


def get_v6_subnet(address):
	"""derive subnet number for provided ipv6 address

	Args:
		address (str): ipv6 address in string with mask

	Returns:
		str: subnet zero == network address
	"""    	
	return IPv6(address).subnet_zero()

# decimal network ip and length -> subnet/mask
def _get_subnet(decimal_network_ip, length):
	"""get subnet/mask from decimal network ip and size of subnet

	Args:
		decimal_network_ip (int): integer/decimal number
		length (int): number of ips in a subnet (ex: 128)

	Returns:
		str: string repr of subnet (subnet/mask)
	"""	
	breakup = decimal_network_ip/length 
	s = dec2dotted_ip(decimal_network_ip) + "/" + str(subnet_size_to_mask(length))
	if breakup.is_integer():
		return s
	else:
		raise Exception(f"Invalid subnet/mask cannot return {s}")

def get_subnets(decimal_network_ip, length):
	"""get subnets and sizes from decimal network ip and subnet length (under development)

	Args:
		decimal_network_ip (int): integer/decimal number
		length (int): number of ips in a subnet (ex: 128)

	Returns:
		dict: dictionary of counts and size
	"""	
	breakup = decimal_network_ip/length 
	s = dec2dotted_ip(decimal_network_ip) + "/" + str(subnet_size_to_mask(length))
	if breakup.is_integer():
		return s
	else:
		c = 0
		for x in range(256):
			point = breakup%int(breakup)
			counts = 1/point
			if counts.is_integer():
				new_sizes = length/counts
				return {'counts': counts+c, 'size': new_sizes}
			else:
				c += 1
				breakup = counts

def is_overlap(range1, range2):
	"""check if range1 and range2 are overlaping

	Args:
		range1 (range): range1 of items
		range2 (range): range2 of items

	Returns:
		bool: whether range1 and range2 are overlaping or not.
	"""	
	if range1.start not in range2 and range1.stop-1 not in range2:
		return False
	return True

def range_subset(range1, range2):
	"""check whether range1 is a subset of range2

	Args:
		range1 (range): range1 of items
		range2 (range): range2 of items

	Returns:
		bool: whether range1 is part of range2 or not.
	"""	
	if not range1:
		return True  # empty range cannot subset of anything
	if not range2:
		return False  # non-empty range can not subset of empty range
	if len(range1) > 1 and range1.step % range2.step:
		return False  # steps check
	return range1.start in range2 and range1[-1] in range2

def classful_subnet(ip):
	"""proives ip-subnet object for classfull summary of given ip

	Args:
		ip (str): ip address or number

	Returns:
		IPv4: IPv4 object
	"""    	
	classes = {
		'0'    : 8 ,   ## A
		'10'   : 16,   ## B
		'110'  : 24,   ## C
		'1110' : None, ## D Multicast, mask not defined
		'11110': None, ## E Reserved, mask not defined
	}
	binary_ip = binsubnet(ip)
	for leadingbits, mask in classes.items():
		if binary_ip.startswith(leadingbits):
			return addressing(f"{ip}/{mask}") if mask else addressing(ip)

def addressing(subnet, ddc_mask=None):
	"""proives ip-subnet object for various functions on it

	Args:
		subnet (str): ipv4 or ipv6 subnet with/without mask
		ddc_mask (str, None): provide dottel decimal mask (v4 only) or None.

	Returns:
		IPv4, IPv6: IPv4 or IPv6 object
	"""    	
	subnet = subnet.strip()
	if ddc_mask is not None:
		try:
			mask = to_dec_mask(ddc_mask)
			if len(subnet.split("/")) == 1:
				subnet += "/" + str(mask)
			else:
				print(f"[-] Multiple mask entries received.\nsubnet mask value will {subnet} override, ddc_mask value {ddc_mask}")
		except:
			raise Exception("[-] Invalid dotted decimal mask provided... required format [255.255.255.0] got [{ddc_mask}]")
	v_obj = Validation(subnet)
	if v_obj.validated: return v_obj.ip_obj


def get_summaries(*net_list):
	"""summarize the provided network prefixes, provide all networks as arguments.

	Args:
		net_list (args): variable arguments ( networks )

	Returns:
		list: summaries
	"""    	
	if not isinstance(net_list, (list, tuple, set)): return None
	s = Summary(*net_list)
	s.calculate()
	summaries = s.prefixes
	i = 0	
	while True:
		i += 1
		if i >= MAX_RECURSION_DEPTH: break
		ss = Summary(*summaries)
		ss.calculate()
		if summaries == ss.prefixes: break
		summaries = ss.prefixes
	return sorted(summaries)
	# return sorted_v4_addresses(summaries)


def calc_summmaries(min_subnet_size, *net_list):
	"""summarize the provided network prefixes, provide all networks as arguments.
	minimum subnet summarized to provided min_subnet_size parameter

	Args:
		min_subnet_size (int): minimuze subnet mask to be summarized up on
		net_list (args): variable arguments ( networks )

	Returns:
		list: summaries
	"""    	
	summaries = get_summaries(*net_list)
	nset = set()
	for subnet in summaries:
		if isinstance(subnet, IPv4) and subnet.mask > min_subnet_size:
			nset.add(subnet.expand(min_subnet_size))
		elif isinstance(subnet, str) and int(subnet.split("/")[-1]) > min_subnet_size:
			nset.add(IPv4(subnet).expand(min_subnet_size))
	summaries.extend(nset)
	nSummaries = get_summaries(*set(summaries))
	return nSummaries

def break_prefix(pfx, mask_size):
	"""downsize larger prefix size to smaller size

	Args:
		pfx (str): prefix/subnet
		mask_size (int): required mask size numeric

	Raises:
		Exception: InputError: Invalid Prefix
		Exception: InputError: Invalid mask_size

	Returns:
		str: broken prefix
	"""    	
	try:
		s = IPv4(pfx)
	except:
		raise Exception(f"InputError: Invalid Prefix {pfx}")
	try:
		bit_length = 2**(32-mask_size)
	except:
		raise Exception(f"InputError: Invalid mask_size {mask_size}")
	d = s.size/bit_length
	return s/d

def recapsulate(subnet, size):
	"""capsulate provided subnet (str, IPv4) with given sizing.

	Args:
		subnet (str, IPv4): string or IPv4 Object
		size (int): subnet mask, for sizing

	Returns:
		str: sized/capsulated subnet
	"""    	
	if isinstance(subnet, IPv4): subnet = str(subnet)
	s = subnet.split("/")[0] + "/" + str(size)
	v4s = IPv4(s).subnet_zero(withMask=True)
	return v4s

def isSplittedRoute(line):
	"""checks if ip route is splitted in multiple lines or not.

	Args:
		line (str): ip route line from configuration

	Returns:
		int: 1: No single line,  0 : Yes splitted line [line1],  -1: Yes splitted line [line2]
	"""    	
	if STR.found(line, ','):
		return 1 if len(line.split()) > 5 else -1
	else:
		return 0

def isSubset(pfx, supernet):
	"""Check if provided prefix is part of provided supernet or not.

	Args:
		pfx (str): subnet
		supernet (str): supernet

	Raises:
		Exception: if an input error occur

	Returns:
		bool: True if subnet is part of supernet else False
	"""    	
	if not isinstance(pfx, (str, IPv4)):
		raise Exception("INPUTERROR")
	if not isinstance(supernet, (str, IPv4)):
		raise Exception("INPUTERROR")
	if isinstance(supernet, str): supernet = addressing(supernet)
	if isinstance(pfx, str): pfx = addressing(pfx)
	if supernet.mask <= pfx.mask:
		supernet_bin = binsubnet(supernet.subnet)
		pfx_bin = binsubnet(pfx.subnet)
		if supernet_bin[0:supernet.mask] == pfx_bin[0:supernet.mask]:
			return True
	return False	


# ----------------------------------------------------------------------------
# Validation Class - doing subnet validation and version detection
# ----------------------------------------------------------------------------
class Validation():
	"""ip-subnet validation class, provide ipv4 or ipv6 subnet with "/" mask

	Args:
		subnet (str): ipv4 or ipv6 subnet with "/" mask

	"""    	

	def __init__(self, subnet):
		"""Initialise the validation.
		"""    		
		self.mask = None
		self.subnet = subnet
		self.version = self._version()
		self.validated = False
		self._check_ip_object()


	def _version(self):
		"""ip version number

		Returns:
			int: version number
		"""    		
		if STR.found(self.subnet, ":"):
			return 6
		elif STR.found(self.subnet, "."):
			return 4
		else:
			return 0

	def _check_ip_object(self):
		"""internal checking method

		Raises:
			Exception: _description_

		Returns:
			_type_: _description_
		"""    		
		object_map = {4: IPv4, 6: IPv6}
		func_map = {4: self.check_v4_input, 6: self.check_v6_input}
		if self.version in object_map:
			self.validated = func_map[self.version]()
			if not self.validated: return None
			self.ip_obj = object_map[self.version](self.subnet)
			self.validated = expand(self.ip_obj[0]) == expand(self.ip_obj.NetworkIP(False))

			if not self.validated:  return None
		else:
			raise Exception(_invalid_subnet(self.subnet))

	def check_v4_input(self):
		'''validation of v4 subnet
		'''
		# ~~~~~~~~~ Mask Check ~~~~~~~~~
		try:
			self.mask = self.subnet.split("/")[1]
		except:
			self.mask = 32
			self.subnet = self.subnet + "/32"
		try:			
			self.mask = int(self.mask)
			if not all([self.mask>=0, self.mask<=32]):
				raise Exception(f"Invalid mask length {self.mask}")
		except:
			raise Exception(f"Incorrect Mask {self.mask}")

		# ~~~~~~~~~ Subnet Check ~~~~~~~~~
		try:
			octs = self.subnet.split("/")[0].split(".")
			if len(octs) != 4:
				raise Exception(f"Invalid Subnet Length {len(octs)}")
			for i in range(4):
				if not all([int(octs[i])>=0, int(octs[i])<=255 ]):
					raise Exception(f"Invalid Subnet Octet {i}")
			return True
		except:
			raise Exception(f"Unidentified Subnet: {self.subnet}")

	def check_v6_input(self):
		'''validation of v6 subnet
		'''
		try:
			# ~~~~~~~~~ Mask Check ~~~~~~~~~
			self.mask = self.subnet.split("/")[1]
		except:
			self.mask = 128
			self.subnet = self.subnet + "/128"
		try:
			self.mask = int(self.mask)
			if not all([self.mask>=0, self.mask<=128]):
				raise Exception(f"Invalid mask length {self.mask}")
			
			# ~~~~~~~~~ Subnet ~~~~~~~~~
			sip = self.subnet.split("/")[0].split("::")
			
			# ~~~~~~~~~ Check Subnet squeezers ~~~~~~~~~
			if len(sip) > 2:
				raise Exception("Invalid Subnet, Squeezers detected > 1")
			
			# ~~~~~~~~~ Subnet Length ~~~~~~~~~
			lsip = sip[0].split(":")
			try:
				rsip = sip[1].split(":")
			except:
				rsip = []
			if len(lsip)+len(rsip) > 8:
				raise Exception(f"Invalid Subnet Length {len(lsip)+len(rsip)}")
			
			# ~~~~~~~~~ Validate Hextates ~~~~~~~~~
			for hxt in lsip+rsip:
				try:
					if hxt != '' :
						hex(int(hxt, 16))
				except:
					raise Exception(f"Invalid Hextate {hxt}")
			
			# ~~~~~~~~~ All Good ~~~~~~~~~
			return True

		except:
			raise Exception("Unidentified Subnet")

# --------------------------------------------------------------------------------------------------
# Parent IP class defining default methods for v4 and v6 objects
# --------------------------------------------------------------------------------------------------

@total_ordering
class IP():
	'''defines common properties and methods

	Raises:
		Exception: incorrect input

	Returns:
		IP: object

	Yields:
		IP: object
	'''

	def __init__(self, subnet):
		self.subnet = subnet
		spl_subnet = self.subnet.split("/")
		self.mask = int(spl_subnet[1]) if len(spl_subnet) > 1 else self.bit_length
		self.net = spl_subnet[0] if len(spl_subnet) > 0 else None
	def __hash__(self):
		try:
			return int(self)*self.mask
		except:
			raise Exception(f"UnhashableInput: {self.subnet}")
	def __str__(self): return self.subnet
	def __int__(self): return self._net_ip
	def __repr__(self): return self.subnet
	def __len__(self):  return self._bc_ip - int(self) + 1
	def __gt__(self, ip): return int(self) - ip._bc_ip > 0
	def __lt__(self, ip): return self._bc_ip - int(ip) < 0
	def __eq__(self, ip): 
		return (int(self) == int(ip) and self._bc_ip == ip._bc_ip )
	def __add__(self, n):
		'''add n-ip's to given subnet and return udpated subnet'''
		if isinstance(n, int):
			return self.n_thIP(n, False, "_")
		elif isinstance(n, IPv4):
			summary = get_summaries(self, n)
			if len(summary) == 1:
				return get_summaries(self, n)[0]
			else:
				raise Exception(
					"Inconsistant subnets cannot be added "
					"and >2 instances of IPv4/IPv6 Object add not allowed. please check inputs or "
					"Use 'get_summaries' function instead"
					)
	def __sub__(self, n): return self.n_thIP(-1*n, False, "_")
	def __truediv__(self, n): return self._sub_subnets(n)
	def __iter__(self): return self._subnetips()
	def __getitem__(self, n):
		if isinstance(n, int) and n < 0: n = len(self)+n
		try:
			return self.n_thIP(n, False)
		except:
			l = []
			for x in self._subnetips(n.start, n.stop):
				l.append(x)
			return tuple(l)
	def __contains__(self, pfx): return isSubset(pfx, self)

	@property
	def _net_ip(self): return bin2dec(binsubnet(self.NetworkIP()))
	@property
	def _bc_ip(self): return bin2dec(binsubnet(self.broadcast_address()))

	@property
	def hosts(self):
		for _ in self:
			yield _
	@property
	def host_count(self):
		return len(self)
	@property
	def is_host(self):
		return self.mask == self.bit_length
	@property
	def is_ip_interface(self):
		return self.is_host or self.ip_number > 0
	@property
	def is_ip_network(self):
		return self.ip_number == 0

	# get n-number of subnets of given super-net
	def _sub_subnets(self, n):
		_iplst = []
		for i1, x1 in enumerate(range(self.bit_length)):
			p = 2**x1
			if p >= n: break
		_nsm = self.mask + i1
		_nip = int(binsubnet(self.subnet_zero()), 2)
		_bcip = int(binsubnet(self.broadcast_address()), 2)
		_iis = (_bcip - _nip + 1) // p
		for i2, x2 in enumerate(range(_nip, _bcip+1, _iis)):
			_iplst.append(self.n_thIP(i2*_iis)+ "/" + str(_nsm))
		return tuple(_iplst)

	# yields IP Address(es) of the provided subnet
	def _subnetips(self, begin=0, end=0):
		_nip = int(binsubnet(self.subnet_zero()), 2)
		if end == 0:
			_bcip = int(binsubnet(self.broadcast_address()), 2)
		else:
			_bcip = _nip + (end-begin)
		for i2, x2 in enumerate(range(_nip, _bcip+1)):
			if begin>0:  i2 = i2+begin
			yield self.n_thIP(i2)

	@property
	def startsat_dec(self):
		return int(binsubnet(self.subnet_zero()), 2)
	@property
	def endsat_dec(self):
		return int(binsubnet(self.broadcast_address()), 2)
	@property
	def range(self):
		return range(self.startsat_dec, self.endsat_dec+1)

	def is_subset(self, summary):
		return isSubset(self, summary)


# ----------------------------------------------------------------------------
# IP Subnet (IPv6) class 
# ----------------------------------------------------------------------------

class IPv6(IP):
	'''IPv6 object

	Args:
		subnet (str): ipv6 subnet with mask.
	'''

	version = 6
	bit_length = 128

	# Object Initializer
	def __init__(self, subnet=''):
		"""initialize the IPv6 object for provided v6 subnet
		"""    		
		super().__init__(subnet)
		self._network_ip()
		self.__actualv6subnet = False				# breaked subnet expanded
		self._network_address_bool = False			# Subnet zero available/not

	def len(self): 
		"""Subnet size

		Returns:
			int: count of ip in this subnet 
		"""	
		return len(self)

	# ------------------------------------------------------------------------
	# Private Methods
	# ------------------------------------------------------------------------

	# update Subnet to actual length / expand zeros 
	def _to_actualsize(self):
		self.subnet = expand(self.subnet)
		# if not self.subnet: return False
		return self.subnet

	# IP Portion of Input
	def _network_ip(self):
		try:
			self.network = self.subnet.split("/")[0]
			return self.network
		except:
			raise Exception(f"NoValidIPv6SubnetDetected: {self.subnet}")
			return None

	# Padding subnet with ":0" or ":ffff"
	@staticmethod
	def _pad(padwhat='0', counts=0):
		s = ''
		for x in range(counts):
			s = s + ":" + padwhat
		return s

	# Return a specific Hextate (hexTnum) from IPV6 address
	def _get_hext(self, hexTnum, s=''):	return get_hext(self.subnet, hexTnum, s)

	# Return Number of Network Hextates (hxts) from IPV6 address
	def _get_hextates(self, hxts=1, s=''):
		ox = ''
		for o in range(1, hxts+1):
			ox = STR.string_concate(ox, self._get_hext(o, s=s), conj=':')
		return ox+":"

	# NETWORK / BC Address Calculation : addtype = 'NET' , 'BC'
	def _endpoint(self, addtype='NET'):
		self._to_actualsize()
		if self.mask != '' and self.mask<128:	 # Non host-only subnets
			x = 0 if addtype == 'NET' else -1
			padIP = '0' if addtype == 'NET' else 'ffff'
			(asilast, avs) = ([], [])
			fixedOctets = self.mask//16

			## get full list of available subnets in selected Hexate.
			while x < 65536:	
				asilast.append(x)
				x = x + (2**(16-(self.mask-((fixedOctets)*16))))

			## check avlbl subnet and choose less then given one.
			for netx in asilast:		
				avs.append(self._get_hextates(fixedOctets)  
										+ str(hex(netx))[2:])
				if addtype =='BC':
					last_subnet = avs[-1]
				if int(self._get_hext(fixedOctets+1), 16) < netx:
					break
				if addtype =='NET':
					last_subnet = avs[-1]

			## Return subnet by padding zeros.
			self.fixedOctets = fixedOctets
			nt = last_subnet+self._pad(padIP, 7-fixedOctets)
			if nt[0] == ":": nt = nt[1:]
			return nt

		else:									# host-only subnet
			return self.network

	def _add_ip_to_network_address(self, num=0, _=''):
		'''Adds num of IP to Network IP and return address'''
		self._network_address
		s = self._subnet_zero
		if _ != '':
			s = self.subnet
		_7o = self._get_hextates(7, s)
		_8o = int(self._get_hext(8, s), 16) + num
		return _7o + str(hex(_8o)[2:])

	@property
	def _broadcast_address(self): return self._endpoint(addtype='BC')
	@property
	def _network_address(self):
		'''Returns only NETWORK ADDRESS for given subnet'''
		if not self._network_address_bool:
			self._subnet_zero = self._endpoint(addtype='NET')
			self._network_address_bool = True
		return self._subnet_zero
	NetworkAddress = _network_address


	# ------------------------------------------------------------------------
	# Public Methods 
	# ------------------------------------------------------------------------

	def get_hext(self, hexTnum): 
		"""get a specific Hextate value from IPV6 address
		same as: getHext

		Args:
			hexTnum (int): hextate number

		Returns:
			str: hextate value
		"""		
		return self._get_hext(hexTnum)
	getHext = get_hext

	def subnet_zero(self, withMask=True):
		"""Network Address (subnet zero) with/without mask for given subnet
		same as: NetworkIP

		Args:
			withMask (bool, optional): return with mask. Defaults to True.

		Returns:
			str: Network Address
		"""    		
		if withMask :
			return self._network_address + "/" + str(self.mask)
		else:
			return self._network_address
	NetworkIP = subnet_zero

	def broadcast_address(self, withMask=True):
		"""Broadcast Address with/without mask for given subnet
		same as: BroadcastIP

		Args:
			withMask (bool, optional): return with mask. Defaults to True.

		Returns:
			str: Broadcast Address
		"""
		if withMask :
			return self._broadcast_address + "/" + str(self.mask)
		else:
			return self._broadcast_address
	BroadcastIP = broadcast_address

	def n_thIP(self, n=0, withMask=False, _=''):
		"""n-th IP with/without mask from given subnet

		Args:
			n (int, optional): n-th ip. Defaults to 0.
			withMask (bool, optional): return with mask. Defaults to False.

		Returns:
			str: nth IP Address string
		"""
		ip = self._add_ip_to_network_address(n, _)
		mask = self.decimalMask
		return ip+"/"+mask if withMask else ip

	@property
	def expanded(self):
		"""expanded format of ipv6 address.

		Returns:
			str: expanded format ipv6 address.
		"""		
		return expand(self.subnet)

	def shrinked(self, withMask=True):
		"""shrinked format of ipv6 address.

		Returns:
			str: shrinked format ipv6 address.
		"""		
		return shrink(self.subnet_zero(withMask=True), withMask=withMask)

	@property
	def decimalMask(self):
		'''decimal mask of given subnet
		same as: decmask
		'''
		return str(self.mask)
	decmask = decimalMask

	## - NA - for IPv6 ##
	@property
	def binmask(self): 
		"""Not Implemented for IPv6 """		
		return None
	@property
	def invmask(self): 
		"""Not Implemented for IPv6 """		
		return None
	def ipdecmask(self, n=0): 
		"""nth ip with decimal mask"""
		return self.n_thIP(n, True)
	def ipbinmask(self, n=0): 
		"""Not Implemented for IPv6 """		
		return None
	def ipinvmask(self, n=0): 
		"""Not Implemented for IPv6 """		
		return None


# ----------------------------------------------------------------------------
# IPv4 Subnet (IPv4) class 
# ----------------------------------------------------------------------------
class IPv4(IP):
	'''IPv4 object
	'''

	version = 4
	bit_length = 32

	# ------------------------------------------------------------------------
	# Private methods / Properties
	# ------------------------------------------------------------------------

	# binary mask return property
	@property
	def _binmask(self):
		try:
			pone ='1'*self.mask
			pzero = '0'*(32-self.mask)
			return pone+pzero
		except:
			pass

	# Inverse mask return property
	@property
	def _invmask(self):
		try:
			pone ='0'*self.mask
			pzero = '1'*(32-self.mask)
			return pone+pzero
		except:
			pass

	@staticmethod
	def _pad_zeros(bins): 
		return '0'*(34 - len(str(bins)))+bins[2:]
	@staticmethod
	def _octets_bin2dec(binnet): 
		return  [bin2dec(binnet[x:x+8]) for x in range(0, 32, 8) ]
	def _bin_and(self, binone, bintwo):
		return self._pad_zeros(bin(int(binone.encode('ascii'), 2) & int(bintwo.encode('ascii'), 2) ))
	def _bin_or(self, binone, bintwo):
		return self._pad_zeros(bin(int(binone.encode('ascii'), 2) | int(bintwo.encode('ascii'), 2) ))

	# ------------------------------------------------------------------------
	# Available Methods & Public properties of class
	# ------------------------------------------------------------------------

	@property
	def ip_number(self):
		"""distance of provided ip from its network number

		Returns:
			int: difference of ips from provided ip to its network number
		"""		
		selfinteger = int(binsubnet(str(self)).encode('ascii'), 2)
		return selfinteger - self.network_number_int

	@property
	def network_number_int(self):
		return int(binsubnet(str(IPv4(self.NetworkIP()))).encode('ascii'), 2)

	@property
	def broadcast_number_int(self):
		return int(binsubnet(str(IPv4(self.BroadcastIP()))).encode('ascii'), 2)


	def expand(self, new_mask):
		"""expand the provided subnet to given bigger size subnet. provided subnet mask `new_mask` should be less in number to the existing subnet mask in such case.

		Args:
			new_mask (int): subnet mask to which subnet to be expanded.

		Returns:
			str: expanded subnet string value
		"""		
		if not isinstance(new_mask, int):
			raise(f"Invalid mask provided {new_mask}.  Expected integer got {type(new_mask)}")
		if new_mask < self.mask:
			_ns = IPv4(self.subnet_zero(withMask=False) + f"/{new_mask}")
			return _ns.subnet_zero()
		return self.subnet_zero()

	def subnet_zero(self, withMask=True):
		"""Network IP Address (subnet zero) of subnet from provided IP/Subnet.
		same as: NetworkIP

		Args:
			withMask (bool, optional): return with mask. Defaults to True.

		Returns:
			str: Network address
		"""    		
		try:
			s = binsubnet(self.subnet)
			bm = self._binmask
			net = LST.list_to_octet(self._octets_bin2dec(self._bin_and(s, bm )))
			if withMask :
				return net + "/" + str(self.mask)
			else:
				return net
		except:
			pass
	NetworkIP = subnet_zero

	def broadcast_address(self, withMask=False):
		"""Broadcast IP Address of subnet from provided IP/Subnet
		same as: BroadcastIP

		Args:
			withMask (bool, optional): return with mask. Defaults to False.

		Returns:
			str: broadcast ip
		"""    		
		try:
			s = binsubnet(self.subnet)
			im = self._invmask
			bc = LST.list_to_octet(self._octets_bin2dec(self._bin_or(s, im )))
			if withMask :
				return bc + "/" + str(self.mask)
			else:
				return bc
		except:
			pass
	BroadcastIP = broadcast_address

	def n_thIP(self, n=0, withMask=False, _='', summary_calc=False):
		"""n-th IP Address of subnet from provided IP/Subnet

		Args:
			n (int, optional): number of ip. Defaults to 0.
			withMask (bool, optional): return with mask. Defaults to False.

		Raises:
			Exception: for address out of range

		Returns:
			str: nth ip address
		"""
		s = binsubnet(self.subnet)
		if _ == '':
			bm = self._binmask
			addedbin = self._pad_zeros(bin(int(self._bin_and(s, bm), 2)+n))
		else:
			addedbin = self._pad_zeros(bin(int(s.encode('ascii'), 2 )+n))

		if (any([addedbin > binsubnet(self.broadcast_address()), 
				addedbin < binsubnet(self.NetworkIP())]) and 
			not summary_calc
			):
			raise Exception("Address Out of Range")

		else:
			ip = LST.list_to_octet(self._octets_bin2dec(addedbin))
			if withMask :
				return ip + "/" + str(self.mask)
			else:
				return ip

	@property
	def decmask(self):
		'''Decimal Mask from provided IP/Subnet - Numeric/Integer'''
		return self.mask
	decimalMask = decmask

	@property
	def binmask(self):
		'''Binary Mask from provided IP/Subnet'''
		return LST.list_to_octet(self._octets_bin2dec(self._binmask))

	@property
	def invmask(self):
		'''Inverse Mask from provided IP/Subnet'''
		return LST.list_to_octet(self._octets_bin2dec(self._invmask))

	def ipdecmask(self, n=0):
		"""IP with Decimal Mask for provided IP/Subnet,

		Args:
			n (int, optional): n-th ip of subnet will appear in output if provided. Defaults to 0.

		Raises:
			Exception: invalid input

		Returns:
			str: ipaddress/mask
		"""    		
		try:
			return self[n] + "/" + str(self.mask)
		except:
			raise Exception(f'Invalid Input : detected')

	def ipbinmask(self, n=0):
		"""IP with Binary Mask for provided IP/Subnet,

		Args:
			n (int, optional): n-th ip of subnet will appear in output if provided,. Defaults to 0.

		Raises:
			Exception: invalid input

		Returns:
			str: ip_address subnet_mask
		"""    		
		try:
			return self[n] + " " + self.binmask
		except:
			raise Exception(f'Invalid Input : detected')

	ipnetmask = ipbinmask

	def ipinvmask(self, n=0):
		"""IP with Inverse Mask for provided IP/Subnet,

		Args:
			n (int, optional): n-th ip of subnet will appear in output if provided. Defaults to 0.

		Raises:
			Exception: invalid input

		Returns:
			str: ip_address inverse_mask
		"""    		
		try:
			return self[n] + " " + self.invmask
		except:
			raise Exception(f'Invalid Input : detected')

	def to_decimal(self):
		"""decimal number of subnet number

		Returns:
			int: integer/decimal value
		"""		
		return bin2dec(binsubnet(self.ipdecmask()))

	@property
	def size(self):
		"""number of ips available in subnet

		Returns:
			int: number of ips (subnet size)
		"""		
		return 2**(32-int(self.mask))

	def ipn(self, ip):
		"""get the ip number for provided ip address in the current subnet

		Args:
			ip (str): ip address

		Returns:
			int: ip number
		"""		
		if isinstance(ip, str):
			child = addressing(ip)
		return child.to_decimal() - self.to_decimal()

	def get_octet(self, o):
		"""get the desired octet for subnet

		Args:
			o (int): octet number

		Returns:
			str: octet number
		"""    		
		return ipv4_octets(self)['octets'][o-1]


# ------------------------------------------------------------------------------
# Routes Class
# ------------------------------------------------------------------------------
class Routes(object):
	"""Routes Object
	Either one input is require (route_list, route_file)

	Args:
		hostname (str): device hostname
		route_list (list, optional): cisco sh route command in list format. Defaults to None.
		route_file (str, optional): text file of sh route output. Defaults to None.
	"""    	


	def __init__(self, hostname, route_list=None, route_file=None):
		"""Initialize Route object
		"""    		
		if route_file != None: route_list = IO.file_to_list(route_file)
		self.__parse(route_list, hostname)

	def __getitem__(self, key):
		return self.routes[key]

	def __iter__(self):
		for k, v in self.routes.items():
			yield (k, v)

	@property
	def reversed_table(self):
		"""reversed routes

		Yields:
			tuple: route, route_attributes
		"""
		for k, v in reversed(self.routes.items()):
			yield (k, v)

	@property
	def routes(self):
		"""routes with its name"""
		return self._op_items

	def get_prefix_desc(self, prefix):
		"""prefix description if available or returns it for default route

		Args:
			prefix (str): prefix to check

		Raises:
			Exception: input error

		Returns:
			str: prefix remark/description if any
		"""    		
		pfxlst = []
		if isinstance(prefix, str):
			x = self.__check_in_table(addressing(prefix))[1]
			try:
				pfxlst.append(self[x])
				return pfxlst[0]
			except:
				print("[-] prefixesNotinAnySubnet: Error")
				return None
		elif isinstance(prefix, IPv4):
			x = self.__check_in_table(prefix.subnet)
			pfxlst.append(self[x])
		elif isinstance(prefix, (list, tuple, set)):
			for p in prefix:
				px = self.get_prefix_desc(p)
				if px:
					pfxlst.append(px)
		else:
			raise Exception("[-] INPUTERROR")
		if len(set(pfxlst)) == 1:
			return pfxlst[0]
		else:
			print("[-] prefixesNotinSamesubnet: Error")

	def inTable(self, prefix):
		"""check if prefix is in routes table, return for default-route otherwise

		Args:
			prefix (str): prefix to check

		Returns:
			bool: prefix in table or not
		"""    		
		return self.__check_in_table(prefix)[0]

	def outerPrefix(self, prefix):
		"""check and return parent subnet of prefix in routes table, default-route otherwise

		Args:
			prefix (str): prefix to check

		Returns:
			str: matching prefix/supernet
		"""    		
		return self.__check_in_table(prefix)[1]

	######################### LOCAL FUNCTIONS #########################

	# Helper for inTable and outerPrefix
	def __check_in_table(self, prefix):
		if not isinstance(prefix, (str, IPv4)):
			raise Exception("INPUTERROR")
		for k, v in self.reversed_table:
			if k == '0.0.0.0/0': continue
			if isSubset(prefix, k):
				return (True, k)
				break
		return (False, '0.0.0.0/0')

	# set routes in dictionary/ parser
	def __parse(self, route_list, hostname):
		headers = (
		"L - local", "C - connected", "S - static", "R - RIP", "M - mobile", "B - BGP",
		"D - EIGRP", "EX - EIGRP external", "O - OSPF", "IA - OSPF inter area", 
		"N1 - OSPF NSSA external type 1", "N2 - OSPF NSSA external type 2",
		"E1 - OSPF external type 1", "E2 - OSPF external type 2", "V - VPN",
		"i - IS-IS", "su - IS-IS summary", "L1 - IS-IS level-1", "L2 - IS-IS level-2",
		"ia - IS-IS inter area", "* - candidate default", "U - per-user static route",
		"o - ODR", "P - periodic downloaded static route", "+ - replicated route",
		"Gateway of last resort"
		)
		op_items = OrderedDict()
		for line in route_list:
			if STR.is_blank_line(line): continue
			if STR.is_hostname_line(line, hostname): continue
			if STR.find_any(line, headers): continue
			if isSplittedRoute(line) == 0:
				spl = line.strip()
				continue
			if isSplittedRoute(line) == -1:
				line = spl + ' ' + line
			spl = line.split(",")
			if line.find('0.0.0.0 0.0.0.0') > -1:
				op_items['0.0.0.0/0'] = STR.replace_dual_and_split(spl[1])[-1].strip()
				continue
			route = STR.replace_dual_and_split(spl[0])[1]
			try:
				routeMask = binsubnet(STR.replace_dual_and_split(spl[0])[2]).count('1')
			except:
				print(spl)
			routeDesc = STR.replace_dual_and_split(spl[-1])[-1]
			op_items[route + '/' + str(routeMask)] = routeDesc.strip()
		self._op_items = op_items


# ----------------------------------------------------------------------------
# Prefixes summarization class 
# ----------------------------------------------------------------------------

MAX_RECURSION_DEPTH = 100		# default recursion depth, increase if exceeding and need to go deep more.
class Summary(IPv4):
	'''Defines Summaries of prefixes
	DEPRYCATED CLASS -- will be removed in future version..
	USE `addressing.summary.Aggregate` instead for better performance.
	'''

	# __slots__ = ['networks', 'summaries', 'del_eligibles','mask','first','second',
	# 	'first_len','second_len','total']

	def __init__(self, *args):		
		"""initialize object with provided args=prefixes
		"""
		self.networks = set()
		args = sorted_v4_addresses(args)
		for arg in args:
			if isinstance(arg, str):
				if arg.strip():
					arg=IPv4(arg)
			self.networks.add(arg)
		self.summaries = []
		self.networks = sorted(self.networks)
		self._validate_and_update_networks()

	def __str__(self):
		return str(self.prefixes)

	@property
	def prefixes(self):
		"""set of summary addresses

		Returns:
			set: summaries
		"""    		
		for pfx in self.summaries:
			if isinstance(pfx, str): pfx = IPv4(pfx)
		return set(self.summaries)

	# provided networks validation, remove non-validated networks.
	def _validate_and_update_networks(self):
		for network in self.networks:
			if not Validation(str(network)).validated:
				print(f"[-] InvalidSubnetDetected-Removed: {network}")
				self.networks.remove(network)

	# kick
	def calculate(self):
		"""calculate summaries for provided networks
		"""
		prev_network = None
		for network in self.networks:
			_sumy = self.summary(prev_network, network)
			prev_network = _sumy if _sumy is not None else network
			if _sumy is not None: 
				# prev_network = _sumy
				if isinstance(prev_network, str): 
					_sumy = IPv4(_sumy)
					prev_network = IPv4(prev_network)
				self.summaries.append(str(_sumy))
			else:
				self.summaries.append(str(network))
		self.summaries = list(set(self.summaries))
		self.calc_subset_prefixes()
		self.remove_subset_prefixes()

	def remove_subset_prefixes(self):
		"""revmoes subset of prefixes from already calculated summary
		"""		
		for pfx in self.del_eligibles:
			self.summaries.remove(pfx)

	def calc_subset_prefixes(self):
		"""calculates subbsets of prefixes to identify delete eligibles
		"""		
		del_eligibles = set()
		for i, pfx in enumerate(self.summaries):
			for j, varify_pfx in enumerate(self.summaries):
				if j == i: continue
				if str(pfx) != str(varify_pfx) and isSubset(pfx, varify_pfx):
					del_eligibles.add(pfx)
		self.del_eligibles = del_eligibles

	def summary(self, s1, s2):
		"""summary of given two network addresses s1 and s2

		Args:
			s1 (IPv4): IPv4 object1
			s2 (IPv4): IPv4 object2

		Returns:
			_type_: _description_
		"""		
		if s2 is None: return s1
		if s1 is None: return s2
		if self._are_equal(s1, s2): return s1
		big_subnet = self._is_any_subset(s1, s2)
		if big_subnet: return big_subnet
		self._sequnce_it(s1, s2)
		self._local_vars()
		if not self._contigious() or not self._immidiate(): return None
		summary_ip = self.first.NetworkIP(False)+"/"+str(self.mask)
		return summary_ip if Validation(summary_ip).validated else None

	# Order the subnet sequencially.
	def _sequnce_it(self, s1, s2):
		if int(binsubnet(s1.NetworkIP()), 2 ) > int(binsubnet(s2.NetworkIP()), 2 ):
			(first, second) = (s2, s1) 
		else: 
			(first, second) = (s1, s2)
		self.first, self.second = first, second

	# defining some local variables
	def _local_vars(self):
		# ---------- set local vars ------------------
		self.first_len = len(self.first)
		self.second_len = len(self.second)	
		self.total = 2*self.first_len if self.first_len >= self.second_len else 2*self.second_len
		self.mask = 32 - len(bin(self.total-1)[2:])			# tantative summary mask
		# --------------------------------------------

	# are provided two prefixes equal or not, check boolean
	def _are_equal(self, s1, s2): return s1.mask == s2.mask and s1.NetworkIP() == s2.NetworkIP()

	# is s1 part of s2 ?
	def _is_any_subset(self, s1, s2):
		(big_subnet, small_subnet) = (s2, s1) if s1.mask > s2.mask else (s1, s2)
		is_part = False
		for power in range(1, 33):
			no_of_subnets = (2**power)
			try:
				portions = big_subnet/no_of_subnets
			except ValueError:
				break
			if small_subnet.NetworkIP() in portions:
				is_part = True
				break
		return big_subnet if is_part else None

	# a condition
	def _contigious(self):
		# condition 1 - next ip of subnet 1 should be network ip of subnet 2 / Verfications
		return self.first.n_thIP(self.first_len, summary_calc=True) == self.second.NetworkIP(False)

	# a more condition
	def _immidiate(self):
		# condition 2 - length subnet 1 + lenght subnet 2 == bc ip of subnet 2
		return self.first.n_thIP(self.total-1, summary_calc=True) == self.second.broadcast_address()

# =====================================================================================================

class Allocations():
	"""Store Allocations of subnets
	"""	

	def __init__(self):
		self.ranges = []
		self.what_list = []
		self.assignment_dict = {}
		self.increamental = 0
		self.allocation_type = 'additive'   ## options: 'comparative', 'override'
		self.display_warning = True


	def add_prefix(self, pfx, forwhat=None):
		"""add subnet to allocation. 
		provide additional information forwhat this prefix is allocated

		Args:
			pfx (str, IPv4): string or IPv4 subnet object
			forwhat (str): additional information of range (defaults to None, will be increamental)
		"""
		if forwhat is None:
			self.increamental += 1
			forwhat = self.increamental
		if isinstance(pfx, str):
			pfx = IPv4(pfx)
		start = pfx.to_decimal()
		cri = self.check_range_in(range(start, start + len(pfx)))
		if cri:
			conflict = _get_subnet(cri[0], cri[-1]-cri[0]+1)
			if self.display_warning: print(f"[-] Prefix {pfx} is already allocated, or it has clash with existing assignment {conflict}")
		else:
			self.add(range(start, start + len(pfx)), forwhat)

	def add(self, rng, forwhat):
		"""add decimal range address to allocation. 
		provide additional information forwhat this prefix is allocated

		Args:
			rng (range): decimal range object
			forwhat (str): additional information of range
		"""		
		if forwhat in self.assignment_dict:
			if self.allocation_type == 'additive':
				self.ranges.append(rng)
				if isinstance(self.assignment_dict[forwhat], str):
					self.assignment_dict[forwhat] = {self.assignment_dict[forwhat], }
				self.assignment_dict[forwhat].add(self.get_subnet(rng))
			elif self.allocation_type == 'override':
				self.ranges.append(rng)
				self.assignment_dict[forwhat] = self.get_subnet(rng)
			elif self.allocation_type == 'comparative':
				# print( int(self.assignment_dict[forwhat]) ,   int(self.get_subnet(rng).split("/")) )
				if isinstance(self.assignment_dict[forwhat], str):
					if IPv4(self.assignment_dict[forwhat]).size >= IPv4(self.get_subnet(rng)).size:
						if self.display_warning: print(f"[-] Subneet already found same or bigger, comparative allocations will not add")
					else:
						self.ranges.append(rng)
						self.assignment_dict[forwhat] = {self.assignment_dict[forwhat], self.get_subnet(rng)}
				elif isinstance(self.assignment_dict[forwhat], set):
					for ad_fw in self.assignment_dict[forwhat]:
						if IPv4(ad_fw).size >= IPv4(self.get_subnet(rng)).size:
							if self.display_warning: print(f"[-] Subneet already found same or bigger, comparative allocations will not add")
						else:
							self.assignment_dict[forwhat].add(self.get_subnet(rng))

		else:
			self.ranges.append(rng)
			self.what_list.append(forwhat)
			self.assignment_dict[forwhat] = self.get_subnet(rng)

	def check_ip_in(self, ip):
		"""verify if provided ip is falling in the already allocated range(s)

		Args:
			ip (str): single ip address

		Returns:
			bool, range: if found returns matched range, else False
		"""		
		for range_x in  self.ranges:
			if ip in range_x:
				return range_x
		return False

	def check_range_in(self, rng):
		"""verify if provided range is part of any allocated range(s)

		Args:
			rng (range): decimal range of ips 

		Returns:
			bool, range: if found returns matched range, else False
		"""		
		for range_x in self.ranges:
			if is_overlap(rng, range_x):
				return range_x
		return False

	@staticmethod
	def get_subnet(rng):
		"""get subnet/mask information for the provided range

		Args:
			rng (range): decimal range of ips

		Returns:
			str: string representation of subnet/mask for given range
		"""		
		sr = [x for x in rng]
		for x in range(1048576):
			try:
				return _get_subnet(sr[0]+x, sr[-1]-sr[0]+1)
			except:
				pass



class Subnet_Allocate():
	"""Allocate a subnet

	Args:
		proposed (str): initial based / proposed ip
		forwhat (str): additional information of prefix
	"""	

	def __init__(self, proposed, forwhat):
		"""instance initializer
		"""		
		self.proposed = proposed
		self.forwhat = forwhat
		self.get_attributes()

	def get_attributes(self):
		"""initial attributes setting
		"""		
		self.subnet = IPv4(self.proposed)
		self.decimal = self.subnet.to_decimal()
		self.subnet_size = self.subnet.size
		self.subnet_zero = self.subnet.subnet_zero()
		self.subnet_range = range(self.decimal, self.decimal+self.subnet_size)

	def verification(self, Alloc):
		"""verifications to check range(s)

		Args:
			Alloc (Allocations): allocations object
		"""		
		self.checked_range = self.check_range(Alloc)
		Alloc.add(self.checked_range, self.forwhat)

	def check_range(self, Alloc):
		"""check range against already allocated ranges

		Args:
			Alloc (Allocations): allocations object

		Returns:
			range: verify if subnet-range is already part of any range
		"""		
		current_range_in = Alloc.check_range_in(self.subnet_range)
		if not current_range_in:
			return self.subnet_range
		else:
			sr = [x for x in current_range_in]
			self.subnet_range = range(sr[-1]+1, sr[-1]+1+self.subnet_size)
			return self.check_range(Alloc)

	def get_subnet(self):
		"""get subnet/mask information for the checked range

		Returns:
			str: string representation of subnet/mask for given range
		"""	
		sr = [x for x in self.checked_range]
		for x in range(1048576):
			try:
				return _get_subnet(sr[0]+x, self.subnet_size)
			except:
				pass


	def get_nxt_subnet_decimal(self):
		"""get next available ip in decimal format

		Returns:
			str: dotted decimal format next available ip
		"""		
		sr = [x for x in self.checked_range]
		return dec2dotted_ip(sr[-1]+1)


class Allocate(object):
	"""Allocation series

	Args:
		size_wise_dict (dict): size wise allocation requirements dictionary
		base_ip (str): sample base ip
		what_list_dict_key (str, optional): additional information of prefix. Defaults to None.
	"""	

	def __init__(self, size_wise_dict, base_ip, what_list_dict_key=None, Alloc=None, iterate_base_ip=False):
		self.size_wise_dict = size_wise_dict
		self.base_ip = base_ip
		self.iterate_base_ip = iterate_base_ip
		self.what_list_dict_key = what_list_dict_key
		if Alloc is None:
			self.Alloc = Allocations()
		else:
			self.Alloc = Alloc
		self.rearrange_size()

	def rearrange_size(self):
		"""rearrange size wise dictionary in reversed order bigger to smaller
		"""		
		self.ssize = reversed(sorted(self.size_wise_dict.keys()))

	def subnet_allocate(self, size, what):
		"""allocate subnet for given size and prefix information

		Args:
			size (int): decimal ip
			what (str): information of prefix
		"""		
		msk = str(subnet_size_to_mask(size))
		SA = Subnet_Allocate(self.base_ip + "/" + msk, what)
		SA.verification(self.Alloc)
		if self.iterate_base_ip:
			self.base_ip = SA.get_nxt_subnet_decimal()

	def go_thru_each_section(self, size, size_dict_values):
		"""repeate thru each section (if any) to allocate subnets.

		Args:
			size (int): decimal ip
			size_dict_values (dict, set, list, tuple, str, int): input information on prefix(es)

		Raises:
			Exception: _description_
		"""		
		if isinstance(size_dict_values, dict):
			if not self.what_list_dict_key:
				raise Exception('what_list_dict_key is mandatory when providing nested size_wise_dict')
			for k, v in size_dict_values.items():
				if k != self.what_list_dict_key: continue
				for what in v:
					self.subnet_allocate(size, what)
		elif isinstance(size_dict_values, (set, list, tuple)):
			for what in size_dict_values:
				self.subnet_allocate(size, what)
		elif isinstance(size_dict_values, (str, int)):
			self.subnet_allocate(size, size_dict_values)

	def start(self):
		"""start executions for all size wise dictionary informations
		"""		
		for size in self.ssize:
			for s, size_dict_values in self.size_wise_dict.items():
				if s != size: continue
				self.go_thru_each_section(size, size_dict_values)

	@property
	def assignments(self):
		"""return allocations/assignments dictionary

		Returns:
			dict: allocated subnet/prefixes
		"""		
		return self.Alloc.assignment_dict

# =====================================================================================================


def ipv4_octets(ip):
	"""get octets in a list for provided ip/subnet

	Args:
		ip (str): ip/mask

	Returns:
		dict: dictionary with octets list and mask
	"""	
	if not ip: return {}
	fs = str(ip).strip().split("/")
	octets = fs[0].split(".")
	try:
		mask = int(fs[1])
	except:
		mask = 32
	return { 'octets': octets, 'mask':mask }

# sorted dataframe based on ip octets
def _get_sorted_dataframe(dic, ascending, byip=True, bymask=False):
	df = pd.DataFrame(dic)
	for x in range(4):
		df[x] = pd.to_numeric(df[x], errors='coerce')
	df['mm'] = pd.to_numeric(df['mm'], errors='coerce')
	byip = not bymask
	if byip:
		df.sort_values([0,1,2,3,'mm'], inplace=True, ascending=ascending)
	else:
		df.sort_values(['mm', 0,1,2,3], inplace=True, ascending=ascending)
	return df

# converts octets list to dictionary
def _convert_list_to_dict(lst):
	dic,mm = {0:[], 1:[], 2:[], 3:[]},[]
	for oNm in lst:
		if not oNm: continue
		mm.append(oNm['mask'])
		for n in range(4):
			dic[n].append(oNm['octets'][n])
	dic['mm'] = mm
	return dic

# join list format octet back to string in dataframe
def _join_octets_fr_df(df):
	for x in range(4):
		df[x] = df[x].apply(lambda x: str(x))
	return [ ".".join([row[n] for n in range(4)]) + "/" + str(row['mm']) for k, row in df.iterrows() ]


def sorted_v4_addresses(args, ascending=True):
	"""sort IPv4 addresses (subnets)

	Args:
		args (list): list of addresses/subnets
		ascending (bool or list of bool, optional): Sort ascending vs. descending. Specify list for multiple sort orders. If this is a list of bools, must match the length of the by. Defaults to True.

	Returns:
		list: sorted list
	"""	
	return _join_octets_fr_df(
		_get_sorted_dataframe(
			_convert_list_to_dict([ ipv4_octets(ip) for ip in args ]), ascending=ascending )
		)


def sort_by_size(args):
	"""sort IPv4 addresses (sort by mask)

	Args:
		args (list): list of addresses/subnets

	Returns:
		list: sorted list
	"""	
	return _join_octets_fr_df(
		_get_sorted_dataframe(
			_convert_list_to_dict([ ipv4_octets(ip) for ip in args ]),ascending=True, bymask=True )
		)

# ----------------------------------------------------------------------------
# Main Function
# ----------------------------------------------------------------------------
if __name__ == '__main__':
	pass
# END
# ----------------------------------------------------------------------------
