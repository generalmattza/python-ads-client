import pyads

ERROR_STRUCTURE = (
    ("status", pyads.PLCTYPE_BOOL, 1),
    ("code", pyads.PLCTYPE_DINT, 1),
    ("source", pyads.PLCTYPE_STRING, 1),
)