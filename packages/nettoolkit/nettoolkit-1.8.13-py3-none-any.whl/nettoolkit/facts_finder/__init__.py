"""generate Network Devices (Switch/Router) facts from its configuration outputs.
"""

# ------------------------------------------------------------------------------

from .generators.merger import device
from .generators.merger import DeviceDB
from .rearrange import rearrange_tables
from .generators import get_necessary_cmds, get_absolute_command

from .clean import CleanFacts
from .exec_fns import exec_facts_finder


__all__ = [ 
	'device', 'DeviceDB',
	'CleanFacts',
	'rearrange_tables',
	'get_necessary_cmds', 'get_absolute_command',
	'exec_facts_finder',
]

