# """ creates ping script xxxx.bat file for ping test during / after cr
# provide prefixes and names of prefixes to it. 
# """

from .addressing import addressing
try:
	import PySimpleGUI as sg
except:
	pass

# -----------------------------------------------------------------------------
# Class to initiate UserForm
# -----------------------------------------------------------------------------

class CreateBatch():
	'''Create Batchfile GUI - Inititates a UserForm asking user inputs.	'''
	def __init__(self):
		s = "Deprycated class, use `Nettoolkit` instead"
		print(s)
		sg.Popup(s)


# ------------------------------------
def create_batch_file(pfxs, names, ip, op_folder):
	"""creates batch file(s)

	Args:
		pfxs (list): list of prefixes
		names (list): list of prefix names
		ip (list): ip(s) for which batch file(s) to be created
		op_folder (str): output folder where batch file(s) should be created

	Returns:
		bool, None: Result of outcome
	"""	
	if not isinstance(ip, int):
		try:
			ip = int(ip)
		except:
			s = f"[-] incorrect ip detected .`{ip}`, will be skipped"
			sg.Popup(s)
			print(s)
			return None
	if not op_folder:
		s = f'[-] Mandatory argument output folder was missing.\ncould not proceed, check inputs\n'
		sg.Popup(s)
		print(s)
		return None
	op_batch_filename = f"{op_folder}/ping_test-ips-.{ip}.bat"  
	#
	if not isinstance(pfxs, (list, tuple)):
		s = f'[-] Wrong type of prefix list \n{pfxs}, \ncould not proceed, check inputs\nExpected <class "list"> or <class "tuple">, got {type(pfxs)}\n'
		sg.Popup(s)
		print(s)
		return None
	if not isinstance(names, (list, tuple)):
		s = f'[-] Wrong type of name list \n{names}, \ncould not proceed, check inputs\nExpected <class "list"> or <class "tuple">, got {type(names)}\n'
		sg.Popup(s)
		print(s)
		return None
	if len(pfxs) != len(names):
		s = "[-] length of prefixes mismatch with length of names. both should be of same length \ncould not proceed, check inputs"
		sg.Popup(s)
		print(s)
		return None
	#
	# ------------------------------------
	list_of_ips = add_ips_to_lists(pfxs, ip)
	s = create_batch_file_string(list_of_ips, names)
	write_out_batch_file(op_batch_filename, s)
	# ------------------------------------
	return True

def add_ips_to_lists(pfxs, n):
	"""create list of ip addresses for given nth ip from given prefixes 

	Args:
		pfxs (list): list of subnets/prefixes
		n (int): nth ip address

	Returns:
		list: crafted list of ip addresses
	"""	
	list_of_1_ips = []
	for pfx in pfxs:
		subnet = addressing(pfx)
		try:
			ip1 = subnet[n]
			list_of_1_ips.append(ip1)
		except:
			pass
	return list_of_1_ips

def create_batch_file_string(lst, names):
	"""get the output batch file content

	Args:
		lst (list): list of prefixes
		names (list): list of prefix names

	Returns:
		str: output batch file content
	"""	
	s = ''
	for ip, name in zip(lst, names):
		s += f'start "{name}" ping -t {ip}\n'
	return s


def write_out_batch_file(op_batch_filename, s):
	"""write the output batch file.

	Args:
		op_batch_filename (str): output file name
		s (str): mutliline string to write to file
	"""	
	print(f'[+] creating batch file {op_batch_filename}')
	with open(op_batch_filename, 'w') as f:
		f.write(s)

# ------------------------------------
if __name__ == '__main__':
	pass
# ------------------------------------

