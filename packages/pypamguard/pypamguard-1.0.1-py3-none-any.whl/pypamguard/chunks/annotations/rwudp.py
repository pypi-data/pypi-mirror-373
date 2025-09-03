from .baseannotation import BaseAnnotation
from pypamguard.core.readers import *

class RWUDPAnnotation(BaseAnnotation):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.label: str = None
        self.method: str = None
        self.score: np.float32 = None

    def _process(self, br: BinaryReader, *args, **kwargs):
        super()._process(br, *args, **kwargs)
        self.label = br.string_read()
        self.method = br.string_read()
        self.score = br.bin_read(DTYPES.FLOAT32)
        