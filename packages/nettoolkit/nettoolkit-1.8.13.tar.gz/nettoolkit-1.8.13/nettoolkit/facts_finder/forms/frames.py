
from nettoolkit.nettoolkit.forms.formitems import *

# ===================================================================

def facts_finder_frame():
	"""tab display - Credential inputs

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('Facts Generatorion Inputs', font=('TimesNewRoman', 12), text_color="orange") ],

		[sg.Text('log files\t\t', text_color="black"), 
		 sg.InputText('', key='ff_log_files'), 
		 sg.FilesBrowse(key='ff_log_files_btn'), ],
		[sg.Text('Output Folder\t', text_color="black"), 
		 sg.InputText(get_cache(CACHE_FILE, 'yf_output_folder'), key='yf_output_folder', change_submits=True), 
		 sg.FolderBrowse(key='yf_output_folder_browse_btn'), ],
		# under_line(80),
		blank_line(),

		[sg.Text('Excel Facts',  font=('TimesNewRoman', 12), text_color="orange") ],
		[sg.Text('Custom Pkg Yaml file:', text_color="black"), 
	     sg.InputText(get_cache(CACHE_FILE, 'cit_file_custom_yml'), key='ff_file_custom_yml', change_submits=True,), 
	     sg.FileBrowse(button_color="grey"), ],
		[sg.Text('File suffix', text_color="black"),  sg.InputText('-clean', key='ff_new_suffix', size=(10,1)),],
		[sg.Button("Facts Gen - Excel", change_submits=True, size=(20,1), key='ff_btn_start', button_color="blue"),],
		blank_line(),
		[sg.Text('Yaml Facts',  font=('TimesNewRoman', 12), text_color="orange") ],
		[sg.Button("Facts Gen - Yaml",  change_submits=True, size=(20,1), key='yf_btn_start', button_color="blue"),],
		# under_line(80),


		])


FACTSFINDER_FRAMES = {
	'Facts-Finder': facts_finder_frame(),
}