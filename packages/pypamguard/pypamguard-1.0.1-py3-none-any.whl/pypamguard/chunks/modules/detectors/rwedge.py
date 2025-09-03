from pypamguard.chunks.standard import StandardModule
from pypamguard.core.readers import DTYPES, BinaryReader
import numpy as np

class RWEdgeDetector(StandardModule):

    def __init__(self, file_header, module_header, filters):
        super().__init__(file_header, module_header, filters)

        self.type: int = None
        self.signal: float = None
        self.noise: float = None
        self.n_slices: int = None
        self.slice_nums: np.ndarray = None
        self.lo_freqs: np.ndarray = None
        self.peak_freqs: np.ndarray = None
        self.hi_freqs: np.ndarray = None
        self.peak_amp: np.ndarray = None

    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)

        self.type = br.bin_read(DTYPES.INT16)
        self.signal = br.bin_read(DTYPES.FLOAT32)
        self.noise = br.bin_read(DTYPES.FLOAT32)
        self.n_slices = br.bin_read(DTYPES.INT16)

        (self.slice_nums, self.lo_freqs, self.peak_freqs, self.hi_freqs, self.peak_amp) = br.bin_read([DTYPES.INT16, DTYPES.INT16, DTYPES.INT16, DTYPES.INT16, DTYPES.FLOAT32], (self.n_slices,))
