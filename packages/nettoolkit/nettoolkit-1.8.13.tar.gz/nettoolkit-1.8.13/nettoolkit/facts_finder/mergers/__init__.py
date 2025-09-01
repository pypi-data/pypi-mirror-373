"""Cisco/Juniper - facts generator and facts modifier databases merger """


from .cisco import CiscoMerge
from .juniper import JuniperMerge


__all__ = [
	'CiscoMerge', 'JuniperMerge'
]

