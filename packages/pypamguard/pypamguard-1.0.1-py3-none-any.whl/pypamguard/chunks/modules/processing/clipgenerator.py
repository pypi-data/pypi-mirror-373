from pypamguard.chunks.standard import StandardModule
from pypamguard.core.readers import *


class ClipGenerator(StandardModule):

    _minimum_version = 3 # As at 10 Jul 2025

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.trigger_millis: np.int64 = None
        self.file_name: str = None
        self.trigger_name: str = None
        self.trigger_uid: np.int64 = None
        self.n_chan: np.int16 = None
        self.n_samps: np.int32 = None
        self.scale: np.float32 = None
        self.wave: np.ndarray[np.floating] = None
    
    def _process(self, br, chunk_info):
        
        super()._process(br, chunk_info)

        self.trigger_millis = br.bin_read(DTYPES.INT64)
        self.file_name = br.string_read()
        self.trigger_name = br.string_read()
        self.trigger_uid = br.bin_read(DTYPES.INT64)
        if chunk_info.identifier == 2:
            self.n_chan = br.bin_read(DTYPES.INT16)
            self.n_samps = br.bin_read(DTYPES.INT32)
            self.scale = br.bin_read((DTYPES.FLOAT32, lambda x: 1/x))
            self.wave = br.bin_read((DTYPES.INT8, lambda x: np.int16(x) * self.scale), shape=(self.n_chan, self.n_samps))
