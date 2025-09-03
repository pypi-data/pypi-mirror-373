import io
from pypamguard.chunks.standard import StandardModule, StandardBackground, StandardChunkInfo
from pypamguard.chunks.base import BaseChunk
from pypamguard.core.readers import *
import zlib, math


class GeminiThresholdDetectorBackgroundHeader(BaseChunk):
    def _process(self, br: BinaryReader, chunk_info: StandardChunkInfo):
        self.m_id_char = br.bin_read(DTYPES.UINT8)
        self.m_version = br.bin_read(DTYPES.UINT8)
        self.m_length = br.bin_read(DTYPES.UINT32)
        self.m_timestamp = br.bin_read(DTYPES.FLOAT64)
        self.m_data_type = br.bin_read(DTYPES.UINT8)
        self.tm_device_id = br.bin_read(DTYPES.UINT16)
        self.m_node_id = br.bin_read(DTYPES.UINT16)
        self.spare = br.bin_read(DTYPES.UINT16)

class GeminiThresholdDetectorBackgroundGLFRecord(BaseChunk):
    def _process(self, br: BinaryReader, chunk_info: StandardChunkInfo):
        self.id1 = br.bin_read(DTYPES.UINT16)
        self.efef = hex(br.bin_read(DTYPES.UINT16))
        self.image_version = br.bin_read(DTYPES.UINT16)
        self.start_range = br.bin_read(DTYPES.UINT32)
        self.end_range = br.bin_read(DTYPES.UINT32)
        self.range_compression = br.bin_read(DTYPES.UINT16)
        self.start_bearing = br.bin_read(DTYPES.UINT32)
        self.end_bearing = br.bin_read(DTYPES.UINT32)
        if self.image_version == 3: skip = br.bin_read(DTYPES.UINT16)
        n_bearing = self.end_bearing - self.start_bearing
        n_range = self.end_range - self.start_range
        packed_size = br.bin_read(DTYPES.UINT32)
        zipped = br.bin_read(DTYPES.UINT8, shape=(packed_size,))
        full_len = n_range * n_bearing
        unzipped_bytes = bytearray(zlib.decompressobj().decompress(zipped))
        if len(unzipped_bytes) < full_len:
            n_range = math.floor(len(unzipped_bytes)/n_bearing)
            self.end_range = n_range
            unzipped_bytes = unzipped_bytes[:n_range * n_bearing]
        # Read the unzipped data into a BinaryReader by emulating a buffered reader
        # Note conversion to uint16 to allow for in-place arithmetic and the copy()
        # as np.ndarray from BinaryReader by default is immutable.
        unzipped_reader = BinaryReader(io.BytesIO(unzipped_bytes), br.report, endianess=BYTE_ORDERS.LITTLE_ENDIAN)
        self.image_data = np.uint16(unzipped_reader.bin_read(DTYPES.UINT8, shape=(n_range, n_bearing)).copy())
        is_neg = np.where(self.image_data < 0)[0]
        self.image_data.put(is_neg, self.image_data.take(is_neg) + 256)
        self.bearing_table = br.bin_read(DTYPES.FLOAT64, n_bearing)
        self.state_flags = br.bitmap_read(DTYPES.UINT32)
        self.modulation_frequency = br.bin_read(DTYPES.UINT32)
        self.beam_form_aperture = br.bin_read(DTYPES.FLOAT32)
        self.tx_time = br.bin_read(DTYPES.FLOAT64)
        self.ping_flags = br.bin_read(DTYPES.UINT16)
        self.sos_at_xd = br.bin_read(DTYPES.FLOAT32)
        self.percent_gain = br.bin_read(DTYPES.UINT16)
        self.chirp = br.bin_read(DTYPES.UINT8)
        self.sonar_type = br.bin_read(DTYPES.UINT8)
        self.platform = br.bin_read(DTYPES.UINT8)
        self.one_spare = br.bin_read(DTYPES.UINT8)
        self.dede = hex(br.bin_read(DTYPES.UINT16))
        self.max_range = self.end_range * self.sos_at_xd/2 /self.modulation_frequency
        t_offs = 723181 # 1 Jan 1980
        secs_per_day = 3600*24;
        self.tx_date = (self.tx_time / secs_per_day) + t_offs   

class GeminiThresholdDetectorBackground(StandardBackground):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        br.endianess = BYTE_ORDERS.LITTLE_ENDIAN

        self.head = GeminiThresholdDetectorBackgroundHeader()
        self.head._process(br, chunk_info)

        self.glf = GeminiThresholdDetectorBackgroundGLFRecord()
        self.glf._process(br, chunk_info)


class GeminiThresholdDetector(StandardModule):

    _background = GeminiThresholdDetectorBackground

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.n_points: np.int32 = None
        self.n_sonar: np.int8 = None
        self.sonar_ids: np.ndarray[np.int16] = None
        self.straight_length: np.float32 = None
        self.wobbly_length: np.float32 = None
        self.mean_occupancy: np.float32 = None
        self.time_millis: np.ndarray[np.int64] = None
        self.sonar_id: np.ndarray[np.int16] = None
        self.min_bearing: np.ndarray[np.float32] = None
        self.max_bearing: np.ndarray[np.float32] = None
        self.peak_bearing: np.ndarray[np.float32] = None
        self.min_range: np.ndarray[np.float32] = None
        self.max_range: np.ndarray[np.float32] = None
        self.peak_range: np.ndarray[np.float32] = None
        self.obj_size: np.ndarray[np.float32] = None
        self.occupancy: np.ndarray[np.float32] = None
        self.ave_value: np.ndarray[np.int16] = None
        self.tot_value: np.ndarray[np.int32] = None
        self.max_value: np.ndarray[np.int16] = None
        self.dates: np.ndarray[datetime.datetime] = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        self.n_points = br.bin_read(DTYPES.INT32)
        self.n_sonar = br.bin_read(DTYPES.INT8)
        self.sonar_ids = br.bin_read(DTYPES.INT16, shape=(self.n_sonar,))
        self.straight_length, self.wobbly_length, self.mean_occupancy = br.bin_read([DTYPES.FLOAT32, DTYPES.FLOAT32, DTYPES.FLOAT32])
        (
            self.time_millis,
            self.sonar_id,
            self.min_bearing,
            self.max_bearing,
            self.peak_bearing,
            self.min_range,
            self.max_range,
            self.peak_range,
            self.obj_size,
            self.occupancy,
            self.ave_value,
            self.tot_value,
            self.max_value,
        ) = br.bin_read([
            DTYPES.INT64,
            DTYPES.INT16,
            DTYPES.FLOAT32,
            DTYPES.FLOAT32,
            DTYPES.FLOAT32,
            DTYPES.FLOAT32,
            DTYPES.FLOAT32,
            DTYPES.FLOAT32,
            DTYPES.FLOAT32,
            DTYPES.FLOAT32,
            DTYPES.INT16,
            DTYPES.INT32,
            DTYPES.INT16,
        ], shape=(self.n_points,))
        self.dates = [BinaryReader.millis_to_timestamp(x) for x in self.time_millis]
