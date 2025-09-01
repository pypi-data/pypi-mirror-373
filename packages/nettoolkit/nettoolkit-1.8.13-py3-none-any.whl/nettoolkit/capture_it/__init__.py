__doc__ = '''Device Output Capture Utility'''


from .executions import Execute_By_Login as capture
from .executions import Execute_By_Individual_Commands as capture_individual
from .executions import Execute_By_Excel as capture_by_excel
from ._detection import quick_display
from .cap_summary import LogSummary, TableReport
