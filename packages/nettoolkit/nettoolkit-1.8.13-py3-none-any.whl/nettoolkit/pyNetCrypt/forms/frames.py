
from nettoolkit.nettoolkit.forms.formitems import *

# ============================ [ Juniper ] ======================================= #

def netcrypt_frame():
	"""tab display

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('Password Encryption/Decryption', font=('TimesNewRoman', 12), text_color="orange") ],

		[sg.Text('Password string:', text_color="black"), sg.InputText(key='netcrypt_input_pw'), ],
		[sg.Text('\t'), sg.Button("Cisco Encrypt (7)", size=(20,1), change_submits=True, key='netcrypt_cisco_enc_btn_start', button_color="darkblue"),
		 sg.Text(''), sg.Button("Juniper Encrypt ($9)", size=(20,1), change_submits=True, key='netcrypt_juniper_enc_btn_start', button_color="darkblue"),],
		[sg.Text('\t'),   sg.Button("Cisco Decrypt (7)", size=(20,1), change_submits=True, key='netcrypt_cisco_dec_btn_start', button_color="darkblue"),
		 sg.Text(''),   sg.Button("Juniper Decrypt ($9)", size=(20,1), change_submits=True, key='netcrypt_juniper_dec_btn_start', button_color="darkblue"),],
		# under_line(80),

		[sg.Text('File Password - Decrypt / Mask', font=('TimesNewRoman', 12), text_color="orange") ],

		[sg.Text('Input file(s):',  text_color="black"), 
		 sg.InputText(key='netcrypt_file'), sg.FilesBrowse(),
		 sg.Button("open", change_submits=True, key='netcrypt_file_input_open', button_color="darkgrey"),],

		[sg.Checkbox('overwrite',	    key='netcrypt_file_dec_overwrite',        default=False,  text_color='black'),],

		[sg.Text('\t'),
		 sg.Button("Decrypt Passwords", size=(20,1),  change_submits=True, key='netcrypt_file_dec_btn_start', button_color="darkblue"),
		 sg.Button("Mask Passwords", size=(20,1),  change_submits=True, key='netcrypt_file_mask_btn_start', button_color="darkblue")],


		# under_line(80),
		[sg.Text('File MD5 Hash Calculator', font=('TimesNewRoman', 12), text_color="orange") ],
		[sg.Text('Input file:',  text_color="black"), 
		 sg.InputText(key='md5_generate_file'), sg.FileBrowse(),],
		[sg.Button("Generate MD5 Hex", size=(20,1),  change_submits=True, key='netcrypt_file_hash_btn_start', button_color="darkblue"),],

		under_line(80),

		[sg.Text('Result:', background_color='lightyellow', text_color="black"), sg.InputText(key='netcrypt_output_pw',  text_color="darkred",  disabled=True), ],



		])

# ========================================================================
CRYPT_FRAMES = {
	'Cryptology': netcrypt_frame(),
}