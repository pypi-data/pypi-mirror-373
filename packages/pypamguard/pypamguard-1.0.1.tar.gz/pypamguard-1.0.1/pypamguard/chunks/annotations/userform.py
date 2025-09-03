from .baseannotation import BaseAnnotation
from pypamguard.core.readers import *

class UserFormAnnotation(BaseAnnotation):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_data: str = None

    def _process(self, br: BinaryReader, *args, **kwargs):
        super()._process(br, *args, **kwargs)
        txt_len = self.annotation_length - len(self.annotation_id) - 2 - 2
        self.form_data = br.nstring_read(txt_len)
        