"""Simple function profiling example — demonstrates using @track to profile a standalone function."""
import time
from flexprofiler import stats, track

# use @track() decorator to profile the function
@track()
def simple_func():
    time.sleep(0.1)

simple_func()
simple_func()

stats() # display the profiling statistics