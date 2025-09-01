__doc__ = '''Compare IT Utility'''

__all__ = [ 
	"CompareText", "CompareExcelData", "get_string_diffs",
	"CompareConfig",
	]


from .diff import CompareText, CompareExcelData, get_string_diffs
from .compare_config import CompareConfig