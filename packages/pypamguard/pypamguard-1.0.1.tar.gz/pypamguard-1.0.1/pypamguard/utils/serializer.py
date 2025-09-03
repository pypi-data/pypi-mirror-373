import json, datetime, numpy as np
from pypamguard.utils.bitmap import Bitmap

def serialize(value):
    def serialize_list(l):
        if isinstance(l, list):
            return [serialize_list(i) for i in l]
        elif isinstance(l, np.ndarray):
            return serialize_list(l.tolist())
        return l

    if type(value) == np.ndarray: value = serialize_list(value)
    if type(value) == datetime.datetime: value = value.timestamp() * 1000
    if type(value) == Bitmap: value = value.bits
    return value

