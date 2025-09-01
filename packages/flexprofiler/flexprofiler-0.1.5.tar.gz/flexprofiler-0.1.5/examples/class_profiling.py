"""Class profiling example — demonstrates using @track to profile all methods of a class."""
import time
from flexprofiler import track, stats

# use @track decorator to profile the function
@track
class Foo:
    def example_method(self):
        self.another_method()
        time.sleep(0.1)
    def another_method(self):
        time.sleep(0.2)

Foo().example_method()
Foo().another_method()

stats() # display the profiling statistics