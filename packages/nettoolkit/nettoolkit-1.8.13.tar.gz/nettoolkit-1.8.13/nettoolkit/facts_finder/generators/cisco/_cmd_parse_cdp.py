"""cisco show cdp neighbour command output parser """

# ------------------------------------------------------------------------------

from nettoolkit.facts_finder.generators.commons import *
from .common import *
# ------------------------------------------------------------------------------

def get_cdp_neighbour(cmd_op, *args, dsr=True):
	"""parser - show cdp neigh command output // Deprycated and removed // use lldp neighbor instead.

	Parsed Fields:
		* port/interface
		* neighbor interface
		* neighbor plateform
		* neighbor hostname

	Args:
		cmd_op (list, str): command output in list/multiline string.
		dsr (bool, optional): DOMAIN SUFFIX REMOVAL. Defaults to True.

	Returns:
		dict: output dictionary with parsed fields
	"""	
	cmd_op = verifid_output(cmd_op)
	nbr_d, remote_hn, prev_line = {}, "", ""
	nbr_table_start = False
	for i, line in enumerate(cmd_op):

		if line.startswith("Device ID"): 
			hdr_idx = STR.header_indexes_using_splitby(line)
			nbr_table_start = True
			continue
		if not nbr_table_start: continue
		if not line.strip(): continue				# Blank lines
		if line.startswith("Total "): continue		# Summary line
		if line.startswith("!"): continue			# Remarked line

		### NBR TABLE PROCESS ###
		if len(line.strip().split()) == 1:  
			remote_hn = line[hdr_idx['Device ID'][0]:]
			prev_line = True
			continue
		else:
			if not prev_line: remote_hn = line[hdr_idx['Device ID'][0]:hdr_idx['Device ID'][-1]]
			local_if = line[hdr_idx['Local Intrfce'][0]:hdr_idx['Local Intrfce'][-1]].strip()
			try:
				local_if = STR.if_standardize(local_if)
			except:
				pass
			remote_if = line[hdr_idx['Port ID'][0]:hdr_idx['Port ID'][-1]].strip()
			try:
				remote_if = STR.if_standardize(remote_if)
			except:
				pass
			remote_plateform = line[hdr_idx['Platform'][0]:hdr_idx['Platform'][-1]]
			prev_line = False

		if remote_hn and dsr: remote_hn = remove_domain(remote_hn)

		# SET / RESET
		nbr_d[local_if] = {}
		nbr = nbr_d[local_if]
		nbr['nbr_hostname'] = remote_hn
		nbr['nbr_interface'] = remote_if
		nbr['nbr_plateform'] = remote_plateform
		remote_hn, remote_if, remote_plateform = "", "", ""

	return {'op_dict': nbr_d }
# ------------------------------------------------------------------------------
