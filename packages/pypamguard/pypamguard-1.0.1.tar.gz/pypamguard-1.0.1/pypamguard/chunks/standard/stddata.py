from pypamguard.chunks.base.chunk import BaseChunk
import datetime
from pypamguard.utils.bitmap import Bitmap
from pypamguard.core.exceptions import *
from pypamguard.core.readers import *
from pypamguard.chunks.standard import StandardChunkInfo

DATA_FLAG_FIELDS = [
    "TIMEMILLISECONDS",
    "TIMENANOSECONDS",
    "CHANNELMAP",
    "UID",
    "STARTSAMPLE",
    "SAMPLEDURATION",
    "FREQUENCYLIMITS",
    "MILLISDURATION",
    "TIMEDELAYSECONDS",
    "HASBINARYANNOTATIONS",
    "HASSEQUENCEMAP",
    "HASNOISE",
    "HASSIGNAL",
    "HASSIGNALEXCESS"
]

class StandardDataMixin:
    def _initialize_stddata(self, *args, **kwargs):
        self.file_path: str = None
        self.millis: int = None
        self.date: datetime.datetime = None
        self.flags: Bitmap = None
        self.time_ns: int = None
        self.channel_map: Bitmap = None
        self.uid: int = None
        self.start_sample: int = None
        self.sample_duration: int = None
        self.freq_limits: float = None
        self.millis_duration: float = None
        self.time_delays: list[float] = None
        self.sequence_map: float = None
        self.noise: float = None
        self.signal: float = None
        self.signal_excess: float = None
    
    def _process_stddata(self, br: BinaryReader, chunk_info: StandardChunkInfo):
        self.file_path = chunk_info.file_path

        self.millis, self.date = br.timestamp_read()        
        self._filters.filter('daterange', self.date)

        self.flag_bitmap = br.bitmap_read(DTYPES.INT16, DATA_FLAG_FIELDS)
        set_flags = self.flag_bitmap.get_set_bits()
        
        if "TIMENANOSECONDS" in set_flags:
            self.time_ns = br.bin_read(DTYPES.INT64)
        
        if "CHANNELMAP" in set_flags:
            self.channel_map = br.bitmap_read(DTYPES.INT32)
        
        if "UID" in set_flags:
            self.uid = br.bin_read(DTYPES.INT64)
            self._filters.filter('uidrange', self.uid)
            self._filters.filter('uidlist', self.uid)
        
        if "STARTSAMPLE" in set_flags:
            self.start_sample = br.bin_read(DTYPES.INT64)
        
        if "SAMPLEDURATION" in set_flags:
            self.sample_duration = br.bin_read(DTYPES.INT32)
        
        if "FREQUENCYLIMITS" in set_flags:
            self.freq_limits = br.bin_read(DTYPES.FLOAT32, shape=(2,))

        if "MILLISDURATION" in set_flags:
            self.millis_duration = br.bin_read(DTYPES.FLOAT32)
        
        if "TIMEDELAYSECONDS" in set_flags:
            num_time_delays = br.bin_read(DTYPES.INT16)
            self.time_delays = br.bin_read(DTYPES.FLOAT32, shape=(num_time_delays,))

        if "HASSEQUENCEMAP" in set_flags:
            self.sequence_map = br.bin_read(DTYPES.INT32)

        if "HASNOISE" in set_flags:
            self.noise = br.bin_read(DTYPES.FLOAT32)

        if "HASSIGNAL" in set_flags:
            self.signal = br.bin_read(DTYPES.FLOAT32)

        if "HASSIGNALEXCESS" in set_flags:
            self.signal_excess = br.bin_read(DTYPES.FLOAT32)
            
        data_length = br.bin_read(DTYPES.INT32)
        if data_length <= 0: raise WarningException(br, chunk_info, self)
