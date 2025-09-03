from .baseannotation import BaseAnnotation
from pypamguard.core.readers import *

class TBDLAnnotation(BaseAnnotation):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n_angles: np.int16 = None
        self.angles: np.ndarray[np.float32] = None
        self.n_errors: np.int16 = None
        self.errors: np.ndarray[np.float32] = None

    def _process(self, br: BinaryReader, *args, **kwargs):
        super()._process(br, *args, **kwargs)
        self.n_angles = br.bin_read(DTYPES.INT16)
        self.angles = br.bin_read(DTYPES.FLOAT32, shape=(self.n_angles))
        self.n_errors = br.bin_read(DTYPES.INT16)
        self.errors = br.bin_read(DTYPES.FLOAT32, shape=(self.n_errors,))
        