from pypamguard.chunks.standard import StandardModule
from pypamguard.core.readers import *

class DbHtProcessing(StandardModule):

    _minimum_version = 2 # As at 9 Jul 2025

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rms: np.float32 = None
        self.zero_peak: np.float32 = None
        self.peak_peak: np.float32 = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        self.rms = br.bin_read((DTYPES.INT16, lambda x: x / 100))
        self.zero_peak = br.bin_read((DTYPES.INT16, lambda x: x / 100))
        self.peak_peak = br.bin_read((DTYPES.INT16, lambda x: x / 100))