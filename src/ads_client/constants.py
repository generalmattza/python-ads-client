import pyads

ERROR_STRUCTURE = (
    ("status", pyads.PLCTYPE_BOOL, 1),
    ("code", pyads.PLCTYPE_DINT, 1),
    ("source", pyads.PLCTYPE_STRING, 1),
)

MAGNET_STRUCTURE = (
    ("Enable", pyads.PLCTYPE_BOOL, 1),
    ("Driver Safety Limit Current (A)", pyads.PLCTYPE_INT, 1),
    ("Max Driver Current (A)", pyads.PLCTYPE_INT, 1),
    ("Feedback Max (A)", pyads.PLCTYPE_INT, 1),
    ("Desired Current (A)", pyads.PLCTYPE_INT, 1),
    ("On time (ms)", pyads.PLCTYPE_INT, 1),
    ("Time offset (ms)", pyads.PLCTYPE_INT, 1),
)

TDKLOCAL_STRUCTURE = (
    ("HV Enable", pyads.PLCTYPE_BOOL, 1),
    ("Inhibit", pyads.PLCTYPE_BOOL, 1),
)
TDK_STRUCTURE = (
    ("Name", pyads.PLCTYPE_STRING, 1),
    ("Type", pyads.PLCTYPE_STRING, 1),
    ("Total Load (uF)", pyads.PLCTYPE_REAL, 1),
    ("Rated Voltage (V)", pyads.PLCTYPE_REAL, 1),
    ("Max Current (A)", pyads.PLCTYPE_REAL, 1),
    ("wLCA", pyads.PLCTYPE_BOOL, 1),
)
