
from nettoolkit.nettoolkit_common import *

# ========================================================================================

def update_int_number(number):
	"""calculates and returns interface number for given interface

	Args:
		number (str): cisco/juniper interface

	Returns:
		str: interface number
	"""	
	if not number: return -1
	port_suffix = STR.if_suffix(number)
	s = 0
	for i, n in enumerate(reversed(port_suffix.split("/"))):
		org_n = n
		spl_n = n.split(".")
		pfx = spl_n[0]
		if pfx == org_n:
			pfx = pfx.split(":")[0]
		if pfx != '0':
			if len(spl_n) == 2:
				sfx = float("0." + spl_n[1])
			else:
				sfx = 0
			multiplier = 100**i
			if pfx:
				nm = int(pfx)*multiplier
				s += nm+sfx
		else:
			#
			s += int(spl_n[-1])
	return s

def generate_int_number(pdf):
	"""generates interface number for each interfaces

	Args:
		pdf (DataFrame): Pandas DataFrame
	"""	
	pdf['int_number'] =  pdf['interface'].apply(update_int_number)
	pdf.sort_values(by=['int_number'], inplace=True)

# ========================================================================================
