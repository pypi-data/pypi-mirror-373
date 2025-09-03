from pypamguard.chunks.base import BaseChunk
from pypamguard.core.readers import *

class Location(BaseChunk):
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.height = None
        self.error = None
    
    def _process(self, br, *args, **kwargs):
        self.latitude = br.bin_read(DTYPES.FLOAT64)
        self.longitude = br.bin_read(DTYPES.FLOAT64)
        self.height = br.bin_read(DTYPES.FLOAT32)
        self.error = br.string_read()
