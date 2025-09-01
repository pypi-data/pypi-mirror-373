
import os
try:
	from PySimpleGUI import Popup
except:
	pass


# -----------------------------------------------------------------------------------
# Stencil functions
# -----------------------------------------------------------------------------------
def get_list_of_stencils(folder, devices_data):
	"""finds the required stencil files in given folder and return those filenames in a list.

	Args:
		folder (str): path of folder where stencils stored
		devices_data (DeviceData): Device Data object

	Raises:
		ValueError: Raise Exception if any stencil is missing

	Returns:
		list: list of file names
	"""	
	default_stencil = devices_data.default_stencil
	stencil_col = 'stencil'
	if not stencil_col in devices_data.df:
		print(f"[-] column information incorrect, check column existance `{stencil_col}`") 
		Popup(f"[-] column information incorrect, check column existance `{stencil_col}`") 
		devices_data.df[stencil_col] = ""

	used_stn = set(devices_data.df[stencil_col])
	try:
		used_stn.remove("")
	except: pass
	found_stn = []
	stn_file = set()
	if folder:
		for file in os.listdir(folder):
			if file.startswith("~$$"): continue
			if default_stencil and default_stencil == ".".join(file.split(".")[:-1]):
				found_stn.append(folder+"/"+file)
				stn_file.add(".".join(file.split(".")[:-1]))
				continue
			for stn in used_stn:
				if ".".join(file.split(".")[:-1]) == stn:
					found_stn.append(folder+"/"+file)
					stn_file.add(".".join(file.split(".")[:-1]))
					break

	if not folder: 
		Popup("Not a valid Stencils or Stencil Folder")

	if len(used_stn) == len(stn_file):
		return found_stn
	elif len(used_stn) == 0:
		return found_stn
	else:
		pass
		print("[-] Error:\t\tBelow mentioned stencil(s) are missing; ",
		"Kindly update/correct data before re-run.\n",
		used_stn.difference(stn_file), "\n",
		)
		Popup("Below mentioned stencil(s) are missing; ",
		"Kindly update/correct data before re-run.\n",
		used_stn.difference(stn_file), "\n")
		# raise ValueError("Stencil is/are Missing or Invalid")
		quit()

