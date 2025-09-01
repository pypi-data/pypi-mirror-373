"""generate Network Devices (Switch/Router) facts from its configuration outputs.
"""

from .merger import device
from .merger import DeviceDB
from .facts_gen import FactsGen, get_necessary_cmds, get_absolute_command

__all__ = [ 
	'device', 'DeviceDB', 'FactsGen', 'get_necessary_cmds', 'get_absolute_command',
]
