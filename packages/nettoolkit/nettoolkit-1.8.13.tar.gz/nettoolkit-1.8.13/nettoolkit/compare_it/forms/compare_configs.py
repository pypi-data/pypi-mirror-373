
# ---------------------------------------------------------------------------------------
from nettoolkit.compare_it import *

from nettoolkit.nettoolkit.forms.formitems import *
from nettoolkit.nettoolkit_common import IO

# ---------------------------------------------------------------------------------------

def go_compare_config_text_exec(i):
	"""executor function

	Args:
		i (itemobject): item object of frame

	Returns:
		bool: wheter executor success or not.
	"""	
	try:
		if i['compare_config_file1'] != '' and i['compare_config_file2'] != '':
			text_diff(i['compare_config_file1'], i['compare_config_file2'], i['op_folder_compare_config_text'])
			sg.Popup("Success!")
			return True
	except Exception as e:
		sg.Popup('Failure!')
		return None


def go_compare_config_xl_exec(i):
	"""executor function

	Args:
		i (itemobject): item object of frame

	Returns:
		bool: wheter executor success or not.
	"""	
	try:
		if i['compare_config_file3'] != '' and i['compare_config_file4'] != '':
			xl_diff(i['compare_config_file3'], i['compare_config_file4'], i['op_folder_compare_xl'],
				i['compare_config_tab_name'], i['compare_config_index_col'])
			sg.Popup("Success!")
			return True
	except Exception as e:
		sg.Popup('Failure!')
		return None


def compare_config_texts_frame():
	"""tab display - Compares two configuration output

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('compare text files (cisco/juniper)', font='Bold', text_color="black") ],
		under_line(80),

		[sg.Text('Select first file (text file only):',  text_color="yellow"), 
			sg.InputText(key='compare_config_file1'),  
			sg.FileBrowse()],

		[sg.Text('Select second file (text file only):',  text_color="yellow"), 
			sg.InputText(key='compare_config_file2'), 
			sg.FileBrowse()],

		[sg.Text('output folder:', text_color="yellow"), 
			sg.InputText('', key='op_folder_compare_config_text'),  
			sg.FolderBrowse(),
		],

		[sg.Button("Compare-Text", change_submits=True, key='go_compare_config_text')],
		under_line(80),

		# -----------------------------------------------------------------------------

		[sg.Text('compare excel files ', font='Bold', text_color="black") ],
		under_line(80),

		[sg.Text('Select first file (excel file only):',  text_color="yellow"), 
			sg.InputText(key='compare_config_file3'),  
			sg.FileBrowse()],

		[sg.Text('Select second file (excel file only):',  text_color="yellow"), 
			sg.InputText(key='compare_config_file4'), 
			sg.FileBrowse()],

		[sg.Text('output folder:', text_color="yellow"), 
			sg.InputText('', key='op_folder_compare_xl'),  
			sg.FolderBrowse(),
		],

		[sg.Text('tab name:',  text_color="yellow"), 
			sg.InputText(key='compare_config_tab_name'),],
		[sg.Text('index column name:',  text_color="yellow"), 
			sg.InputText(key='compare_config_index_col'),],


		[sg.Button("Compare-Excel", change_submits=True, key='go_compare_config_xl')],
		under_line(80),

		])

# ---------------------------------------------------------------------------------------


def text_diff(f1, f2, output_folder):
	"""text files difference using compare-it

	Args:
		f1 (str): text file reference
		f2 (str): text file reference
		output_folder (str): folder reference

	Returns:
		str: differences (multi-line)
	"""	
	output_file = output_folder+"/compare-text.op.txt"
	header = f"\n# {'-'*80} #\n" + f"# {' '*20} Difference between two Text files {' '*26}#\n" + f"# [{f1}] \n" + f"# [{f2}]\n" + f"# {'-'*80} #\n"
	removal_header = f"\n# {'- '*20} #\n" + f"# {' '*15} REMOVALS"  + f"\n# {'- '*20} #\n"
	addition_header = f"\n# {'+ '*20} #\n" + f"# {' '*15} ADDITIONS" + f"\n# {'+ '*20} #\n"
	#
	diff = {}
	removals = CompareText(f1, f2, "- ")
	adds = CompareText(f2, f1, "+ ")
	diff[removal_header] = removals.CTObj.diff
	diff[addition_header] = adds.CTObj.diff
	#
	diff_str = get_string_diffs(diff, header=header)
	#
	IO.to_file(output_file, matter=diff_str)
	return diff_str


def xl_diff(f1, f2, output_folder, sheet_name, index_col):
	"""excel file tab difference using compare-it
	default difference output file name is `compare-xl.op.txt`

	Args:
		f1 (_type_): excel file reference
		f2 (_type_): excel file reference
		output_folder (str): folder reference
		sheet_name (str): sheet/tab name
		index_col (str): index column name

	Returns:
		str: differences (multi-line)
	"""	
	output_file = output_folder+"/compare-xl.op.txt"

	diff = {}
	removals = CompareExcelData(f1, f2, sheet_name, "- ")   # removals from file1
	adds = CompareExcelData(f1, f2, sheet_name, "+ ")       # adds to file 2
	remove_diff = removals.diff(index_col)
	add_diff = adds.diff(index_col)
	removals_str = get_string_diffs(remove_diff, "")
	adds_str = get_string_diffs(add_diff, "")
	diff_str = removals_str +'\n\n'+ adds_str

	IO.to_file(output_file, matter=diff_str)
	return diff_str

# ---------------------------------------------------------------------------------------
