from pypamguard.chunks.standard import StandardModule, StandardModuleHeader
from pypamguard.core.readers import *

class NoiseMonitorHeader(StandardModuleHeader):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.n_bands: np.int16 = None
        self.stats_types: np.int16 = None
        self.lo_edges: np.ndarray = None
        self.hi_edges: np.ndarray = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        if self.binary_length != 0:
            self.n_bands = br.bin_read(DTYPES.INT16)
            self.stats_types = br.bin_read(DTYPES.INT16)
            self.lo_edges = br.bin_read(DTYPES.FLOAT32, shape=(self.n_bands,))
            self.hi_edges = br.bin_read(DTYPES.FLOAT32, shape=(self.n_bands,))

class NoiseMonitor(StandardModule):

    _minimum_version = 2 # As at 9 Jul 2025
    _header = NoiseMonitorHeader

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.i_chan: np.int16 = None
        self.n_bands: np.int16 = None
        self.n_measures: np.int16 = None
        self.noise: np.ndarray = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)

        self.i_chan = br.bin_read(DTYPES.INT16)
        self.n_bands = br.bin_read(DTYPES.INT16)
        self.n_measures = br.bin_read(DTYPES.INT16)
        self.noise = br.bin_read((DTYPES.INT16, lambda x: x / 100), shape=(self.n_bands, self.n_measures))
