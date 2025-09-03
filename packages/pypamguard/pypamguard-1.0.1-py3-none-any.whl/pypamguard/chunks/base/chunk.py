from abc import ABC, abstractmethod
import io

import numpy as np
from pypamguard.core.serializable import Serializable
from pypamguard.core.readers import BinaryReader

class BaseChunk(Serializable, ABC):

    def __init__(self, *args, **kwargs):
        self._measured_length = None
        self._start_pos = None

    @property
    def measured_length(self):
        return self._measured_length

    def _process(self, br: BinaryReader, *args, **kwargs):
        pass

    def _post(self, br: BinaryReader, *args, **kwargs):
        pass

    def process(self, br: BinaryReader, *args, **kwargs):
        self._start_pos = br.tell()
        self._process(br, *args, **kwargs)
        self._post(br, *args, **kwargs)
        self._measured_length = br.tell() - self._start_pos 

    def get_attrs(self):
        return [attr for attr in self.__dict__ if not attr.startswith('_')]

    def signature(self) -> dict:
        lines = {}
        for attr, value in self.__dict__.items():
            if not attr.startswith('_'):
                lines[attr] = type(value)
        return lines

    def __str__(self):
        lines = []
        for attr, value in self.__dict__.items():
            if not attr.startswith('_') and not value is None:
                lines.append(f"{attr} ({type(value)}): ")
                # Custom code to print the signature of a list
                if isinstance(value, (list, np.ndarray)) and len(value) > 0:
                    shape = []
                    while isinstance(value, (list, np.ndarray)) and len(value) > 0:
                        shape.append(str(len(value)))
                        value = value[0]
                    lines[-1] += f"[{'x'.join(shape)} {value.__class__.__name__}]"
                else:
                    lines[-1] += f"{value}"

        return '\t' + '\n\t'.join(lines)
