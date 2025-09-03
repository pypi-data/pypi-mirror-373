from .baseannotation import BaseAnnotation
from pypamguard.core.readers import *

class MatchClsfrAnnotation(BaseAnnotation):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.data: np.ndarray[np.ndarray[np.float64], np.ndarray[np.float64], np.ndarray[np.float64]] = None

    def _process(self, br: BinaryReader, *args, **kwargs):
        super()._process(br, *args, **kwargs)
        if self.annotation_version == 1:
            # threshold, matchcorr, rejectcorr
            self.data = br.bin_read([DTYPES.FLOAT64, DTYPES.FLOAT64, DTYPES.FLOAT64])
            return
        n_templates = br.bin_read(DTYPES.INT16)        
        self.data = br.bin_read([DTYPES.FLOAT64, DTYPES.FLOAT64, DTYPES.FLOAT64], shape=(n_templates,))
        