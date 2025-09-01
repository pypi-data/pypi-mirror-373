# ------------------------------------------------------------------------------
#  Local Functions
# ------------------------------------------------------------------------------

def get_filename(absolute_pathfile):
	"""This function takes in the absolute path of a file and returns the filename.

	Args:
		absolute_pathfile (str): The absolute path of the file.

	Returns:
		str: filename
	"""	
	return absolute_pathfile.split("/")[-1].split("""\\""")[-1].split(".")[0]
