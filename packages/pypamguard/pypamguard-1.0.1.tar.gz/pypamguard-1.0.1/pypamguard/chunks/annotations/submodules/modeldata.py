from pypamguard.chunks.base import BaseChunk
from pypamguard.core.readers import *

class ModelData(BaseChunk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.predictions: np.ndarray[np.floating] = None
        self.class_id: np.ndarray[np.int16] = None
        self.is_binary: bool = None
        self.type: np.int18 = None

    def _process(self, br: BinaryReader, *args, **kwargs):
        model_type = br.bin_read(DTYPES.INT8)
        is_binary = bool(br.bin_read(DTYPES.INT8) != 0)
        scale = br.bin_read(DTYPES.FLOAT32)
        n_species = br.bin_read(DTYPES.INT16)
        data = br.bin_read((DTYPES.INT16, lambda x: x/scale), shape=(n_species,))

        n_class = br.bin_read(DTYPES.INT16)
        class_names = br.bin_read(DTYPES.INT16, shape=(n_class,))

        if model_type == 0 or model_type == 1: # generic deep learning annotation
            self.predictions = data
            self.class_id = class_names
            self.is_binary = is_binary
            self.type = model_type
        elif model_type == 2: # dummy result
            self.predictions = np.ndarray(0)
            self.type = 'dummy'