
from nettoolkit.nettoolkit.forms.formitems import *
from nettoolkit.nettoolkit_common import open_text_file, open_folder
from pathlib import *
import sys

from nettoolkit.pyVig import exec_pyvig_cable_matrix, exec_pyvig_visio

# ====================================================================================

#### -- cache updates -- ####
def update_cache_pyvig(i):
	update_cache(CACHE_FILE, cit_file_custom_yml=i['pv_file_custom_yml'])
	update_cache(CACHE_FILE, pv_folder_stencil=i['pv_folder_stencil'])
	update_cache(CACHE_FILE, pv_file_default_stencil=i['pv_file_default_stencil'])
	update_cache(CACHE_FILE, pv_folder_output=i['pv_folder_output'])
	update_cache(CACHE_FILE, pv_file_output_db=i['pv_file_output_db'])
	update_cache(CACHE_FILE, pv_file_output_visio=i['pv_file_output_visio'])
	update_cache(CACHE_FILE, pv_file_cable_matrix=i['pv_file_cable_matrix'])
	update_cache(CACHE_FILE, pv_file_output_file_visio=i['pv_file_output_file_visio'])

def update_keep_all_cols(obj, i):
	obj.event_update_element(pv_opt_keep_all_cols={'value': True})

def update_cm_cache_pyvig(obj, i):
	xlextension = "" if i['pv_file_output_db'].endswith(".xlsx") else ".xlsx" 
	visextension = "" if i['pv_file_output_visio'].endswith(".vsdx") else ".vsdx" 
	#
	op_db_file = i['pv_folder_output'] + "/" + i['pv_file_output_db'] + xlextension
	op_vis_file = i['pv_folder_output'] + "/" + i['pv_file_output_visio'] + visextension
	obj.event_update_element(pv_file_cable_matrix={'value': op_db_file})	
	obj.event_update_element(pv_file_output_file_visio={'value': op_vis_file})	
	update_cache_pyvig(i)

def exec_pv_folder_output_open(i):
	open_folder(i['pv_folder_output'])
def exec_pv_folder_stencil_open(i):
	open_folder(i['pv_folder_stencil'])
def exec_pv_file_default_stencil_open(i):
	open_folder(i['pv_file_default_stencil'])
def exec_pv_file_cable_matrix_open(i):
	open_folder(i['pv_file_cable_matrix'])
def exec_pv_file_output_file_visio_open(i):
	open_folder(i['pv_file_output_file_visio'])

def add_path(file):
	sys.path.insert(len(sys.path), str(Path(file).resolve().parents[0]))

def get_filename(file):
	return Path(file).stem

def pyvig_start_cm(obj, i, followedbyvisio=False):
	custom = i['pv_file_custom_yml']
	if i['pv_file_custom_yml']:
		add_path(custom)

	xlextension = "" if i['pv_file_output_db'].endswith(".xlsx") else ".xlsx" 
	output_file = i['pv_folder_output'] + "/" + i['pv_file_output_db'] + xlextension
	#
	opd = exec_pyvig_cable_matrix(
		files=i['pv_files_clean_data'].split(";"),
		output_file=output_file,
		custom=custom,
		default_stencil=get_filename(i['pv_file_default_stencil']),
		keep_all_cols=i['pv_opt_keep_all_cols'],
	)
	obj.event_update_element(pv_file_cable_matrix={'value': opd['data_file']})	
	if not followedbyvisio:
		sg.Popup("Activity Finished")
	return opd

def prepare_visio_drawing(dic, i):
	custom = i['pv_file_custom_yml']
	if i['pv_file_custom_yml']:
		add_path(custom)
	#
	visextension = "" if i['pv_file_output_visio'].endswith(".vsdx") else ".vsdx" 
	output_file = str(Path(i['pv_folder_output'])) + "/" + i['pv_file_output_visio'] + visextension
	#
	exec_pyvig_visio(
		data_file=i['pv_file_cable_matrix'],
		output_file=output_file,
		stencil_folder=i['pv_folder_stencil'],
		custom=custom,
		dic=dic,
	)
	sg.Popup("Activity Finished")

def pyvig_start_visio(obj, i):
	update_keep_all_cols(obj, i)
	dic = {}
	prepare_visio_drawing(dic, i)

def pv_start_cm_visio(obj, i):
	update_keep_all_cols(obj, i)
	dic = pyvig_start_cm(obj, i, followedbyvisio=True)
	prepare_visio_drawing(dic, i)

# ======================================================================================

PYVIG_EVENT_FUNCS = {
	'pv_btn_start_cm': pyvig_start_cm,
	'pv_btn_start_visio': pyvig_start_visio,
	'pv_btn_start_cm_visio': pv_start_cm_visio,
	'pv_file_custom_yml': update_cache_pyvig,
	'pv_folder_stencil': update_cache_pyvig,
	'pv_file_default_stencil': update_cache_pyvig,
	'pv_file_cable_matrix': update_cache_pyvig,
	'pv_file_output_file_visio': update_cache_pyvig,

	'pv_folder_output': update_cm_cache_pyvig,
	'pv_file_output_db': update_cm_cache_pyvig,
	'pv_file_output_visio': update_cm_cache_pyvig,

	'pv_folder_output_open': exec_pv_folder_output_open,
	'pv_folder_stencil_open': exec_pv_folder_stencil_open,
	'pv_file_default_stencil_open': exec_pv_file_default_stencil_open,
	'pv_file_cable_matrix_open': exec_pv_file_cable_matrix_open, 
	'pv_file_output_file_visio_open': exec_pv_file_output_file_visio_open,

}
PYVIG_EVENT_UPDATERS = {
	'pv_folder_output', 'pv_file_output_db', 'pv_file_output_visio',
	'pv_btn_start_cm', 'pv_btn_start_visio', 'pv_btn_start_cm_visio',
}
PYVIG_ITEM_UPDATERS = set()

PYVIG_RETRACTABLES = {
	'pv_files_clean_data', 'pv_folder_stencil', 'pv_file_default_stencil', 
}

