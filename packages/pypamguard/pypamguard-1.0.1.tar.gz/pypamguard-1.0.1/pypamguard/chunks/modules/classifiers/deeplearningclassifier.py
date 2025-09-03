from pypamguard.chunks.standard import StandardModule, StandardChunkInfo
from pypamguard.core.readers import *

class DLCModels(StandardModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.type: np.int8 = None
        self.is_binary: np.uint8 = None
        self.scale: np.float32 = None
        self.n_species: np.int16 = None
        self.predictions: np.ndarray[np.float32] = None
        self.n_class: np.int16 = None

    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)

        self.type = br.bin_read(DTYPES.INT8)
        self.is_binary = br.bin_read(DTYPES.UINT8) # logical
        self.scale = br.bin_read(DTYPES.FLOAT32)
        self.n_species = br.bin_read(DTYPES.INT16)
        self.predictions = br.bin_read((DTYPES.INT16, lambda x: x / self.scale), shape=(self.n_species,))
        self.n_class = br.bin_read(DTYPES.INT16)
        br.bin_read(DTYPES.INT16, shape=(self.n_class,)) # Not too sure what this is...

class DLCDetections(StandardModule):

    _minimum_version = 2 # As at 9 Jul 2025

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.n_chan: np.int16 = None
        self.n_samps: np.int32 = None
        self.scale: np.float32 = None
        self.wave: np.ndarray[np.float32] = None

    def _process(self, br: BinaryReader, chunk_info: StandardChunkInfo):
        super()._process(br, chunk_info)
        self.n_chan = br.bin_read(DTYPES.INT16)
        self.n_samps = br.bin_read(DTYPES.INT32)
        self.scale = br.bin_read((DTYPES.FLOAT32, lambda x: 1/x))
        self.wave = br.bin_read((DTYPES.INT8, lambda x: x / self.scale), shape=(self.n_chan, self.n_samps))
