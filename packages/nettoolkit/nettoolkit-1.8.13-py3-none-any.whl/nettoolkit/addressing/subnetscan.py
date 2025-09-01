
# -----------------------------------------------------------------------------
import pandas as pd
try:
	import PySimpleGUI as sg
except:
	pass
from nettoolkit.nettoolkit_common import Multi_Execution, IP, nslookup
from nettoolkit.nettoolkit_db.database import write_to_xl, read_xl, get_merged_DataFrame_of_file

from .addressing import addressing

ping = IP.ping_average

# -----------------------------------------------------------------------------
class Ping(Multi_Execution):
	"""Multi Ping class

	Args:
		pfxs (list): list of prefixes
		till (int, optional): how many ips to select. Defaults to 5.
		concurrent_connections (int, optional): number of simultaneous pings. Defaults to 500.
		create_tabs (bool, optional): want to create individual tab (True) for each subnet or clubbed (False)
	"""	

	def __init__(self, pfxs, till=None, concurrent_connections=500, create_tabs=False):
		"""instance initializer
		"""		
		self.pfxs = pfxs
		self.till = till
		self.max_connections = concurrent_connections
		self.create_tabs = create_tabs
		self.items = self.get_first_ips()
		self.ping_results = {}
		self.ping_ms = {}
		self.dns_result = {}
		self.result = {'ping_ms': self.ping_ms, 'dns_result': self.dns_result, 'ping_results': self.ping_results} 
		self.results_dict = {}
		self.counter = 1
		self.start()

	def get_first_ips(self):
		"""selects ips for each subnets from given prefixes

		Args:

		Returns:
			list: crafted list with first (n)/ all ip addresses from each subnet
		"""	
		new_iplist=[]
		self.pfx_dict={}
		for pfx in self.pfxs:
			subnet = addressing(pfx)
			try:
				if self.till==0:
					hosts = subnet[0]
				elif self.till:
					hosts = subnet[0:int(self.till)+1]
				else:
					hosts =subnet[0:len(subnet)]
			except:
				hosts =subnet[0:len(subnet)]
			self.pfx_dict[pfx] = [host for host in hosts]
			new_iplist.extend(self.pfx_dict[pfx])
		return new_iplist

	def execute(self, ip):
		"""executor

		Args:
			ip (str): ip address
		"""		
		# print(f"pinging -{ip}")
		self.ping_ms[ip] = ping(ip)
		self.ping_results[ip] = True if self.ping_ms[ip]  else False
		self.dns_result[ip] = nslookup(ip)
		self.add_results(ip, self.ping_results[ip], self.ping_ms[ip], self.dns_result[ip])

	def add_results(self, ip, ping_R, ping_ms_R, dns_R):
		"""add ping/dns results to results dictionary

		Args:
			ip (str): ip address
			ping_R (bool): ping result True/False
			ping_ms_R (int): milisecond if True
			dns_R (str): dns result
		"""		
		for pfx, hosts in self.pfx_dict.items():
			if not ip in hosts: continue
			if not self.results_dict.get(pfx):
				self.results_dict[pfx] = {}
			self.results_dict[pfx][ip] = { 'ping_ms': ping_ms_R, 'dns_result': dns_R, 'ping_results': ping_R}
			break

	def op_to_xl(self, opfile):
		"""write out result of pings to an output file

		Args:
			opfile (str): output excel file 
		"""		
		if self.create_tabs:
			d = {}
			for pfx, ipresults in self.results_dict.items():
				d[pfx.replace("/", "_")] = pd.DataFrame(ipresults).T
			write_to_xl(opfile, d, index=True, overwrite=False, index_label='ip')
		else:
			df = pd.DataFrame(self.result)
			df.to_excel(opfile, index_label='ip')



def compare_ping_sweeps(first, second):
	"""comparision of two ping result excel files 

	Args:
		first (str): ping result excel file-1
		second (str): ping result excel file-2

	Returns:
		None: Returns None, prints out result on console/screen
	"""	
	#
	df1 = get_merged_DataFrame_of_file(first)
	df2 = get_merged_DataFrame_of_file(second)
	df1 = df1.set_index('ip')
	df2 = df2.set_index('ip')
	#
	sdf1 = df1.sort_values(by=['ping_results', 'ip'])
	sdf2 = df2.sort_values(by=['ping_results', 'ip'])
	#
	pinging1 = set(sdf1[(sdf1['ping_results'] == True)].index)
	not_pinging1 = set(sdf1[(sdf1['ping_results'] == False)].index)
	pinging2 = set(sdf2[(sdf2['ping_results'] == True)].index)
	not_pinging2 = set(sdf2[(sdf2['ping_results'] == False)].index)

	# -----------------------------------------------------------------------------

	missing = pinging1.difference(pinging2)
	added = pinging2.difference(pinging1)
	if not missing and not added:
		s = f'[+] All ping responce same, no changes'
		print(s)
		sg.Popup(s)
	else:
		if missing:
			s = f'\n{"="*80}\nips which were pinging in first file, but not pinging in second file\n{"="*80}\n{missing}\n{"="*80}\n'
			print(s)
			sg.Popup(s)
		if added:
			s = f'\n{"="*80}\nips which were not-pinging in first file, but it is pinging in second file\n{"="*80}\n{added}\n{"="*80}\n'
			print(s)
			sg.Popup(s)

	return None



# -----------------------------------------------------------------------------
# Execute
# -----------------------------------------------------------------------------
if __name__ == '__main__':
	pass
# ----------------------------------------------------------------------
