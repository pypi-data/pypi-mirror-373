import io

from pypamguard.chunks.generics import GenericChunkInfo, GenericFileHeader, GenericModuleFooter, GenericModuleHeader
from pypamguard.core.readers import *

class StandardModuleFooter(GenericModuleFooter):
    
    def __init__(self, file_header, module_header, *args, **kwargs):
        super().__init__(file_header, module_header, *args, **kwargs)
        self.file_path: str = None
        self.length: int = None
        self.identifier: int = None
        self.binary_length: int = None
    
    def _process(self, br: BinaryReader, chunk_info):
        self.file_path = chunk_info.file_path
        self.length = chunk_info.length
        self.identifier = chunk_info.identifier
        self.binary_length = br.bin_read(DTYPES.INT32)
