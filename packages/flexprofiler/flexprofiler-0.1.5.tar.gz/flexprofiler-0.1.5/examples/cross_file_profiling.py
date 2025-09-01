""" Example of cross-file profiling. """
import time
import cross_file_profilling_child # file with @track decorators
from flexprofiler import stats

cross_file_profilling_child.f()
stats()
