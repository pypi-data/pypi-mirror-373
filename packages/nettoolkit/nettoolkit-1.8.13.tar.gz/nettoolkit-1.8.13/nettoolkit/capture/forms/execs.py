
from nettoolkit.nettoolkit.forms.formitems import *
from nettoolkit.nettoolkit_common import read_yaml_mode_us, create_folders, open_text_file, open_excel_file, open_folder
from pathlib import *
import sys

from nettoolkit.capture import capture_by_jump_server_login


# ====================================================================================
def get_item_list(file, index=None):
	try:
		with open(file, 'r') as f:
			lns = f.readlines()
	except:
		return []
	if index is not None:
		try:
			return [line.strip().split()[index] for line in lns]
		except:
			pass
	return [ line.strip() for line in lns]

#### -- cache updates -- ####


# def update_cache_cit(i):
# 	update_cache(CACHE_FILE, cit_cred_un=i['cit_cred_un3'])
# 	update_cache(CACHE_FILE, cit_path_captures=i['cit_path_captures3'])
# 	update_cache(CACHE_FILE, cit_file_hosts=i['cit_file_hosts3'])
# 	update_cache(CACHE_FILE, cit_file_cisco=i['cit_file_cisco3'])
# 	update_cache(CACHE_FILE, cit_file_juniper=i['cit_file_juniper3'])
# 	update_cache(CACHE_FILE, cit_jump_server=i['cit_jump_server'])
# 	update_cache(CACHE_FILE, cit_jump_server_login_un=i['cit_jump_server_login_un'])
# 	update_cache(CACHE_FILE, cit_file_psk=i['cit_file_psk'])



def exec_cit_file_psk_open(i):
	open_text_file(i['cit_file_psk_open'])

def exec_cit_folder_path_captures_open3(i):
	open_folder(i['cit_path_captures3'])

def add_path(file):
	p = Path(file)
	_path = p.resolve().parents[0]
	sys.path.insert(len(sys.path), str(_path))

@activity_finish_popup
def capture_via_jump_start(i):
	if not i['cit_cred_un3'] or not i['cit_cred_pw3']:
		sg.Popup("[-] Mandatory information missing:  Credentionals")
		return
	devices_auth = { 'un':i['cit_cred_un3'], 'pw':i['cit_cred_pw3'], 'en':i['cit_cred_en3'] if i['cit_cred_en3'] else i['cit_cred_pw3'] }
	devices = get_item_list(i['cit_file_hosts3'], index=0)
	cmds = {
	    'cisco': get_item_list(i['cit_file_cisco3']),
    	'juniper': get_item_list(i['cit_file_juniper3']),
	}
	cumulative = True
	if i['cit_opt_cumulative3'] == 'cumulative': cumulative = True 
	elif i['cit_opt_cumulative3'] == 'non-cumulative': cumulative = False
	elif i['cit_opt_cumulative3'] == 'both': cumulative = 'both'
	#
	server_login_pw = i['cit_jump_server_login_pw'] if i['cit_jump_server_login_pw'] != "" else None
	file_psk = i['cit_file_psk'] if i['cit_file_psk'] != "" else None
	#

	capture_by_jump_server_login(
		# // Sever Parameters // #
		server=i['cit_jump_server'], 
		server_login_username=i['cit_jump_server_login_un'], 
		server_private_key_file = file_psk,
		server_login_password = server_login_pw,

		# // Device Parameters // #
		devices=devices, devices_auth=devices_auth,

		# // Commands dictionary // #
		cmds_list_dict=cmds,

		output_path=i['cit_path_captures3'],

		# // Options // #
		append = i['cit_opt_append3'],
		missing_only = i['cit_opt_missing3'],
		cumulative = cumulative,
		max_connections = int(i['cit_opt_max_connections3']),
		tablefmt = i['cit_tablefmt3'],
		failed_retry_count = i['cit_opt_frc'],
		interactive_cmd_report = i['cit_opt_cmd_int_report'],
	)
	print("[+] Capture Task(s) Complete..")


# ======================================================================================
