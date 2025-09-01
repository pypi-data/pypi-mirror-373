
# ====================================================================
#  Imports
# ====================================================================
import socket
from nettoolkit.nettoolkit_common import Multi_Execution
from nettoolkit.nettoolkit_common.formatting import *
from nettoolkit.addressing.addressing import addressing

# ====================================================================
#  Local Functions
# ====================================================================

# validating input port ranges.
def _validate_input_port_range(port_start=None, port_end=None):
	PORT_START = 1
	PORT_END   = 65535

	if not port_start and not port_end: 
		port_end = PORT_END
	if port_start and not port_end: 
		port_end = port_start
	if not port_start:
		port_start = PORT_START
	elif not port_start:
		port_start = port_end	
	try:
		port_start = int(port_start)
		port_end = int(port_end)
	except:
		print(f"[-] Inputs should be integer numbers only")
		return None
	if port_end < port_start:
		print(f"[-] start {port_start} should be less than end {port_end}")
		return None
	if port_start<PORT_START or port_end>PORT_END:
		print(f"[-] invalid range of port provided{port_start}-{port_end}, should be within {PORT_START} and {PORT_END}")
		return None

	return (port_start, port_end)

# PORT Scanner class, enables multi executions.
class PortScanner(Multi_Execution):

	timeout = 2
	port_results = {}

	def __init__(self, target, port_ranges):
		self.target = target
		self.items = range( port_ranges[0], port_ranges[1]+1)

	def execute(self, p):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		socket.setdefaulttimeout(self.timeout)
		result = s.connect_ex((self.target, p))
		self.port_results[p] = result == 0 
		s.close()

	@property
	def open_ports(self):
		return {k for k, v in self.port_results.items() if v}

# ===============================================================================================
def ip_port_scan(target_ip, port_start=None, port_end=None, max_connections=65535):
	port_ranges = _validate_input_port_range(port_start, port_end)
	if port_ranges is None:
		print(f"[-] Cannot continue")
		return
	#
	PS = PortScanner(target_ip, port_ranges)
	PS.max_connections = max_connections
	PS.start()
	return PS.open_ports

def subnet_port_scan(subnet, port_start=None, port_end=None, max_connections=65535):
	result = {}
	network = addressing(subnet)
	for ip in network:
		r = ip_port_scan(ip) or None
		result[ip] = r
		print(f"[+] Found open Ports on {ip} = {r}")
	return result

# ===============================================================================================
#  main bypass
# ===============================================================================================
if __name__ == '__main__':
	pass
# ===============================================================================================