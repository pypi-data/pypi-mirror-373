


cmd_line_pfx = " output for command: "

# -----------------------------------------------------------------------------

def juniper_add_no_more(cmd):
	"""returns updated juniper command with proper full | no-more statement if missing or trunkated found.

	Args:
		cmd (str): juniper show command

	Returns:
		str: updated command with | no-more
	"""	
	spl = cmd.split("|")
	no_more_found = False
	for i, item in enumerate(spl):
		if i == 0: continue
		no_more_found = item.strip().startswith("n")
		if no_more_found:
			spl[i] = " no-more "
			break
	if not no_more_found:
		spl.append( " no-more ")
	ucmd = "|".join(spl)
	return ucmd


def exec_log(msg, to_file, display=False):
	"""print and write execution log to a file.

	Args:
		msg (str): log message
		to_file (str): filename with full path to where message to be added
		display (bool, optional): display message on screen or not. Defaults to False.
	"""    	
	if display: print(msg)
	with open(to_file, 'a') as f:
		f.write(msg+"\n")
