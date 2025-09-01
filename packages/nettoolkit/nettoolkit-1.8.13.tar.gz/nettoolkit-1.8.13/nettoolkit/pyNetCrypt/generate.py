


import hashlib
# ------------------------------------------------------------------------------


def get_md5(file):
	"""create and return md5 hash for given file

	Args:
		file (str): input file

	Returns:
		str: MD5 hash value
	"""	
	chunk = 8192
	with open(file, 'rb') as f:
		_hash = hashlib.md5()
		c = f.read(chunk)
		while c:
			_hash.update(c)
			c = f.read(chunk)
	return _hash.hexdigest()

def str_hash(s):
	"""create and return md5 hash for given string

	Args:
		s (str): input string

	Returns:
		str: MD5 hash value
	"""		
	chunk = 8192
	_hash = hashlib.md5()
	start, end = 0, chunk
	while True:
		_s = s[start: end]
		_hash.update(str.encode(_s))
		start += chunk
		end += chunk
		if start > chunk: break
	return _hash.hexdigest()
