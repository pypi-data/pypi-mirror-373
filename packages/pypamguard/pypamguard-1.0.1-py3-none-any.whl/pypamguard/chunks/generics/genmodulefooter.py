from abc import ABC, abstractmethod

from pypamguard.chunks.base import BaseChunk

from .genfileheader import GenericFileHeader
from .genmoduleheader import GenericModuleHeader

class GenericModuleFooter(BaseChunk, ABC):
    
    def __init__(self, file_header: GenericFileHeader, module_header: GenericModuleHeader, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_header = file_header
        self._module_header = module_header

        self.length: int = None
        self.identifier: int = None
