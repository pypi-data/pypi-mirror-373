import os, glob
from pathlib import Path
from pypamguard.core.filters import Filters, WhitelistFilter
from .load_pamguard_binary_file import load_pamguard_binary_file
from .logger import logger, Verbosity
from pypamguard.chunks.generics import GenericModule
from pypamguard.core.readers import Report
from pypamguard.core.exceptions import CriticalException, MultiFileException

_last_root = None
_last_mask = None
_master_list = []
_master_dict = {}
_MAX_NAME_LEN = 80

def find_binary_file(root, mask, file):
    global _last_mask, _last_root, _master_list, _master_dict
    if (not _last_root or not _last_mask) or (_last_root != root or _last_mask != mask):
        _master_list = glob.glob(pathname=mask, root_dir=root, recursive=True)
        _master_dict = {}
        for reldir in _master_list:
            path = os.path.join(root, reldir)
            fname = os.path.basename(path)
            short_name = fname[len(fname)-_MAX_NAME_LEN:] if len(fname) > _MAX_NAME_LEN else fname
            if short_name not in _master_dict:
                _master_dict[short_name] = path
        _last_root = root
        _last_mask = mask
    if file in _master_dict:
        return _master_dict[file]
    else:
        return None

def load_pamguard_multi_file(data_dir: str | Path, file_names: list[str], item_uids: list[int]) -> tuple[list[GenericModule], Report]:
    """
    A function to load a number of PAMGuard data chunks at once from various binary files, filtering by UID.
    Will return a tuple containing a list of `pypamguard.chunks.generics.GenericModule` objects (event data)
    and a `core.readers.Report` object (with errors/warnings).

    For example, the following code will expect three files, `file1.pgdf`, `file2.pgdf` and `file3.pgdf`
    in the directory `./data` with the respective UIDs.
    ```python
    file_names=["file1.pgdf", "file1.pgdf", "file2.pgdf", "file3.pgdf", "file3.pgdf"]
    item_uids=[7000001, 7000199, 10000001, 10002893, 6000001]
    event_data, report = load_pamguard_multi_file("./data", file_names, item_uids)
    ```

    - A `FileNotFoundError` is raised if `data_dir` does not exist.
    - A `ValueError` is raised if `file_names` and `item_uids` are not the same length.
    - A `FileNotFoundError` is added to the report for each file that is not found.
    - A `pypamguard.core.exceptions.MultiFileException` is added to the report for each file
        that requires one or more UIDs that aren't found.
    - If any warnings/errors occur when reading a file, they are added to the report.
    """
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory {data_dir} does not exist.")
    if len(file_names) != len(item_uids):
        raise ValueError("file_names and item_uids must be the same length.")

    file_name_dict = {}
    report = Report()

    event_data = []
    logger.set_verbosity(verbosity=Verbosity.ERROR)
        
    # Each file name has one or more UIDs. Better represented by dict.
    for file_name, uid in zip(file_names, item_uids):
        if file_name not in file_name_dict:
            file_name_dict[file_name] = []
        file_name_dict[file_name].append(uid)

    for file_name in file_name_dict:
        logger.info(f"Loading {file_name}")
        filter_obj = Filters({"uidlist": WhitelistFilter(file_name_dict[file_name])})
        file_path = find_binary_file(data_dir, "**/*.pgdf", file_name)
        if file_path is None:
            report.add_error(FileNotFoundError(f"File {file_name} not found in {data_dir}."))
            continue
        file_data = load_pamguard_binary_file(file_path, filters=filter_obj, report = report)
        file_data.add_file_info()
        if len(file_data.data) != len(file_name_dict[file_name]):
            report.add_error(MultiFileException(file_name, f"Expected {len(file_name_dict[file_name])} items in {file_name}, found {len(file_data.data)}."))
        event_data.extend(file_data.data)

    return event_data, report