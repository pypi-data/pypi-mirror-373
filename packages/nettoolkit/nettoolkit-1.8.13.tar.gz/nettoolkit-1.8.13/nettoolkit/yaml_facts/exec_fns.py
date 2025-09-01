"""Description: 
"""

# ==============================================================================================
#  Imports
# ==============================================================================================
import pandas as pd
from nettoolkit.yaml_facts import YamlFacts
from pathlib import *
from nettoolkit.nettoolkit_common import print_banner, print_table, add_blankdict_key


# ==============================================================================================
#  Local Statics
# ==============================================================================================


# ==============================================================================================
#  Local Functions
# ==============================================================================================
def get_host(log_file):
	return Path(log_file).stem

def exec_yaml_facts(
	log_files,
	output_folder=None,
	):
	print_banner("Yaml Facts", 'yellow')
	device_log_dict = {}
	for log_file in log_files:
		if not log_file.endswith(".log"): continue
		device = get_host(log_file)
		print("[+] starting", device, "...", end='\t')
		device_dict = add_blankdict_key(device_log_dict, device)
		#
		try:
			YF = YamlFacts(log_file, output_folder)
			print(f"[+] Yaml File Generation Tasks Completed !! {device} !!")
			device_dict['yaml_facts generated'] = "Yes"
			device_dict['remark'] = ""
			if YF.unavailable_cmds:
				print(f"[-] {device}: Missing Captures {YF.unavailable_cmds}")
				device_dict['remark'] = f"Missing Captures {YF.unavailable_cmds}"

		except Exception as e:
			print(f"[-] Yaml File Generation failed...")
			print(e)
			device_dict['yaml_facts generated'] = "No"
			device_dict['remark'] = f"{e.splitlines()[0]}"
			continue
		#
	print("[+] Yaml Facts-Finder All Task(s) Complete..")
	df = pd.DataFrame(device_log_dict).T
	print_table(df)	


# ==============================================================================================
#  Classes
# ==============================================================================================



# ==============================================================================================
#  Main
# ==============================================================================================
if __name__ == '__main__':
	pass

# ==============================================================================================
