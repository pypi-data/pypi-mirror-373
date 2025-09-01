
from nettoolkit.nettoolkit.forms.formitems import *
from nettoolkit.nettoolkit_common import create_folders, open_text_file
from pathlib import *
import sys

from nettoolkit.facts_finder import exec_facts_finder
from nettoolkit.yaml_facts import exec_yaml_facts

# ====================================================================================

#### -- cache updates -- ####
def update_cache_ff(i):
	update_cache(CACHE_FILE, cit_file_custom_yml=i['ff_file_custom_yml'])
	update_cache(CACHE_FILE, yf_output_folder=i['yf_output_folder'])

def add_path(file):
	sys.path.insert(len(sys.path), str(Path(file).resolve().parents[0]))

@activity_finish_popup
def facts_finder_start(i):
	custom = i['ff_file_custom_yml']
	if custom:
		add_path(custom)
	exec_facts_finder(
		log_files=i['ff_log_files'].split(";"),
		custom=custom,
		convert_to_cit=True,
		remove_cit_bkp=True,
		skip_txtfsm=True,
		new_suffix=i['ff_new_suffix'],
		output_folder=i['yf_output_folder'],
	)

@activity_finish_popup
def yaml_facts_start(i):
	exec_yaml_facts(
		log_files=i['ff_log_files'].split(";"),
		output_folder=i['yf_output_folder'],
	)


# ======================================================================================

FACTSFINDER_EVENT_FUNCS = {
	'ff_btn_start': facts_finder_start,
	'yf_btn_start': yaml_facts_start,
	'ff_file_custom_yml': update_cache_ff,
	'yf_output_folder': update_cache_ff,
}
FACTSFINDER_EVENT_UPDATERS = set()
FACTSFINDER_ITEM_UPDATERS = set()

FACTSFINDER_RETRACTABLES = {
	'ff_file_custom_yml', 'ff_log_files', 
}
