from enum import Enum
import numpy as np

# Arguments that can be used when reading
TIME_RANGE = "timerange"
UID_RANGE = "uidrange"
UID_LIST = "uidlist"
FILTER = "filter"
CHANNEL = "channel"

DEFAULT_BUFFER_SIZE = 1024

class BYTE_ORDERS(Enum):
    LITTLE_ENDIAN = "<"
    BIG_ENDIAN = ">"


class IdentifierType(Enum):
    FILE_HEADER = -1
    FILE_FOOTER = -2
    MODULE_HEADER = -3
    MODULE_FOOTER = -4
    IGNORE = -5
    FILE_BACKGROUND = -6

class DTYPES(Enum):
    INT8 = np.dtype(np.int8)
    UINT8 = np.dtype(np.uint8)
    INT16 = np.dtype(np.int16)
    UINT16 = np.dtype(np.uint16)
    INT32 = np.dtype(np.int32)
    UINT32 = np.dtype(np.uint32)
    INT64 = np.dtype(np.int64)
    UINT64 = np.dtype(np.uint64)
    FLOAT32 = np.dtype(np.float32)
    FLOAT64 = np.dtype(np.float64)
