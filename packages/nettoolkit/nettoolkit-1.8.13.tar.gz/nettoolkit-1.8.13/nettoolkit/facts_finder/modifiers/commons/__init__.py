"""Common Cisco / Juniper parsed database Modifiers (captured from capture_it/ntctemplate) """




from .modifier_commons import (
	KeyExchanger, DataFrameInit,
	Var, TableInterfaces, TableVrfs,
	)


__all__ = [
	'DataFrameInit', 'KeyExchanger', 
	'Var', 'TableInterfaces', 'TableVrfs', 
]