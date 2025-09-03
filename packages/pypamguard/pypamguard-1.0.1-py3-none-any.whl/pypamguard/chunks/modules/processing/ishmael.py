from pypamguard.chunks.standard import StandardModule, StandardChunkInfo
from pypamguard.core.readers import *
from pypamguard.logger import logger

class IshmaelDetections(StandardModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.peak_height: np.float64 = None
        self.time_sample: np.float64 = None

    def _process(self, br: BinaryReader, chunk_info: StandardChunkInfo):
        super()._process(br, chunk_info)
        # Ishmael detections contain simply standard module data
        # NOTE: missing 20 bytes of data. Not accounted for in Matlab code.
        self.peak_height = br.bin_read(DTYPES.FLOAT64)
        self.time_sample = br.bin_read(DTYPES.FLOAT64)


class IshmaelData(StandardModule):

    _minimum_version = 2

    def _process(self, br: BinaryReader, chunk_info: StandardChunkInfo):
        super()._process(br, chunk_info)
        n_det = br.bin_read(DTYPES.INT32)
        n_det2 = br.bin_read(DTYPES.INT32)
        self.data = br.bin_read(DTYPES.FLOAT64, shape=(n_det, n_det2))