from .baseannotation import BaseAnnotation
from pypamguard.core.readers import *

class ClickClsfrAnnotation(BaseAnnotation):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n_classification: np.int16 = None
        self.classify_set: np.ndarray[np.int16] = None

    def _process(self, br: BinaryReader, *args, **kwargs):
        super()._process(br, *args, **kwargs)
        self.n_classifications = br.bin_read(DTYPES.INT16)
        self.classify_set = br.bin_read(DTYPES.INT16, shape=(self.n_classifications,))