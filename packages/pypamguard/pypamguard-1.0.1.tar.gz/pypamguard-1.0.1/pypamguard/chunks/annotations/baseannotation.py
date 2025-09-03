from pypamguard.chunks.base import BaseChunk
from pypamguard.core.readers import *

class BaseAnnotation(BaseChunk):

    def __init__(self, *args, **kwargs):
        self.annotation_id = None
        self.annotation_length = None
        self.annotation_version = None

    def process(self, br, *args, **kwargs):
        """Require kwargs to contain annotation_id, annotation_length and annotation_version."""
        super().process(br, *args, **kwargs)

    def _process(self, br, *args, **kwargs):
        if not ('annotation_id' in kwargs and 'annotation_length' in kwargs and 'annotation_version' in kwargs):
            raise ValueError('kwargs must contain annotation_id, annotation_length and annotation_version.')
        self.annotation_id = kwargs['annotation_id']
        self.annotation_length = kwargs['annotation_length']
        self.annotation_version = kwargs['annotation_version']
