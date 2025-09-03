import io
# from pypamguard.core.readers import BinaryReader

class MultiFileException(Exception):

    def __init__(self, fname, *args, **kwargs):
        super().__init__(*args)
        self.fname = fname

    def __str__(self):
        return f"Error reading {self.fname}: {super().__str__()}"


class BinaryFileException(Exception):

    def __init__(self, br):
        super().__init__()
        self.br = br
        self.position = br.tell()
        self.context = ""

    def add_context(self, context):
        self.context = context  

    def __str__(self):
        return f"{self.__class__.__name__}: {self.context} at position {self.position} bytes"

class WarningException(BinaryFileException):
    
    def __init__(self, br):
        super().__init__(br)

    def __str__(self):
        return f"{super().__str__()}"

class ErrorException(BinaryFileException):
    def __init__(self, br, message = ""):
        super().__init__(br)
        self.message = message
    
    def __str__(self):
        return f"{super().__str__()}, reading {self.__class__.__name__}, {self.message}"

class ChunkLengthMismatch(WarningException):
    def __init__(self, br, chunk_info, chunk_obj):
        super().__init__(br)
        self.chunk_info = chunk_info
        self.chunk_obj = chunk_obj
    
    def __str__(self):
        return super().__str__() + f", expected chunk length {self.chunk_info.length if self.chunk_info else 'unknown'} bytes, got {self.chunk_obj._measured_length + self.chunk_info._measured_length if self.chunk_obj else 'unknown'} bytes"

class CriticalException(BinaryFileException):
    pass

class ModuleNotFoundException(Exception):
    pass

class FileCorruptedException(CriticalException):
    pass

class StructuralException(FileCorruptedException):
    
    def __init__(self, file: io.BufferedReader, message=None):
        super().__init__(file)
        self.message = message
    
    def __str__(self):
        return f"{super().__str__()}, {self.message}"

class NoFileHeaderException(StructuralException):
    pass

class NoModuleHeaderException(StructuralException):
    pass

class NoModuleFooterException(StructuralException):
    pass

class NoFileFooterException(StructuralException):
    pass

