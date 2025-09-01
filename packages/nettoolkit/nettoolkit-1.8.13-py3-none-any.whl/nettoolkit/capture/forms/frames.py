
from nettoolkit.nettoolkit.forms.formitems import *

# ===================================================================
TABLE_FORMATS = [
	'rounded_outline', 'simple_outline', 'heavy_outline', 'mixed_outline', 'double_outline', 'fancy_outline',
	'presto', 'outline', 'pipe',
	'pretty',  'psql',  
	'orgtbl', 'jira', 'textile', 'html', 'latex',
]
CAPTURE_MODES = ('cumulative', 'non-cumulative', 'both')

def capture_it_poller_frame():
	"""tab display - Credential inputs

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[


		[sg.Text('Jump Sever Details',  font=('TimesNewRoman', 12), text_color="orange"),], 
		[sg.Text("Server\t",     text_color="black"), sg.InputText(get_cache(CACHE_FILE, 'cit_jump_server'), key='cit_jump_server', size=(15,1),  change_submits=True,),],
		[sg.Text("username",     text_color="black"), sg.InputText(get_cache(CACHE_FILE, 'cit_jump_server_login_un'), key='cit_jump_server_login_un', size=(15,1),  change_submits=True,)],
		[sg.Text("password\t",     text_color="black"), sg.InputText("", password_char='*', key='cit_jump_server_login_pw', size=(15,1)),
		 sg.Text('//or// PSK [public key] file:', text_color="black"), 
	     sg.InputText(get_cache(CACHE_FILE, 'cit_file_psk'), size=(15,1),  key='cit_file_psk', change_submits=True,), 
	     sg.FileBrowse(button_color="grey"),
		 sg.Button("open file", change_submits=True, key='cit_file_psk_open', button_color="darkgrey"),],


		[sg.Text('Devices Credentials',  font=('TimesNewRoman', 12), text_color="orange"),], 
		[sg.Text("un:",     text_color="black"),sg.InputText(get_cache(CACHE_FILE, 'cit_cred_un'), key='cit_cred_un3', size=(8,1), change_submits=True),
		 sg.Text("pw:",     text_color="black"),sg.InputText("", key='cit_cred_pw3', password_char='*', size=(20,1),),
		 sg.Text("secret:", text_color="black"),sg.InputText("", key='cit_cred_en3',  password_char='*', size=(20,1)), ],

		[sg.Text('Inputs',  font=('TimesNewRoman', 12), text_color="orange"),], 
		[sg.Text('output folder:\t\t', text_color="black"), 
		 sg.InputText(get_cache(CACHE_FILE, 'cit_path_captures'), key='cit_path_captures3', change_submits=True),  
		 sg.FolderBrowse(button_color="orange"), 
		 sg.Button("open", change_submits=True, key='cit_folder_path_captures_open3', button_color="darkgrey"),],
		# [sg.Text('execution log folder:\t', text_color="black"), 
		#  sg.InputText(get_cache(CACHE_FILE, 'cit_path_logs'), key='cit_path_logs', change_submits=True), 
		#  sg.FolderBrowse(button_color="orange"), 
		#  sg.Button("open", change_submits=True, key='cit_folder_path_logs_open', button_color="darkgrey"),],
		# [sg.Text('summary log folder:\t', text_color="black"), 
		#  sg.InputText(get_cache(CACHE_FILE, 'cit_path_summary'), key='cit_path_summary', change_submits=True),  
		#  sg.FolderBrowse(button_color="orange"), 
		#  sg.Button("open", change_submits=True, key='cit_folder_path_summary_open', button_color="darkgrey"),],

		[sg.Text('Hosts/IPs file:\t\t', text_color="black"), 
	     sg.InputText(get_cache(CACHE_FILE, 'cit_file_hosts'), size=(30,1),  key='cit_file_hosts3', change_submits=True,), 
	     sg.FileBrowse(button_color="grey"), sg.Button("open file", change_submits=True, key='cit_file_hosts_open3', button_color="darkgrey"),],
		[sg.Text('Cisco commands file:\t', text_color="black"), 
	     sg.InputText(get_cache(CACHE_FILE, 'cit_file_cisco'), size=(30,1), key='cit_file_cisco3', change_submits=True,), 
	     sg.FileBrowse(button_color="grey"), sg.Button("open file", change_submits=True, key='cit_file_cisco_open3', button_color="darkgrey"),],
		[sg.Text('Juniper Commands file:\t', text_color="black"), 
	     sg.InputText(get_cache(CACHE_FILE, 'cit_file_juniper'), size=(30,1), key='cit_file_juniper3', change_submits=True,), 
	     sg.FileBrowse(button_color="grey"), sg.Button("open file", change_submits=True, key='cit_file_juniper_open3', button_color="darkgrey"),],
		# [sg.Checkbox('', key='cit_opt_dependent',     default=True,  text_color='black'),
		#  sg.Text('Custom Pkg Yaml file:', text_color="black"), 
	 #     sg.InputText(get_cache(CACHE_FILE, 'cit_file_custom_yml'), key='cit_file_custom_yml', change_submits=True,), 
	 #     sg.FileBrowse(button_color="grey"), ],



		[sg.Text('Options',  font=('TimesNewRoman', 12), text_color="orange"),
		 sg.Text('\t\t\t\tMode\t\tSummaryTableFormat', text_color="black"), 
		], 
		[sg.Checkbox('Missing only',	key='cit_opt_missing3',       default=False, text_color='black'),
		 sg.Checkbox('Append',	        key='cit_opt_append3',        default=False, text_color='black'),
		 # sg.Checkbox('CIT Format',	    key='cit_opt_format3',        default=True,  text_color='black'),
		 sg.Text('\t'),
		 sg.InputCombo(CAPTURE_MODES,   key='cit_opt_cumulative3',     default_value=CAPTURE_MODES[0],  ),
		 sg.InputCombo(TABLE_FORMATS,   key='cit_tablefmt3',           default_value='pretty',          ), 
		],
		[sg.Checkbox('Commands execution display,\t',	key='cit_opt_cmd_int_report',       default=True, text_color='black'),
		 sg.Text('Failed commands retry', text_color="black"), 
		 sg.InputCombo([1,2,3,4,5],   key='cit_opt_frc',     default_value=2,  ),
		 # sg.Checkbox('Commands Summary',	key='cit_opt_cmd_fin_report',       default=False, text_color='black'),
		],
		[sg.Text('Concurrent connections throttle', text_color="black"), 
		 sg.InputText(100,  key='cit_opt_max_connections3', size=(5,1) ), sg.Text('Use 1 for sequential process', text_color="white"), 
		],

		[sg.Text('\t\t\t\t\t\t\t\t'),
		 sg.Button("Capture", change_submits=True, size=(20,1), key='cit_via_server_btn_start', button_color="blue"),],

		])


# CAPTUREIT_VIA_POLLER_FRAMES = {
# 	'Capture-It via Poller': capture_it_poller_frame(),
# }