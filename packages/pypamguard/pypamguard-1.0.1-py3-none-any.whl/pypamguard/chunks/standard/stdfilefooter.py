import io

from . import StandardChunkInfo
from pypamguard.chunks.generics import GenericFileHeader, GenericFileFooter
from pypamguard.core.readers import *

class StandardFileFooter(GenericFileFooter):
    
    def __init__(self, file_header: GenericFileHeader):
        super().__init__(file_header)
        self.file_footer: str = None
        self.n_objects: int = None
        self.data_date_raw: np.int64 = None
        self.data_date: datetime.datetime = None
        self.analysis_date_raw: np.int64 = None
        self.analysis_date: datetime.datetime = None
        self.end_sample: np.int64 = None
        self.lowest_uid: np.int64 = None
        self.highest_uid: np.int64 = None
        self.file_length: np.int64 = None
        self.end_reason: np.int32 = None

    def _process(self, br: BinaryReader, chunk_info: StandardChunkInfo):
        self.file_path = chunk_info.file_path
        self.length = chunk_info.length
        self.identifier = chunk_info.identifier

        self.n_objects = br.bin_read(DTYPES.INT32)
        self.data_date_raw, self.data_date = br.timestamp_read()
        self.analysis_date_raw, self.analysis_date = br.timestamp_read()
        self.end_sample = br.bin_read(DTYPES.INT64)
        if self._file_header.file_format >= 3:
            self.lowest_uid = br.bin_read(DTYPES.INT64)
            self.highest_uid = br.bin_read(DTYPES.INT64)
        self.file_length = br.bin_read(DTYPES.INT64)
        self.end_reason = br.bin_read(DTYPES.INT32)