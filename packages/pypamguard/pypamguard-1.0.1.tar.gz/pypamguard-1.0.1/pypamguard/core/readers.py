import io
import numpy as np
import enum, datetime, mmap
from typing import Callable
from pypamguard.utils.constants import DTYPES
from pypamguard.utils.bitmap import Bitmap
from pypamguard.core.exceptions import WarningException, ErrorException, CriticalException, BinaryFileException
from pypamguard.logger import logger
from pypamguard.core.serializable import Serializable
from pypamguard.utils.constants import BYTE_ORDERS
from contextlib import contextmanager
import traceback

class Report(Serializable):
    """
    A class to store warnings and errors during program execution.
    Warnings and errors all extend `pypamguard.core.filters.BinaryFileException`.
    """

    __warnings = list[WarningException]
    __errors: list[ErrorException]
    __errors_tb: list[list[str]]

    @property
    def warnings(self) -> list[WarningException]:
        """The list of warnings"""
        return self.__warnings

    @property
    def errors(self) -> list[ErrorException]:
        """The list of errors"""
        return self.__errors

    @property
    def errors_tb(self) -> list[list[str]]:
        """The list of error tracebacks"""
        return self.__errors_tb

    def __init__(self):
        self.current_context = ""
        self.__warnings = []
        self.__errors = []
        self.__errors_tb = []
    
    def set_context(self, context):
        """Set the current context. Automatically added to
        all warnings and errors when `add_error()` or `add_warning()`
        are called."""
        self.current_context = context

    def add_warning(self, warning: BinaryFileException):
        """Add a warning to the report"""
        warning.add_context(self.current_context)
        self.__warnings.append(warning)
        logger.warning(warning)
    
    def add_error(self, error: Exception):
        """Add an error to the report"""
        if type(error) == BinaryFileException:
            error.add_context(self.current_context)
        self.__errors.append(error)
        logger.error(error)
        tb = traceback.format_stack()
        self.__errors_tb.append(tb)
    
    def __str__(self):
        string = "### REPORT SUMMARY ###\n"
        if len(self.__warnings) != 0:
            string += f" - {len(self.__warnings)} warnings (access warnings via .warnings list).\n"
        if len(self.__errors) != 0:
            string += f" - {len(self.__errors)} errors (access errors via .errors list and tracebacks via .errors_tb parallel list).\n"
        string += "### END OF REPORT ###"
        return string

    def print_error_tb(self, index: int):
        for tb in self.__errors_tb[index]:
            print(tb)
        print(self.__errors[index])

class BinaryReader:
    """
    A class to read data from a binary file. 
    """

    def __init__(self, fp: io.BufferedReader, report: Report, endianess: BYTE_ORDERS = BYTE_ORDERS.BIG_ENDIAN):
        """
        :param fp: The file pointer from which data is read (must be opened with 'rb' mode)
        :param report: A `pypamguard.core.readers.Report` object used for logging in the event of an error
        :param endianess: The endianess of the binary reader
        """
        self.__fp = fp
        self.__endianess = endianess
        self.__report = report
    
    @property
    def endianess(self) -> BYTE_ORDERS:
        """The endianess of the binary reader. All data is read in this endianess."""
        return self.__endianess

    @endianess.setter
    def endianess(self, endianess: BYTE_ORDERS):
        if not type(endianess) == BYTE_ORDERS: raise ValueError("Endianess must be one ENDIANESS enum value.")
        self.__endianess = endianess
    
    @property
    def report(self) -> Report:
        """The report object used for logging in the event of an error in this `BinaryReader`."""
        return self.__report

    def __collate(self, data, dtypes, shape):
        for i, dtype_i in enumerate(dtypes):            
            d = data[f'f{i}'][0] if (len(shape) == 1 and shape[0] == 1) else data[f'f{i}'].reshape(shape)
            yield dtype_i[1](d) if dtype_i[1] is not None else d

    def __read(self, length: int) -> bytes:
        data = self.__fp.read(length)
        return data

    def tell(self) -> int:
        """Return the current file pointer position."""
        return self.__fp.tell()

    def seek(self, offset, whence: int = io.SEEK_SET):
        """Set the file pointer position (should not be used directly)."""
        return self.__fp.seek(offset, whence)

    def set_checkpoint(self, offset: int):
        """Given an offset from the current position of the binary reader, set the
        next checkpoint. Upon calling `goto_checkpoint()`, the binary reader will
        seek to the next checkpoint."""
        self.next_checkpoint = self.tell() + offset

    def goto_checkpoint(self):
        """Seek to the next checkpoint set by `set_checkpoint()`."""
        self.seek(self.next_checkpoint)
    
    def at_checkpoint(self):
        """Return `True` if the binary reader is at the next checkpoint, `False` otherwise."""
        if self.tell() == self.next_checkpoint: return True
        else: return False

    def bin_read(self, dtype: list[tuple[DTYPES, Callable[[np.ndarray], np.ndarray]]], shape: tuple = (1,)) -> int | float | np.ndarray | tuple[np.ndarray]:
        """
        Read data from the file. This function is polymorphic in the sense that it
        can be used for any of the following purposes:

        1. Read in a single value of a given datatype (for example `read_numeric(DTYPES.INT32)`).
        2. Read in an array of values of a given datatype (for example `read_numeric(DTYPES.INT32, (5,))`).
        3. Read in an n-dimensional array of values of a given datatype (for example `read_numeric(DTYPES.INT32, (5, 5))`).
        4. Read in an interleaved array of values of a given datatype (for example `read_numeric([DTYPES.INT32, DTYPES.INT32], (5,))`).

        Read in an array of 5 integers (32-bit).
        Return a single `np.ndarray` of type `np.int32`.
        ```python
        bin_read(DTYPES.INT32, (5,))
        ```

        Read in two 5-length arrays (interleaved int32, int32).
        Return a tuple of two `np.ndarray`s of type `np.int16`
        and `np.int64`.
        ```python
        bin_read([DTYPES.INT16, DTYPES.INT64], (5,))
        ```

        Read in a single float (32-bit) and divide by 100.
        Return a single `np.float32`.
        ```python
        bin_read((DTYPES.FLOAT32, lambda x: x / 100))
        ```

        Read in two 5-length arrays (interleaved float32, int8).
        Divide the int8 array by 100.
        Return a tuple of two `np.ndarray`s of type `np.float32` and `np.float32`.
        (NOTE: the int8 array is returned as a float32 array due to the division by 100.)
        ```python
        bin_read([(DTYPES.FLOAT32), (DTYPES.INT8, lambda x: x/100)], (5,))
        ```

        Read in a single 5x2 array of floats (32-bit).
        Return a 2d `np.ndarray` of type `np.float32`.
        ```python
        bin_read(DTYPES.FLOAT32, (5, 2))
        ```
        """
        if type(shape) != tuple: shape = (shape,)
        dtypes = [(dtype_i, None) if isinstance(dtype_i, DTYPES) else dtype_i for dtype_i in ([dtype] if not isinstance(dtype, list) else dtype)]
        data = np.frombuffer(self.__read(sum(dtype_i[0].value.itemsize for dtype_i in dtypes) * np.prod(shape)   ), dtype=[(f'f{i}', dtype_i[0].value.newbyteorder(self.__endianess.value)) for i, dtype_i in enumerate(dtypes)])
        ret_val = tuple(self.__collate(data, dtypes, shape))
        return ret_val[0] if len(ret_val) == 1 else ret_val

    @classmethod
    def millis_to_timestamp(self, millis: int) -> datetime.datetime:
        """Convert a timestamp in milliseconds to a datetime object."""
        return datetime.datetime.fromtimestamp(millis / 1000, tz=datetime.UTC)

    def timestamp_read(self) -> tuple[int, datetime.datetime]:
        """Read in a timestamp in milliseconds and convert it to a datetime object.
        Return a tuple of (milliseconds, datetime)."""
        with br_report(self):
            millis = self.bin_read(DTYPES.INT64)
            return millis, self.millis_to_timestamp(millis)

    def nstring_read(self, length: int) -> str:
        """Read in a string of length `length` and return it as a string."""
        with br_report(self):
            return self.__read(length).decode("utf-8")

    def string_read(self) -> str:
        """Read in a string. The string length is read at first as a 2-byte integer
        specifying the length."""
        with br_report(self):
            return self.nstring_read(self.bin_read(DTYPES.INT16))
    
    def bitmap_read(self, dtype: DTYPES, labels: list[str] = None) -> Bitmap:
        """Read in a bitmap of type `dtype` and return it as a `pypamguard.utils.bitmap.Bitmap`
        object. Can specify a list of `labels` to be mapped onto each bit in the bitmap. See
        the `Bitmap` class more more information.
        
        Example usage (8-bit bitmap):
        ```python
        bitmap_read(DTYPES.INT8, ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
        ```
        """
        with br_report(self):
            return Bitmap(dtype.value.itemsize, labels, int(self.bin_read(dtype)))
    
@contextmanager
def br_report(br: BinaryReader):
    """A context manager that reports warnings and errors to the `BinaryReader` object `br`."""
    try:
        yield
    except WarningException as e:
        br.report.add_warning(e)
    except ErrorException as e:
        br.report.add_error(e)
    except CriticalException as e:
        raise e
    except Exception as e:
        br.report.add_error(ErrorException(br=br, message=str(e)))
