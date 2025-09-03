import io

from pypamguard.chunks.generics import GenericFileHeader
from pypamguard.core.readers import *

class StandardFileHeader(GenericFileHeader):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def _process(self, br: BinaryReader, chunk_info):
        self.file_path = chunk_info.file_path
        self.length = chunk_info.length
        self.identifier = chunk_info.identifier

        self.file_format: int = br.bin_read(DTYPES.INT32)
        self.pamguard: str = br.nstring_read(12)
        self.version: str = br.string_read()
        self.branch: str = br.string_read()
        self.data_date_raw, self.data_date = br.timestamp_read()
        self.analysis_date_raw, self.analysis_date = br.timestamp_read()
        self.start_sample: int = br.bin_read(DTYPES.INT64)
        self.module_type: str = br.string_read()
        self.module_name: str = br.string_read()
        self.stream_name: str = br.string_read()
        self.extra_info_len: int = br.bin_read(DTYPES.INT32)