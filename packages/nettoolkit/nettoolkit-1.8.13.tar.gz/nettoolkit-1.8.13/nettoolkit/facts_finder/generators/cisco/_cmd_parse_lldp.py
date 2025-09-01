"""cisco show lldp neighbour command output parser """

# ------------------------------------------------------------------------------

from nettoolkit.facts_finder.generators.commons import *
from .common import *
# ------------------------------------------------------------------------------

def get_lldp_neighbour(cmd_op, *args, dsr=True):
	"""parser - show lldp neigh command output

	Parsed Fields:
		* port/interface
		* neighbor interface
		* neighbor hostname

	Args:
		cmd_op (list, str): command output in list/multiline string.
		dsr (bool, optional): DOMAIN SUFFIX REMOVAL. Defaults to True.

	Returns:
		dict: output dictionary with parsed fields
	"""
	cmd_op = verifid_output(cmd_op)
	nbr_d, remote_hn = {}, ""
	nbr_table_start = False
	for i, line in enumerate(cmd_op):
		line = line.strip()
		dbl_spl = line.split("  ")
		if line.startswith("Device ID"): 
			nbr_table_start = True
			continue
		if not nbr_table_start: continue
		if not line.strip(): continue				# Blank lines
		if line.startswith("Total "): break  		# Summary line
		if line.startswith("!"): continue			# Remarked line

		### NBR TABLE PROCESS ###

		# // LOCAL/NBR INTERFACE, NBR PLATFORM //
		# // NBR HOSTNAME //
		local_if = STR.if_standardize(line[20:31].strip().replace(" ", ""))
		try:
			remote_if = STR.if_standardize(dbl_spl[-1].strip())
		except KeyError:
			remote_if = ''
		remote_hn = line[:20].strip()
		if dsr: remote_hn = remove_domain(remote_hn)

		# SET / RESET
		nbr_d[local_if] = {}
		nbr = nbr_d[local_if]
		nbr['nbr_hostname'] = remote_hn
		nbr['nbr_interface'] = remote_if
		remote_hn, remote_if, local_if = "", "", ""

		# -- not yet implemented , enable if error of blank key due to lldp neighbor.
		# if not (nbr_d.get('filter') and nbr_d['filter']):
		# 	nbr['filter'] = get_cisco_int_type(local_if)

	return {'op_dict': nbr_d }
# ------------------------------------------------------------------------------
