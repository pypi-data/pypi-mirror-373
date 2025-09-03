from pypamguard.chunks.standard import StandardModule
from pypamguard.core.readers import *

class DIFARProcessing(StandardModule):

    _minimum_version = 2 # as at 9 Jul 2025

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clip_start: np.int16 = None
        self.display_sample_rate: np.float32 = None
        self.demuxed_length: np.int32 = None
        self.amplitude: np.float32 = None
        self.gain: np.float32 = None
        self.sel_angle: np.float32 = None
        self.sel_freq: np.float32 = None
        self.species_code: str = None
        self.tracked_group: str = None
        self.max_val: np.float32 = None
        self.demux_data: np.ndarray = None
        self.num_matches: np.int16 = None
        self.latitude: np.float32 = None
        self.longitude: np.float32 = None
        self.errors: np.ndarray = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        self.clip_start = br.bin_read(DTYPES.INT64)
        self.display_sample_rate = br.bin_read(DTYPES.FLOAT32)
        self.demuxed_length = br.bin_read(DTYPES.INT32)
        self.amplitude = br.bin_read(DTYPES.FLOAT32)
        self.gain = br.bin_read(DTYPES.FLOAT32)
        self.sel_angle = br.bin_read(DTYPES.FLOAT32)
        self.sel_freq = br.bin_read(DTYPES.FLOAT32)
        self.species_code = br.string_read()
        self.tracked_group = br.string_read()
        self.max_val = br.bin_read(DTYPES.FLOAT32)
        if self.demuxed_length == 0: self.demux_data = 0
        else: self.demux_data = br.bin_read((DTYPES.INT16, lambda x: x * self.max_val / 32767), shape=(3, self.demuxed_length))
        self.num_matches = br.bin_read(DTYPES.INT16)
        if self.num_matches > 0:
            self.latitude = br.bin_read(DTYPES.FLOAT32)
            self.longitude = br.bin_read(DTYPES.FLOAT32)
            self.errors = br.bin_read(DTYPES.FLOAT32, shape=(2,))
            self.match_chan, self.match_time = br.bin_read([DTYPES.INT16, DTYPES.INT64], shape=(self.num_matches))
        else:
            self.latitude = 0
            self.longitude = 0
            self.errors = [0, 0, 0]
