from pypamguard.chunks.standard import StandardModule
from pypamguard.core.readers import *

class SpermWhaleIPI(StandardModule):

    _minimum_version = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent_uid: np.int64 = None
        self.ipi: np.float32 = None
        self.ipi_amplitude: np.float32 = None
        self.sample_rate: np.float32 = None
        self.max_val: np.float32 = None
        self.echo_len: np.int32 = None
        self.echo_data: np.ndarray = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        
        self.parent_uid = br.bin_read(DTYPES.INT64)
        self.ipi = br.bin_read(DTYPES.FLOAT32)
        self.ipi_amplitude = br.bin_read(DTYPES.FLOAT32)
        self.sample_rate = br.bin_read(DTYPES.FLOAT32)
        self.max_val = br.bin_read(DTYPES.FLOAT32)
        self.echo_len = br.bin_read(DTYPES.INT32)
        self.echo_data = br.bin_read((DTYPES.INT16, lambda x: x * self.max_val / 32767), shape=(self.echo_len,))
