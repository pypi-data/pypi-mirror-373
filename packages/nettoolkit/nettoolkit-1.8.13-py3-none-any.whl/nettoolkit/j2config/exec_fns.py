
# ====================================================================================

import pandas as pd
from nettoolkit.nettoolkit_common import read_yaml_mode_us, print_banner, print_table, add_blankdict_key
from nettoolkit.j2config import PrepareConfig
from pathlib import *

# ====================================================================================

def get_host(file):
	return Path(file).stem.split("-clean")[0]

def get_custom_classes(custom):
	return {k: v for k, v in custom['j2_class_filters'].items() }

def get_custom_funcs(custom):
	return { v for k, v in custom['j2_functions_filters'].items() }

def exec_config_generation(
		data_files,
		template_file,
		output_folder,
		regional_file, 
		custom,
	):
	print_banner("Config Gen", 'green')
	regional_class, custom_classes, custom_funcs = None, {}, []
	try:
		if custom:
			custom = read_yaml_mode_us(custom)
			regional_class = custom['j2_regional']['regional_class']
	except Exception as e:
		raise Exception(f"[-] Custom Yaml Read failed or missing information")
	#
	device_log_dict = {}
	for data_file in data_files:
		if not data_file.endswith(".xlsx"): continue
		device = get_host(data_file)
		device_dict = add_blankdict_key(device_log_dict, device)
		print(f"[+] Generating Configuration for {device}", end="\t")
		try:
			PrCfg = PrepareConfig(
				data_file=data_file,
				jtemplate_file=template_file,
				output_folder=output_folder,
				regional_file=regional_file,
				regional_class=regional_class,
			)
			if custom:
				custom_classes = get_custom_classes(custom)
				custom_funcs = get_custom_funcs(custom)
			#
			PrCfg.custom_class_add_to_filter(**custom_classes)
			PrCfg.custom_module_methods_add_to_filter(*custom_funcs)
			#
			PrCfg.start()
			print(f"Done..")
			device_dict['Config Gen'] = 'Yes'
		except:
			print(f"Failed..")
			device_dict['Config Gen'] = 'No'

	print("[+] Configuration Generation All Task(s) Complete..")
	df = pd.DataFrame(device_log_dict).T
	print_table(df)	

# ====================================================================================
