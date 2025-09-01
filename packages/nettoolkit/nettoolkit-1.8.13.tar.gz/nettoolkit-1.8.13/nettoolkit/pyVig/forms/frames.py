
from nettoolkit.nettoolkit.forms.formitems import *

# ===================================================================

def pyvig_frame():
	"""tab display

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('Cable Matrix Generation', font=('TimesNewRoman', 12), text_color="orange") ],

		[sg.Text('clean data files:\t\t', text_color="black"),
		 sg.InputText('', key='pv_files_clean_data'), sg.FilesBrowse(), ],
		[sg.Text('output folder:\t\t',text_color='black'), 
		 sg.InputText(get_cache(CACHE_FILE, 'pv_folder_output'), key='pv_folder_output', change_submits=True),  
		 sg.FolderBrowse(),
		 sg.Button("open", change_submits=True, key='pv_folder_output_open', button_color="darkgrey"),],
		[sg.Text('cable matrix output filename:', text_color="black"), 
		 sg.InputText(get_cache(CACHE_FILE, 'pv_file_output_db'), key='pv_file_output_db', change_submits=True),  ],
		[sg.Text('Custom Package Yaml file:\t', text_color="black"), 
	     sg.InputText(get_cache(CACHE_FILE, 'cit_file_custom_yml'), key='pv_file_custom_yml', change_submits=True,), 
	     sg.FileBrowse(button_color="grey"), ],
		[sg.Checkbox('Keep All Columns \t        ', key='pv_opt_keep_all_cols', default=True, text_color='black'),
		 sg.Button("Cable Matrix Only", size=(20,1), change_submits=True, key='pv_btn_start_cm', button_color="blue"),],
		# ------------------------------------------------------------------------------------

		[sg.Text('Visio Drawing Generation', font=('TimesNewRoman', 12), text_color="orange") ],

		[sg.Text('Cable Matrix file:\t\t', text_color="black"), 
	     sg.InputText(get_cache(CACHE_FILE, 'pv_file_cable_matrix'), key='pv_file_cable_matrix', change_submits=True), 
	     sg.FileBrowse(),
		 sg.Button("open", change_submits=True, key='pv_file_cable_matrix_open', button_color="darkgrey"),],
		[sg.Text('Stencil Folder:\t\t', text_color="black"),
		 sg.InputText(get_cache(CACHE_FILE, 'pv_folder_stencil'), key='pv_folder_stencil',  change_submits=True), 
		 sg.FolderBrowse(),
		 sg.Button("open", change_submits=True, key='pv_folder_stencil_open', button_color="darkgrey"),],
		[sg.Text('Default Stencil:\t\t', text_color="black"),
		 sg.InputText(get_cache(CACHE_FILE, 'pv_file_default_stencil'), key='pv_file_default_stencil',  change_submits=True), 
		 sg.FileBrowse(),
		 sg.Button("open", change_submits=True, key='pv_file_default_stencil_open', button_color="darkgrey"),],
		[sg.Text('visio output filename:\t', text_color="black"), 
		 sg.InputText(get_cache(CACHE_FILE, 'pv_file_output_visio'), key='pv_file_output_visio', change_submits=True),  ],
		[sg.Text('Visio Output file:\t\t', text_color="black"), 
	     sg.InputText(get_cache(CACHE_FILE, 'pv_file_output_file_visio'), key='pv_file_output_file_visio', text_color="darkred",  disabled=True), 
		 sg.Button("open", change_submits=True, key='pv_file_output_file_visio_open', button_color="darkgrey"),],

		[sg.Text("\t"*3),
		 sg.Button("Visio Drawing Only", size=(20,1), change_submits=True, key='pv_btn_start_visio', button_color="blue"),],
		under_line(80),
		[sg.Text('\t\t\t'),
		 sg.Button("Cable Matrix + Visio Drawing", size=(40,1), change_submits=True, key='pv_btn_start_cm_visio', button_color="blue"),],
		])


PYVIG_FRAMES = {
	'Visio Drawing Generation': pyvig_frame(),
}