
from nettoolkit.nettoolkit.forms.formitems import *

# ===================================================================

def configure_it_frame():
	"""tab display

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('Credentials',  font=('TimesNewRoman', 12), text_color="orange"),], 
		[sg.Text("un:",     text_color="black"),sg.InputText(get_cache(CACHE_FILE, 'confit_cred_un'), key='confit_cred_un', size=(8,1), change_submits=True),
		 sg.Text("pw:",     text_color="black"),sg.InputText("", key='confit_cred_pw', password_char='*', size=(20,1),),
		 sg.Text("secret:", text_color="black"),sg.InputText("", key='confit_cred_en',  password_char='*', size=(20,1)), ],
		# under_line(80),

		[sg.Text('Inputs',  font=('TimesNewRoman', 12), text_color="orange"),], 
		[sg.Text('Provide configuration Excel(s):', text_color="black"), 
		 sg.InputText('', disabled=True, key='confit_excel', change_submits=True,), 
		 sg.FilesBrowse(),],

		[sg.Listbox([], key='confit_config_excel_in', change_submits=False, size=(80,3), horizontal_scroll=True, bind_return_key=True)],
		[sg.Text('Re-Sequence Files as required Execution Order:', text_color="black")], 
		[sg.Listbox([], key='confit_config_excel_out',  change_submits=False, size=(80,3),horizontal_scroll=True , bind_return_key=True )],

		[sg.Text('Options',  font=('TimesNewRoman', 12), text_color="orange"),], 
		[sg.Text('Excel tabs execution ordering: ', text_color="black"), 
		 sg.InputCombo(['ascending', 'reversed'], default_value='ascending' , key='confit_tab_orders', size=(12,1)),],

		[sg.Text('Provide Log folder:', text_color="black"), 
		 sg.InputText(get_cache(CACHE_FILE, 'confit_folder_log'), key='confit_folder_log', change_submits=True), 
		 sg.FolderBrowse(),
		 sg.Button("open", change_submits=True, key='confit_folder_log_open', button_color="darkgrey"),],

		[sg.Checkbox('Configuration Logs', key='confit_cb_conf_log', default=True, text_color='black'),
		 sg.Checkbox('Execution Logs',     key='confit_cb_exec_log', default=True, text_color='black'),
		 sg.Checkbox('On-screen display',  key='confit_cb_show_log', default=True, text_color='black')],

		# under_line(80),

		# ------------------------------------------------------------------------------------
		[sg.Text('\t\t\t\t\t\t\t'),
		 sg.Button("Configure", change_submits=True, size=(20,1), key='confit_btn_start', button_color="brown"),],

		])


CONFIGURE_FRAMES = {
	'Push Configuration': configure_it_frame(),
}