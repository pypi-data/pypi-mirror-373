from pypamguard.chunks.standard import StandardModule, StandardModuleFooter, StandardBackground
from pypamguard.core.readers import *
from pypamguard.logger import logger

class ClickDetectorFooter(StandardModuleFooter):

    def __init__(self, file_header, module_header):
        super().__init__(file_header, module_header)

        self.types_count_length: int = None
        self.types_count: list[int] = None

    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)

        if self.binary_length > 0:
            self.types_count_length = br.bin_read(DTYPES.INT16)
            if self.types_count_length > 0: self.types_count = br.bin_read(DTYPES.INT32, shape=(self.types_count_length,))
            else: self.types_count = []

class ClickDetectorBackgound(StandardBackground):

    _minimum_version = 2

    def __init__(self, file_header, module_header, filters):
        super().__init__(file_header, module_header, filters)

        self.noise_len: np.int16 = None
        self.background: np.ndarray[np.float32] = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        
        self.noise_len = br.bin_read(DTYPES.INT16)
        self.background = br.bin_read(DTYPES.FLOAT32, shape=(self.noise_len,))

class ClickDetector(StandardModule):

    _minimum_version = 2 # As at 9 Jul 2025
    _footer = ClickDetectorFooter
    _background = ClickDetectorBackgound

    def __init__(self, file_header, module_header, filters):
        super().__init__(file_header, module_header, filters)
        
        self.start_sample: int = None
        self.channel_map: Bitmap = None
        self.trigger_map: Bitmap = None
        self.type: int = None
        self.flags: Bitmap = None
        self.delays: float = None
        self.angles: np.ndarray = np.array([])
        self.angle_errors: np.ndarray = np.array([])
        self.duration: int = None
        self.wave: np.ndarray = None

    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)

        self.n_chan = len(self.channel_map.get_set_bits())

        if self._module_header.version <= 3:
            self.start_sample, self.channel_map = br.bin_read([DTYPES.INT64, DTYPES.INT32])

        self.trigger_map, self.type = br.bin_read([DTYPES.INT32, DTYPES.INT16])
        self.flags = br.bitmap_read(DTYPES.INT32)
        
        if self._module_header.version <= 3:
            n_delays = br.bin_read(DTYPES.INT16)
            if n_delays: self.delays = br.bin_read(DTYPES.FLOAT32, shape=n_delays)
        
        n_angles = br.bin_read(DTYPES.INT16)
        if n_angles: self.angles = br.bin_read(DTYPES.FLOAT32, shape=n_angles)
        
        n_angle_errors = br.bin_read(DTYPES.INT16)
        if n_angle_errors: self.angle_errors = br.bin_read(DTYPES.FLOAT32, shape=n_angle_errors)
        
        if self._module_header.version <= 3: self.duration = br.bin_read(DTYPES.UINT16)
        else: self.duration = self.sample_duration
        
        max_val = br.bin_read(DTYPES.FLOAT32)
        def normalize_wave(x): return np.round(x * max_val / 127, 4)
        self.wave = br.bin_read((DTYPES.INT8, normalize_wave), shape=(self.n_chan, self.duration))
