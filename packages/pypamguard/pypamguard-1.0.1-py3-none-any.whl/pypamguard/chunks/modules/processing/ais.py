from pypamguard.core.readers import *
from pypamguard.chunks.standard import StandardModule

class AISProcessing(StandardModule):

    _minimum_version = 1 # As at 9 Jul 2025

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mmsi_number: np.int32 = None
        self.fill_bits: np.int16 = None
        self.char_data: str = None
        self.ais_channel: str = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        self.mmsi_number = br.bin_read(DTYPES.INT32)
        self.fill_bits = br.bin_read(DTYPES.INT16)
        self.char_data = br.string_read()
        self.ais_channel = br.string_read()
