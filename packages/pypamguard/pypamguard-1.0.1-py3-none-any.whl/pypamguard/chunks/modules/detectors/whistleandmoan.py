from pypamguard.chunks.standard import StandardModule, StandardModuleFooter, StandardModuleHeader
from pypamguard.chunks.modules.detectors.spectralbackground import SpectralBackground
from pypamguard.core.readers import *

class WhistleAndMoanDetectorHeader(StandardModuleHeader):
    def __init__(self, file_header):
        super().__init__(file_header)

        self.delay_scale: int = None
    
    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)
        if self.binary_length != 0:
            self.delay_scale = br.bin_read(DTYPES.INT32)

class WhistleAndMoanDetector(StandardModule):

    _header = WhistleAndMoanDetectorHeader
    _background = SpectralBackground

    def __init__(self, file_header, module_header, filters):
        super().__init__(file_header, module_header, filters)

        self.n_slices: int = None
        self.amplitude: float = None

        self.contour: np.ndarray
        self.contour_width: np.ndarray
        self.slice_numbers: np.ndarray
        self.n_peaks: np.ndarray
        self.peak_data: np.ndarray

    def _process(self, br, chunk_info):
        super()._process(br, chunk_info)

        # self.n_slices = br.read_numeric(DTYPES.INT16)
        # self.amplitude = br.read_numeric(DTYPES.INT16) / 100

        self.n_slices, self.amplitude = br.bin_read([(DTYPES.INT16), (DTYPES.INT16, lambda x: x / 100)])

        self.slice_numbers = np.ndarray((self.n_slices,), dtype=np.int32)
        self.n_peaks = np.ndarray((self.n_slices,), dtype=np.int8)
        self.peak_data = np.empty(shape=(self.n_slices,), dtype=object)
        self.contour = np.ndarray((self.n_slices), dtype=np.int16)
        self.contour_width = np.ndarray((self.n_slices), dtype=np.int16)

        for i in range(self.n_slices):
            self.slice_numbers[i] = br.bin_read(DTYPES.INT32)
            self.n_peaks[i] = br.bin_read(DTYPES.INT8)
            self.peak_data[i] = br.bin_read(DTYPES.INT16, (self.n_peaks[i], 4))            
            self.contour[i] = self.peak_data[i][0][1]
            self.contour_width[i] = self.peak_data[i][0][2] - self.peak_data[i][0][0] + 1
        
        self.mean_width = self.contour_width.mean()