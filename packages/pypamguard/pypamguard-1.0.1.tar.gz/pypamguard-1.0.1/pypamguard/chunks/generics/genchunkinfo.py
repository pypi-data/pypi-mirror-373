from abc import ABC, abstractmethod
import io

from pypamguard.chunks.base import BaseChunk

class GenericChunkInfo(BaseChunk, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start: int = None
