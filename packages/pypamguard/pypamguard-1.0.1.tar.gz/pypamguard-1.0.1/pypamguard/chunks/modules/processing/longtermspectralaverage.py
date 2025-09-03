from pypamguard.core.readers import *
from pypamguard.chunks.standard import StandardModule, StandardModuleHeader
from pypamguard.chunks.generics import GenericChunkInfo

class LongTermSpectralAverageHeader(StandardModuleHeader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _process(self, br: BinaryReader, chunk_info: GenericChunkInfo):
        super()._process(br, chunk_info)

        if self.binary_length != 0:
            self.fft_length = br.bin_read(DTYPES.INT32)
            self.fft_hop = br.bin_read(DTYPES.INT32)
            self.interval_seconds = br.bin_read(DTYPES.INT32)

class LongTermSpectralAverage(StandardModule):

    _header = LongTermSpectralAverageHeader
    _minimum_version = 2

    a = 127 * 2 / np.log(32767)
    b = -127

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.end_millis: int = None
        self.end_date: datetime = None
        self.n_fft: np.int32 = None
        self.max_val: np.float32 = None
        self.bytes_data: np.ndarray = None
        self.data: np.ndarray = None


    def _process(self, br: BinaryReader, chunk_info: GenericChunkInfo):
        super()._process(br, chunk_info)
        
        self.end_date, self.end_millis = br.timestamp_read()

        self.n_fft = br.bin_read(DTYPES.INT32)
        self.max_val = br.bin_read(DTYPES.FLOAT32)

        # The type of the data is int8 but it needs to be promoted to int16
        # to support the arithmetic in the line after.
        self.data = br.bin_read((DTYPES.INT8, lambda x: np.exp((x.astype(np.int16,copy=False) - self.b) / self.a) * self.max_val / 32767), shape=(int(self._module_header.fft_length/2),))
