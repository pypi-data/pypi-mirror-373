import time
from contextlib import contextmanager
from pypamguard.logger import logger

@contextmanager
def timer(label):
    logger.debug(f"Started {label}")
    start_time = time.perf_counter()
    yield
    total_time = time.perf_counter() - start_time
    logger.debug(f"Finished {label} in {total_time:.3f} seconds")
