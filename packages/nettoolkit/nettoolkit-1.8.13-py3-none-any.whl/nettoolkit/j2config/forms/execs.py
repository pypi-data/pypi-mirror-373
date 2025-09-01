
from nettoolkit.nettoolkit.forms.formitems import *
from nettoolkit.nettoolkit_common import create_folders, open_text_file, open_folder, open_excel_file
from pathlib import *
import sys

from nettoolkit.j2config import exec_config_generation, get_host
from nettoolkit.j2config.general import get_model_template_version


# ====================================================================================

#### -- cache updates -- ####
def update_cache_j2(i):
	update_cache(CACHE_FILE, cit_file_custom_yml=i['j2_file_custom_yml'])
	update_cache(CACHE_FILE, j2_file_regional=i['j2_file_regional'])	
	update_cache(CACHE_FILE, j2_output_folder=i['j2_output_folder'])	
	update_cache(CACHE_FILE, j2_file_template=i['j2_file_template'])	
	update_cache(CACHE_FILE, j2_file_data=i['j2_file_data'])	

def exec_j2_file_regional_open(i):
	open_excel_file(i['j2_file_regional'])
def exec_j2_folder_output_open(i):
	open_folder(i['j2_output_folder'])
def exec_j2_file_data_open(i):
	open_excel_file(i['j2_file_data'])
def exec_j2_file_template_open(i):
	open_text_file(i['j2_file_template'])
def exec_j2_files_output_open(i):
	for file in i['j2_output_files'].split(";"):
		open_text_file(file)

def add_path(file):
	sys.path.insert(len(sys.path), str(Path(file).resolve().parents[0]))


@activity_finish_popup
def j2config_start(obj, i):
	custom =  i['j2_file_custom_yml']
	if custom:
		add_path(custom)
	regional_file = i['j2_file_regional'] if i['j2_file_regional'] else None
	#
	exec_config_generation(
		data_files=i['j2_file_data'].split(";"),
		template_file=i['j2_file_template'],
		output_folder=i['j2_output_folder'],
		regional_file=regional_file, 
		custom=i['j2_file_custom_yml'],
	)
	#
	update_output_files(obj, i)


def update_output_files(obj, i):
	update_cache_j2(i)
	model, template_ver = get_model_template_version(i['j2_file_template'])
	files = ";".join( 
		[f"{i['j2_output_folder']}/{get_host(file)}-{model}-{template_ver}-j2Gen.cfg"
		 for file in i['j2_file_data'].split(";")
	])
	obj.event_update_element(j2_output_files={'value': files})


# ======================================================================================

J2CONFIG_EVENT_FUNCS = {
	'j2_btn_start': j2config_start,
	'j2_file_custom_yml': update_cache_j2,
	'j2_file_regional': update_cache_j2,
	'j2_file_data': update_cache_j2,
	'j2_file_template': update_cache_j2,
	'j2_output_folder': update_cache_j2,

	'j2_file_template_open': exec_j2_file_template_open,
	'j2_file_data_open': exec_j2_file_data_open,
	'j2_folder_output_open': exec_j2_folder_output_open,
	'j2_file_regional_open': exec_j2_file_regional_open,
	'j2_files_output_open': exec_j2_files_output_open,
}
J2CONFIG_EVENT_UPDATERS = {
	'j2_btn_start'
}
J2CONFIG_ITEM_UPDATERS = set()

J2CONFIG_RETRACTABLES = {
	'j2_file_template', 'j2_file_data', 
}

