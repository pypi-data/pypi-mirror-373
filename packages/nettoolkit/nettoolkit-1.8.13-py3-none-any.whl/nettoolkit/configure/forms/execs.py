
from nettoolkit.nettoolkit.forms.formitems import *
from nettoolkit.nettoolkit_common import read_yaml_mode_us, create_folders, open_text_file, open_folder
from pathlib import *
import sys

from nettoolkit.configure import ConfigureByExcel

# ====================================================================================

def update_cache_confit(i): 
	update_cache(CACHE_FILE, confit_cred_un=i['confit_cred_un'])
	update_cache(CACHE_FILE, confit_folder_log=i['confit_folder_log'])

def exec_confit_folder_log_open(i):
	open_folder(i['confit_folder_log'])

@activity_finish_popup
def configure_it_start(obj, i):
	auth = {
		'un': i['confit_cred_un'] ,
		'pw': i['confit_cred_pw'], 
		'en': i['confit_cred_en'] if i['confit_cred_en'] else i['confit_cred_pw'],
	}
	files = obj.var_dict['confit_config_excel_out'] 
	captures_folder = i['confit_folder_log'] if i['confit_folder_log'] else ""
	# ==============================================
	C = ConfigureByExcel(auth,
		files=files,                         ## str-filenane, list - list of file names
		# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
		tab_sort_order=i['confit_tab_orders'],
		log_folder=captures_folder,
		config_log=i['confit_cb_conf_log'],
		exec_log=i['confit_cb_exec_log'],
		exec_display=i['confit_cb_show_log'],
		configure=True,                    ## Default False for test , True to configure
		# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
	)
	C()
	print("[+] Configuration All Task(s) Complete..")

# ================================ [ Listbox updates ] ========================================


def add_to_confit_config_excel_in(obj, i):
	if obj.var_dict.get('confit_config_excel_in'):
		new_list = obj.var_dict['confit_config_excel_in'] + i['confit_excel'].split(";")
	else:
		new_list = i['confit_excel'].split(";")
	if i['confit_excel'] != '':
		obj.event_update_element(confit_config_excel_in={'values': new_list})
		obj.event_update_element(confit_config_excel_out={'values': []})
	obj.var_dict['confit_config_excel_in'] = new_list
	obj.var_dict['confit_config_excel_out'] = []
	return True

def update_confit_config_excel_in_to_out(obj, i, event):
	return add_remove_lb_config_excel_files_sequenced('add', obj, i, event)

def update_confit_config_excel_out_to_in(obj, i, event):
	return add_remove_lb_config_excel_files_sequenced('remove', obj, i, event)

def add_remove_lb_config_excel_files_sequenced(what, obj, i, event):
	lst1 = obj.var_dict['confit_config_excel_in']
	lst2 = obj.var_dict['confit_config_excel_out']
	try:
		item = i[event][0]
	except IndexError:
		print("[-] No Such element")
		return False
	if what == 'add':
		lst2.append(item)
		lst1.remove(item)
	elif what == 'remove':
		lst1.append(item)
		lst2.remove(item)
		lst1 = sorted(lst1)
	obj.event_update_element(confit_config_excel_in={'values': lst1})
	obj.event_update_element(confit_config_excel_out={'values': lst2})
	obj.var_dict['confit_config_excel_in'] = lst1
	obj.var_dict['confit_config_excel_out'] = lst2
	return True

# ==============================================================================================

# ======================================================================================

CONFIGURE_EVENT_FUNCS = {
	'confit_btn_start': configure_it_start,
	'confit_cred_un': update_cache_confit,
	'confit_excel': add_to_confit_config_excel_in,
	'confit_config_excel_in': update_confit_config_excel_in_to_out,
	'confit_config_excel_out': update_confit_config_excel_out_to_in,
	'confit_folder_log_open': exec_confit_folder_log_open,
}
CONFIGURE_EVENT_UPDATERS = {'confit_excel', 'confit_btn_start'}
CONFIGURE_ITEM_UPDATERS = {'confit_config_excel_in', 'confit_config_excel_out', }

CONFIGURE_RETRACTABLES = {
	'confit_cred_pw', 'confit_cred_en',
	'confit_excel', 'confit_config_excel_in', 'confit_config_excel_out'
}

