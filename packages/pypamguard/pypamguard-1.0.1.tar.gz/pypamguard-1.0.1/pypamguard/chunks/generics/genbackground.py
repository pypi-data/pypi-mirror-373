from abc import ABC, abstractmethod

from pypamguard.chunks.base import BaseChunk

from .genfileheader import GenericFileHeader
from .genmoduleheader import GenericModuleHeader
from .genmodulefooter import GenericModuleFooter

from pypamguard.core.filters import FILTER_POSITION, Filters

class GenericBackground(BaseChunk, ABC):

    _minimum_version = 0
    _maximum_version = None

    def __init__(self, file_header: GenericFileHeader, module_header: GenericModuleHeader, filters: Filters, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_header = file_header
        self._module_header = module_header
        self._filters = filters
  