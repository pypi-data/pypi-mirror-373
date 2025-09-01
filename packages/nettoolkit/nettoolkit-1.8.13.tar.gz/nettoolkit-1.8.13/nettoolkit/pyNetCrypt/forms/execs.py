
from nettoolkit.nettoolkit.forms.formitems import *
from nettoolkit.nettoolkit_common import read_yaml_mode_us, create_folders, open_text_file, open_excel_file, open_folder
from pathlib import *
import sys

from nettoolkit.pyNetCrypt import decrypt_type7, encrypt_type7, decrypt_file_passwords, mask_file_passwords
from nettoolkit.pyNetCrypt import juniper_decrypt, juniper_encrypt, decrypt_doller9_file_passwords, mask_doller9_file_passwords
from nettoolkit.pyNetCrypt import get_md5


# ================================ [ NetCrypt ] ========================================

def exec_netcrypt_file_input_open(i):
	open_folder(i['netcrypt_file'])

def netcrypt_cisco_enc_start(obj, i):
	try:
		_pw = encrypt_type7(i['netcrypt_input_pw'])
		obj.event_update_element(netcrypt_output_pw={'value': _pw})	
	except:
		obj.event_update_element(netcrypt_output_pw={'value': "invalid"})	

def netcrypt_cisco_dec_start(obj, i):
	try:
		_pw = decrypt_type7(i['netcrypt_input_pw'])
		obj.event_update_element(netcrypt_output_pw={'value': _pw})	
	except:
		obj.event_update_element(netcrypt_output_pw={'value': "invalid"})	

def netcrypt_juniper_enc_start(obj, i):
	try:
		_pw = juniper_encrypt(i['netcrypt_input_pw'])
		obj.event_update_element(netcrypt_output_pw={'value': _pw})	
	except:
		obj.event_update_element(netcrypt_output_pw={'value': "invalid"})	

def netcrypt_juniper_dec_start(obj, i):
	try:
		_pw = juniper_decrypt(i['netcrypt_input_pw'])
		obj.event_update_element(netcrypt_output_pw={'value': _pw})	
	except:
		obj.event_update_element(netcrypt_output_pw={'value': "invalid"})	


@activity_finish_popup
def netcrypt_file_dec_start(obj, i):
	if not i['netcrypt_file']: return 
	input_files = i['netcrypt_file'].split(";")
	for input_file in input_files:
		if i['netcrypt_file_dec_overwrite']:
			output_file = input_file
		else:
			output_file = input_file[:-4] + '-pw-decrypted.' + input_file[-3:]
		with open(input_file, 'r') as f:
			lines = f.readlines()
		f = None
		for line in lines:
			if line.startswith("!"): f = decrypt_file_passwords
			if line.startswith("#"): f = decrypt_doller9_file_passwords
			if f: break
		f(input_file, output_file)
		op = f"File Wrote: {output_file}"
		obj.event_update_element(netcrypt_output_pw={'value': op})	

@activity_finish_popup
def netcrypt_file_mask_start(obj, i):
	if not i['netcrypt_file']: return 
	input_files = i['netcrypt_file'].split(";")
	for input_file in input_files:
		if i['netcrypt_file_dec_overwrite']:
			output_file = input_file
		else:
			output_file = input_file[:-4] + '-pw-masked.' + input_file[-3:]
		with open(input_file, 'r') as f:
			lines = f.readlines()
		f = None
		for line in lines:
			if line.startswith("!"): f = mask_file_passwords
			if line.startswith("#"): f = mask_doller9_file_passwords
			if f: break
		f(input_file, output_file)
		op = f"File Wrote: {output_file}"
		obj.event_update_element(netcrypt_output_pw={'value': op})	

def netcrypt_file_hash_start(obj, i):
	if not i['md5_generate_file']: return 
	_hash = get_md5(i['md5_generate_file'])
	obj.event_update_element(netcrypt_output_pw={'value': _hash})	


# ======================================================================================

CRYPT_EVENT_FUNCS = {
	'netcrypt_juniper_dec_btn_start': netcrypt_juniper_dec_start,
	'netcrypt_juniper_enc_btn_start': netcrypt_juniper_enc_start,
	'netcrypt_cisco_dec_btn_start': netcrypt_cisco_dec_start,
	'netcrypt_cisco_enc_btn_start': netcrypt_cisco_enc_start,
	'netcrypt_file_dec_btn_start': netcrypt_file_dec_start,
	'netcrypt_file_mask_btn_start': netcrypt_file_mask_start,
	'netcrypt_file_hash_btn_start': netcrypt_file_hash_start,

	'netcrypt_file_input_open': exec_netcrypt_file_input_open,
}

CRYPT_EVENT_UPDATERS = {
	'netcrypt_juniper_dec_btn_start', 'netcrypt_juniper_enc_btn_start',
	'netcrypt_cisco_dec_btn_start', 'netcrypt_cisco_enc_btn_start',
	'netcrypt_file_dec_btn_start', 'netcrypt_file_mask_btn_start',
	'netcrypt_file_hash_btn_start',

}
CRYPT_ITEM_UPDATERS = set()
CRYPT_RETRACTABLES = {
	'netcrypt_file', 'netcrypt_input_pw', 'netcrypt_output_pw'

}
