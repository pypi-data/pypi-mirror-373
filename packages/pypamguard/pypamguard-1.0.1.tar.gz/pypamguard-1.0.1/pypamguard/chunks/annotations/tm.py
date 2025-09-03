from .baseannotation import BaseAnnotation
from pypamguard.chunks.annotations.submodules import Location
from pypamguard.core.readers import *

class TMAnnotation(BaseAnnotation):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.model: str = None
        self.n_locations: np.int16 = None
        self.hydrophones: np.uint32 = None
        self.loc: np.ndarray[Location] = None

    def _process(self, br: BinaryReader, *args, **kwargs):
        super()._process(br, *args, **kwargs)
        self.model = br.string_read()
        self.n_locations = br.bin_read(DTYPES.INT16)
        self.hydrophones = br.bin_read(DTYPES.UINT32)
        self.loc = np.ndarray(self.n_locations, type=self.Location)
        for i in range(self.n_locations):
            loc = Location()
            loc.process(br)
            self.loc[i] = loc
