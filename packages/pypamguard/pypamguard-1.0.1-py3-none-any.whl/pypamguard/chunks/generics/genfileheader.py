from abc import ABC, abstractmethod

from pypamguard.chunks.base import BaseChunk

class GenericFileHeader(BaseChunk, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.length: int = None
        self.identifier: int = None
        self.file_format: int = None
        self.pamguard: str = None
        self.version: str = None
        self.branch: str = None
        self.data_date: int = None
        self.analysis_date: int = None
        self.start_sample: int = None
        self.module_type: str = None
        self.module_name: str = None
        self.stream_name: str = None
        self.extra_info_len: int = None
