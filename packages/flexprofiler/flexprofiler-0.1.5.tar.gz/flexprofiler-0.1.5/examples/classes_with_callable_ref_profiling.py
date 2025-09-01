"""Selective profiling example — shows how to use include/exclude to profile only specific methods with @track."""
from flexprofiler import track, stats
import time

@track(max_depth=5, include=["func_b"])
class Foo:
    def __init__(self):
        self.bar = Bar()
    def func_a(self):
        time.sleep(0.05)
        # self.bar.reference_to_func()
        self.bar.func_b()

class Bar:
    def __init__(self):
        self.reference_to_func = self.func_b
    def func_b(self):
        time.sleep(0.01)

obj_inc = Foo()
obj_inc.func_a()

# expected output: 
# Detailed Function Call Statistics:
# Foo.__init__: ───────1 calls, 0.01ms, Avg: 0.01ms
# Foo.func_a: ────────1 calls, 60.66ms, Avg: 60.66ms
#   └──Bar.func_b: ───1 calls, 10.13ms, Avg: 10.13ms
stats()