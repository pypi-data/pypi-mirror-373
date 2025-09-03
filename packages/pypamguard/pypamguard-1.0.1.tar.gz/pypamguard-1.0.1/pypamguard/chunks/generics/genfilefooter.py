from abc import ABC, abstractmethod

from pypamguard.chunks.base import BaseChunk
from .genfileheader import GenericFileHeader

class GenericFileFooter(BaseChunk, ABC):
    
    def __init__(self, file_header: GenericFileHeader):
        super().__init__()
        self._file_header = file_header

        self.length: int = None
        self.identifier: int = None
