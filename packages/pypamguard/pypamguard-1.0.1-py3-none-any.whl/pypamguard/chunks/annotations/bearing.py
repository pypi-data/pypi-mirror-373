from .baseannotation import BaseAnnotation
from pypamguard.core.readers import *

class BearingAnnotation(BaseAnnotation):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_name: str = None
        self.hydrophones: np.uint32 = None
        self.array_type: np.int16 = None
        self.localisation_content: np.uint32 = None
        self.n_angles: np.int16 = None
        self.angles: np.ndarray[np.float32] = None
        self.n_errors: np.int16 = None
        self.errors: np.ndarray[np.float32] = None
        self.n_ang: np.int16 = None
        self.ang: np.ndarray[np.float32] = None

    def _process(self, br: BinaryReader, *args, **kwargs):
        super()._process(br, *args, **kwargs)
        self.algorithm_name = br.string_read()
        self.hydrophones = br.bin_read(DTYPES.UINT32)
        self.array_type = br.bin_read(DTYPES.INT16)
        self.localisation_content = br.bin_read(DTYPES.UINT32)
        self.n_angles = br.bin_read(DTYPES.INT16)
        self.angles = br.bin_read(DTYPES.FLOAT32, shape=(self.n_angles,))
        self.n_errors = br.bin_read(DTYPES.INT16)
        self.errors = br.bin_read(DTYPES.FLOAT32, shape=(self.n_errors))
        if self.annotation_version >= 2:
            self.n_ang = br.bin_read(DTYPES.INT16)
            self.ang = br.bin_read(DTYPES.FLOAT32, shape=(self.n_ang,))
            