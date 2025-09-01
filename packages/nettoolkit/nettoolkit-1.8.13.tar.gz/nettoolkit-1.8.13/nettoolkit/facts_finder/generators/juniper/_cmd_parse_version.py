"""juniper show version command output parser """

# ------------------------------------------------------------------------------
from collections import OrderedDict

from nettoolkit.facts_finder.generators.commons import *
from .common import *
# ------------------------------------------------------------------------------

def get_version(cmd_op, *args):
	"""parser - show version command output

	Parsed Fields:
		* version
		* model

	Args:
		cmd_op (list, str): command output in list/multiline string.

	Returns:
		dict: output dictionary with parsed fields
	"""
	cmd_op = verifid_output(cmd_op)
	op_dict = OrderedDict()
	version, model = "", ""
	for l in cmd_op:
		if blank_line(l): continue
		if l.strip().startswith("#"): continue
		if l.startswith("Junos: "):  version = l.split()[-1]
		if l.startswith("Model: "): model = l.split()[-1]

	if not op_dict.get('version'): op_dict['version'] = version
	if not op_dict.get('model'): op_dict['model'] = model
	return {'op_dict': op_dict}
# ------------------------------------------------------------------------------
