import datetime

from pypamguard.chunks.generics import GenericModule, GenericModuleFooter
from .stdmodulefooter import StandardModuleFooter
from .stdmoduleheader import StandardModuleHeader
from .stdchunkinfo import StandardChunkInfo
from pypamguard.core.readers import *
from pypamguard.chunks.standard.stddata import StandardDataMixin
from pypamguard.chunks.annotations.annotationmanager import AnnotationManager

class StandardModule(GenericModule, StandardDataMixin):

    _footer = StandardModuleFooter
    _header = StandardModuleHeader

    def __init__(self, file_header, module_header, filters, *args, **kwargs):
        super().__init__(file_header, module_header, filters, *args, **kwargs)
        self._initialize_stddata()
        self.annotations: AnnotationManager = None

    def _process(self, br: BinaryReader, chunk_info: StandardChunkInfo):
        super()._process(br)
        self._process_stddata(br, chunk_info)
    
    def _post(self, br: BinaryReader, chunk_info: StandardChunkInfo):
        super()._post(br)
        if self.flag_bitmap.is_set("HASBINARYANNOTATIONS"):
            self.annotations = AnnotationManager()
            self.annotations.process(br)