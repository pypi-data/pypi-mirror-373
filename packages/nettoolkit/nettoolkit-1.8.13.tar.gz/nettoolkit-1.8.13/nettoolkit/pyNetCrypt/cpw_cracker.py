# """
# Cisco type-7 password breaker. base code derived open-source from web.
# """

import re
import random

xlat = [0x64, 0x73, 0x66, 0x64, 0x3b, 0x6b, 0x66, 0x6f, 0x41, 0x2c, 0x2e, 0x69, 0x79, 0x65, 0x77, 0x72, 0x6b, 0x6c, 0x64
, 0x4a, 0x4b, 0x44, 0x48, 0x53, 0x55, 0x42, 0x73, 0x67, 0x76, 0x63, 0x61, 0x36, 0x39, 0x38, 0x33, 0x34, 0x6e, 0x63,
0x78, 0x76, 0x39, 0x38, 0x37, 0x33, 0x32, 0x35, 0x34, 0x6b, 0x3b, 0x66, 0x67, 0x38, 0x37]

			
def decrypt_type7(ep):
	"""
	Cisco type-7 password decryptor
	"""
	dp = ''
	regex = re.compile('(^[0-9A-Fa-f]{2})([0-9A-Fa-f]+)')
	result = regex.search(ep)
	s, e = int(result.group(1)), result.group(2)
	for pos in range(0, len(e), 2):
		magic = int(e[pos] + e[pos+1], 16)
		if s <= 50:
			newchar = '%c' % (magic ^ xlat[s])
			s += 1
		if s == 51: s = 0
		dp += newchar
	return dp

def encrypt_type7(pt):
	"""
	Cisco type-7 password encryptor
	"""
	salt = random.randrange(0,15);
	ep = "%02x" % salt
	for i in range(len(pt)):
		ep += "%02x" % (ord(pt[i]) ^ xlat[salt])
		salt += 1
		if salt == 51: salt = 0
	return ep


def _update_pw_line(line, mask):
	# updates line if password string found, encrypt or mask it and return updated line	
	regex7 = re.compile('( 7 )([0-9A-Fa-f]+)($)')
	regex9 = re.compile('secret 9 ')
	regex5 = re.compile('secret 5 ')
	result7 = regex7.search(line)
	result9 = regex9.search(line)
	result5 = regex9.search(line)
	if mask:
		if result7: 
			line = line[:line.find(result7.group(0))] + " " + "XXXXXXXX\n"
		if result9: 
			line = line[:line.find(result9.group(0))] + "secret 9 XXXXXXXX\n"
		if result5:
			line = line[:line.find(result5.group(0))] + "secret 5 XXXXXXXX\n"
		line = _update_normal_pw_line_for_masking(line)
	elif result7:
		line = line[:line.find(result7.group(0))] + " " + decrypt_type7(result7.group(2)) + "\n"
	return line

def _update_normal_pw_line_for_masking(line):
	pw_Strings = (" secret ", " password ", " key ", " authentication-key ")
	for pw_Str in pw_Strings:
		if line.find(pw_Str) > -1:
			line = line[:line.find(pw_Str)] + pw_Str + "XXXXXXXX\n"
			break
	return line



def _file_passwords_update(input_file, output_file, pw_masking):
	with open(input_file, 'r') as f:
		lst = f.readlines()
	ulist = (_update_pw_line(line, pw_masking) for line in lst)
	cfg = "".join(ulist)
	with open(output_file, 'w') as f:
		f.write(cfg)

def decrypt_file_passwords(input_file, output_file):
	"""Decrypts all type 7 passwords found in input file, and create a new updated output file
	with plain text passwords

	Args:
		input_file (str): cisco configuration file name
		output_file (str): output file name
	"""
	_file_passwords_update(input_file, output_file, False)

def mask_file_passwords(input_file, output_file):
	"""Masks all type 7 and type 9 passwords found in cisco configuration input file,
	and creates a new updated output file with plain masked passwords

	Args:
		input_file (str): cisco configuration file name
		output_file (str): output file name
	"""
	_file_passwords_update(input_file, output_file, True)


if __name__ == '__main__':
	pass
