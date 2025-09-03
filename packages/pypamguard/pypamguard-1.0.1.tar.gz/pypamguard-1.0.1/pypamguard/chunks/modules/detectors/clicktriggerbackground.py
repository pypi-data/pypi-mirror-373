from pypamguard.chunks.standard import StandardModule, StandardChunkInfo, StandardModuleHeader
from pypamguard.core.readers import *

class ClickTriggerBackgroundHeader(StandardModuleHeader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        if self.binary_length != 0:
            self.channel_map = br.bitmap_read(DTYPES.INT32)
            self.n_chan = len(self.channel_map.get_set_bits())
            self.calibration = br.bin_read(DTYPES.FLOAT32, shape=(self.n_chan,))


class ClickTriggerBackground(StandardModule):

    _header = ClickTriggerBackgroundHeader
    _minimum_version = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scale: np.float32 = None
        self.raw_levels: np.ndarray[np.float64] = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        self.scale = br.bin_read(DTYPES.FLOAT32)
        self.raw_levels = br.bin_read((DTYPES.INT16, lambda x: x / self.scale), shape=(self._module_header.n_chan,))
        