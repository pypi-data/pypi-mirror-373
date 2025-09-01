
import pandas as pd
from dataclasses import dataclass, field
from nettoolkit.addressing import addressing, dec2dotted_ip, inv_subnet_size_to_mask, IPv4, isSubset
from nettoolkit.nettoolkit_db import sort_dataframe_on_subnet, read_xl_all_sheet, read_an_xl_sheet

# =========================================================================================== 
# Static Global Variable
# =========================================================================================== 
# MASK_RANGE = {2**x:{'net':x , 'host':32-x} for x in range(32)}
MASK_RANGE = {
 1: {'host': 32, 'net': 0},
 2: {'host': 31, 'net': 1},
 4: {'host': 30, 'net': 2},
 8: {'host': 29, 'net': 3},
 16: {'host': 28, 'net': 4},
 32: {'host': 27, 'net': 5},
 64: {'host': 26, 'net': 6},
 128: {'host': 25, 'net': 7},
 256: {'host': 24, 'net': 8},
 512: {'host': 23, 'net': 9},
 1024: {'host': 22, 'net': 10},
 2048: {'host': 21, 'net': 11},
 4096: {'host': 20, 'net': 12},
 8192: {'host': 19, 'net': 13},
 16384: {'host': 18, 'net': 14},
 32768: {'host': 17, 'net': 15},
 65536: {'host': 16, 'net': 16},
 131072: {'host': 15, 'net': 17},
 262144: {'host': 14, 'net': 18},
 524288: {'host': 13, 'net': 19},
 1048576: {'host': 12, 'net': 20},
 2097152: {'host': 11, 'net': 21},
 4194304: {'host': 10, 'net': 22},
 8388608: {'host': 9, 'net': 23},
 16777216: {'host': 8, 'net': 24},
 33554432: {'host': 7, 'net': 25},
 67108864: {'host': 6, 'net': 26},
 134217728: {'host': 5, 'net': 27},
 268435456: {'host': 4, 'net': 28},
 536870912: {'host': 3, 'net': 29},
 1073741824: {'host': 2, 'net': 30},
 2147483648: {'host': 1, 'net': 31}
}

# =========================================================================================== 
# Functions
# =========================================================================================== 

# recursive, club adjascent ranges and split diverse ones. 
def _split_continuous_ranges(int_ranges):
	ranges = []
	for start, end in int_ranges:
		max_mask_range = max(_get_range_parts(end-start+1))
		ip = dec2dotted_ip(start)
		for _ in reversed(MASK_RANGE):
			if _ > max_mask_range: continue
			i = addressing( ip + "/" + str(MASK_RANGE[_]['host']))
			if i.NetworkIP() == str(i):
				break
		ranges.append( (i.network_number_int, i.broadcast_number_int) )
		if i.network_number_int == start and i.broadcast_number_int == end:
			continue
		ranges.extend( _split_continuous_ranges([(i.broadcast_number_int+1, end),]))
	return ranges

# get the mask ranges for provided differences.
def _get_range_parts(diff):
	mask_ranges = set() 
	for k in sorted(MASK_RANGE.keys()):
		if k > diff: break
		mask_ranges.add(k)
	return mask_ranges

def get_masks(lst, diff):
	l = sorted(lst)
	if diff == l[-1]: return {l[-1], }
	for x in l[:-1]:
		if l[-1] + x == diff:
			return {l[-1], x}
	return get_masks(l[:-1], diff-l[-1]) | {l[-1]}

# =========================================================================================== 
# Aggregation Class
# =========================================================================================== 
@dataclass
class Aggregate():
	"""class Aggregating provided IPV4 prefixes..

	Raises:
		Exception: Incorrect IP / Format Received

	Returns:
		Aggregate: Object instance of Aggregate
	"""    	
	prefixes: list[str] = field(default_factory=list)

	def __post_init__(self):
		self._sort_prefixes()
		self.pfxs_dict = {}
		self._get_ip_objects()
		self._count_start_stop()
		self.int_ranges = self._get_continuous_ranges()
		self.int_ranges = _split_continuous_ranges(self.int_ranges)
		self._get_aggregates_from_ranges()

	# Sorting prefixes on ascending order
	def _sort_prefixes(self):
		df = pd.DataFrame({'subnets': list(self.prefixes)})
		df = sort_dataframe_on_subnet(df, 'subnets')
		self.prefixes = list(df['subnets'])

	# convert prefixes as IPv4 objects.
	def _get_ip_objects(self):
		for pfx in self.prefixes:
			try:
				if isinstance(pfx, str):
					self.pfxs_dict[IPv4(pfx)] = {}
				elif isinstance(pfx, IPv4):
					self.pfxs_dict[pfx] = {}
				else:
					raise Exception(f"[-] Incorrect IP / Format Received {pfx}\n{e}")					
			except Exception as e:
				raise Exception(f"[-] Incorrect IP / Format Received {pfx}\n{e}")

	# count and store network and broadcast number for each prefixes.
	def _count_start_stop(self):
		for pfx in self.pfxs_dict.keys():
			self.pfxs_dict[pfx]['net_num'] = pfx.network_number_int
			self.pfxs_dict[pfx]['bc_num'] = pfx.broadcast_number_int

	# sorted ranges 
	def _get_continuous_ranges(self):
		ranges = []
		for pfx, pfx_dict in self.pfxs_dict.items():
			# -- First entry
			if not ranges:
				ranges.append( (pfx_dict['net_num'], pfx_dict['bc_num']) ) 
				continue
			# -- adjuscent to previous network
			if ranges[-1][-1] + 1 == pfx_dict['net_num']:
				ranges[-1] = ( ranges[-1][0], pfx_dict['bc_num'] )
				continue
			# -- network within or same as previous existing prefix 
			if (
				(ranges[-1][0] <= pfx_dict['net_num'] <= ranges[-1][-1]) and
				(ranges[-1][0] <= pfx_dict['bc_num']  <= ranges[-1][-1])
				):
				continue
			# -- overlaping to previous network
			if (
				(ranges[-1][0] <= pfx_dict['net_num'] <= ranges[-1][-1]) and
				(                 pfx_dict['bc_num']  >  ranges[-1][-1])
				):
				ranges[-1] = ( ranges[-1][0], pfx_dict['bc_num'] )
				continue

			# -- Far apart previous
			ranges.append( (pfx_dict['net_num'], pfx_dict['bc_num']) ) 

		return ranges

	# get aggregate addresses from sorted ranges
	def _get_aggregates_from_ranges(self):
		self._summaries = []
		for start, end in self.int_ranges:
			ip = addressing(f"{dec2dotted_ip(start)}/{inv_subnet_size_to_mask(end-start)}")
			if ip.network_number_int == start and ip.broadcast_number_int == end:
				self._summaries.append(ip)
				continue
			raise Exception(f"[-] Script Error: Invalid Summary Found: {ip}")

	### ----- Available Properties --- ###

	@property
	def aggregates(self):
		"""returns list of aggregate IPv4 objects 

		Returns:
			list: list of IPv4 objects
		"""    		
		return self._summaries

	@property
	def summaries(self):
		"""returns list of aggregate strings.

		Returns:
			list: list of summary address strings
		"""    		
		return [str(_) for _ in self._summaries]

# =========================================================================================== 
def calc_summmaries(min_subnet_size, prefixes):
	"""summarize the provided network prefixes, provide all networks as arguments.
	minimum subnet summarized to provided min_subnet_size parameter

	Args:
		min_subnet_size (int): minimuze subnet mask to be summarized up on
		prefixes (list): networks 

	Returns:
		list: summaries
	"""    	
	summaries = Aggregate(prefixes).summaries
	nset = set()
	for subnet in summaries:
		if isinstance(subnet, IPv4) and subnet.mask > min_subnet_size:
			nset.add(subnet.expand(min_subnet_size))
		elif isinstance(subnet, str) and int(subnet.split("/")[-1]) > min_subnet_size:
			nset.add(IPv4(subnet).expand(min_subnet_size))
	summaries.extend(nset)
	nSummaries = Aggregate(summaries).summaries
	return nSummaries

# =========================================================================================== 
#  Get unused prefixes details from provided summary subnet 
# =========================================================================================== 
@dataclass
class Subnet_Spare():
	summary: str
	prefixes: list = field(default_factory=[])

	def __post_init__(self):
		try:
			self.sbig = addressing(self.summary) 
		except:
			self.sbig = None
		self.get_subset_subnets()
		self.remove_used_chunks()

	def get_subset_subnets(self):
		self.subset_prefixes = []
		if not self.sbig: return
		for subnet in self.prefixes:
			try:
				ssmall = addressing(subnet)
			except:
				## invalid subnets not checked
				continue 
			if ssmall.is_subset(self.sbig):
				self.subset_prefixes.append(ssmall)

	@property
	def smallest_pfx_mask(self):
		return min({s.mask for s in self.subset_prefixes})

	@property
	def smallest_pfx_host_count(self):
		return 2**(32-self.smallest_pfx_mask)

	@property
	def min_divisor(self):
		return int(len(self.sbig) / self.smallest_pfx_host_count)

	@property
	def smallest_divisions(self):
		return self.sbig / self.min_divisor

	def remove_used_chunks(self):
		self.remaining_chunk_pfx = set(self.smallest_divisions)
		for chunk in self.smallest_divisions:
			for subset_pfx in self.subset_prefixes:
				if isSubset(chunk, subset_pfx):
					self.remaining_chunk_pfx.remove(chunk)

	def unused_prefixes(self, obj=False):
		Agg = Aggregate(self.remaining_chunk_pfx)
		if obj:
			return Agg.aggregates
		return Agg.summaries

# =========================================================================================== 
if __name__ == "__main__":
	pass
# =========================================================================================== 

