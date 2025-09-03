from pypamguard.chunks.base import BaseChunk
from pypamguard.core.readers import *
from pypamguard.chunks.generics import GenericChunkInfo
from pypamguard.utils.constants import IdentifierType
from pypamguard.core.exceptions import CriticalException, FileCorruptedException

class StandardChunkInfo(GenericChunkInfo):
    
    def __init__(self, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length: int = None
        self.identifier: int = None
        self.file_path: str = file_path

    def _process(self, br: BinaryReader):
        self.length, self.identifier = br.bin_read([DTYPES.INT32, DTYPES.INT32])
        if self.length < 0 or (self.identifier < 0 and self.identifier not in IdentifierType._value2member_map_):
            raise FileCorruptedException(br)
