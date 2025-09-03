from pypamguard.chunks.base import BaseChunk
from pypamguard.core.readers import *

from .beamformer import BeamFormerAnnotation
from .bearing import BearingAnnotation
from .tm import TMAnnotation
from .tbdl import TBDLAnnotation
from .clickclsfr import ClickClsfrAnnotation
from .matchcls import MatchClsfrAnnotation
from .rwudp import RWUDPAnnotation
from .dl import DLAnnotation
from .userform import UserFormAnnotation

class AnnotationManager(BaseChunk):

    beam_angles: BeamFormerAnnotation
    bearing: BearingAnnotation
    target_motion: TMAnnotation
    toad_angles: TBDLAnnotation
    classification: ClickClsfrAnnotation
    m_classification: MatchClsfrAnnotation
    basic_classification: RWUDPAnnotation
    dl_classification: DLAnnotation
    user_form_data: UserFormAnnotation

    def _process(self, br, *args, **kwargs):
        annotations_length = br.bin_read(DTYPES.INT16)
        n_annotations = br.bin_read(DTYPES.INT16)
        for i in range(n_annotations):
            annotation_length = br.bin_read(DTYPES.INT16) - 2
            annotation_id = br.string_read()
            annotation_version = br.bin_read(DTYPES.INT16)
            kwarg_data = {
                "annotation_length": annotation_length,
                "annotation_id": annotation_id,
                "annotation_version": annotation_version,
            }
            
            if annotation_id == 'Beer':
                self.beam_angles = BeamFormerAnnotation()
                self.beam_angles.process(br, *args, **kwarg_data)
            elif annotation_id == 'Bearing':
                self.bearing = BearingAnnotation()
                self.bearing.process(br, *args, **kwarg_data)
            elif annotation_id == 'TMAN':
                self.target_motion = TMAnnotation()
                self.target_motion.process(br, *args, **kwarg_data)
            elif annotation_id == 'TBDL':
                self.toad_angles = TBDLAnnotation()
                self.toad_angles.process(br, *args, **kwarg_data)
            elif annotation_id == 'ClickClassifier_1':
                self.classification = ClickClsfrAnnotation()
                self.classification.process(br, *args, **kwarg_data)
            elif annotation_id == 'Matched_Clk_Clsfr':
                self.m_classification = MatchClsfrAnnotation()
                self.m_classification.process(br, *args, **kwarg_data)
            elif annotation_id == 'BCLS':
                self.basic_classification = RWUDPAnnotation()
                self.basic_classification.process(br, *args, **kwarg_data)
            elif annotation_id == 'DLRE' or annotation_id == 'Delt':
                self.dl_classification = DLAnnotation()
                self.dl_classification.process(br, *args, **kwarg_data)
            elif annotation_id == 'Uson' or annotation_id == 'USON':
                self.user_form_data = UserFormAnnotation()
                self.user_form_data.process(br, *args, **kwarg_data)
            elif annotation_id == 'USON':
                self.user_form_data = UserFormAnnotation()
                self.user_form_data.process(br, *args, **kwarg_data)
            else:
                raise Exception(f"Unknown annotation type: {annotation_id}")
