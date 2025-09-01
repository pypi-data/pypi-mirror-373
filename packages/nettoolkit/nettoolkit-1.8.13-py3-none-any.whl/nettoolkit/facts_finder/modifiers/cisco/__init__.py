"""Cisco parsed database Modifiers (captured from capture_it/ntctemplate) """



from .cisco_var import VarCisco
from .cisco_tables import TableInterfaceCisco
from .cisco_vrfs import TableVrfsCisco
from .merger import cisco_modifier


__all__ = [
	'VarCisco', 
	'TableInterfaceCisco',
	'TableVrfsCisco',
	'cisco_modifier',
]


