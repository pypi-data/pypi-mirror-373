


# ======================================================================================================
# Some Known Exceptions
# ======================================================================================================

def Report_Bug_cisco_CSCsq51052(device):
	msg = f"  [-] Device connection failed for device {device}. Possible Cisco Bug ID [CSCsq51052]. Re-configure device with [ip ssh version 2] manually and retry."
	print(msg)
	return msg
