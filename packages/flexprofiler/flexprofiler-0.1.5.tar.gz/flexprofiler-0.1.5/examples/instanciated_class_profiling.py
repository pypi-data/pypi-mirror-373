"""Selective profiling example — shows how to use include/exclude to profile only specific methods with @track."""
from flexprofiler import stats, track
import time

# @track
class Foo:
    def __init__(self):
        self.bar = Bar()
    def func_a(self):
        time.sleep(0.05)
        self.bar.func_b()
        self.bar.ref_func()
class Bar:
    def __init__(self):
        self.ref_func = self.func_c
    def func_b(self):
        time.sleep(0.01)
    def func_c(self):
        time.sleep(0.03)

foo = Foo()
foo = track(foo)
foo.func_a()

# @track 
def f(i=0):
    time.sleep(0.02)
    
f = track(f)
f(1)

stats()