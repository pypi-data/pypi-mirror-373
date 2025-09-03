from pypamguard.chunks.generics import GenericModuleHeader
from pypamguard.core.readers import *

class StandardModuleHeader(GenericModuleHeader):
    
    def __init__(self, file_header, *args, **kwargs):
        super().__init__(file_header, *args, **kwargs)
        self.file_path: str = None
        self.length: int = None
        self.identifier: int = None
        self.version: str = None
        self.binary_length: int = None

    def _process(self, br: BinaryReader, chunk_info):
        self.file_path = chunk_info.file_path
        self.length = chunk_info.length
        self.identifier = chunk_info.identifier
        self.version: int = br.bin_read(DTYPES.INT32)
        self.binary_length: int = br.bin_read(DTYPES.INT32)
