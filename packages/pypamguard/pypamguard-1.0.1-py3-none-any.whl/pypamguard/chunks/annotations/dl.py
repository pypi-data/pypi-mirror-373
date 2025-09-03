from .baseannotation import BaseAnnotation
from pypamguard.chunks.annotations.submodules import ModelData
from pypamguard.core.readers import *

class DLAnnotation(BaseAnnotation):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.n_models: np.int16 = None
        self.models: np.ndarray[ModelData] = None

    def _process(self, br: BinaryReader, *args, **kwargs):
        super()._process(br, *args, **kwargs)
        self.n_models = br.bin_read(DTYPES.INT16)
        self.models = np.ndarray(self.n_models, dtype=ModelData)
        for i in range(self.n_models):
            model = ModelData()
            model.process(br, *args, **kwargs)
            self.models[i] = model
