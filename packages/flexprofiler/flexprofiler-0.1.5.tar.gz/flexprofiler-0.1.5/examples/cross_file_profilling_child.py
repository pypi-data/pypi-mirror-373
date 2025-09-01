# this file is loaded by the cross_file_profiling.py example
from flexprofiler import track
import time

@track
def f():
    time.sleep(0.1)
