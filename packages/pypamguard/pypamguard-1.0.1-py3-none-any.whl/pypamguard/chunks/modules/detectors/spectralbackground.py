from pypamguard.chunks.standard import StandardBackground
from pypamguard.core.readers import *

class SpectralBackground(StandardBackground):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.first_bin: np.int32 = None
        self.noise_len: np.int32 = None
        self.background: np.ndarray[np.float32] = None

    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)

        self.first_bin = br.bin_read(DTYPES.INT32)
        self.noise_len = br.bin_read(DTYPES.INT32)
        self.background = br.bin_read(DTYPES.FLOAT32, shape=(self.noise_len,))