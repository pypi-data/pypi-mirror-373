"""Selective profiling example — shows how to use include/exclude to profile only specific methods with @track."""
from flexprofiler import track, stats
import time

# @track(max_depth=5)
# @track(max_depth=5, exclude=["func_e", "func_d"])
# @track(max_depth=5, include=["func_e", "func_d"])
@track(max_depth=5, include=["Baz"], exclude=["func_e"])
class Foo:
    def __init__(self):
        self.bar = Bar()
    def func_a(self):
        time.sleep(0.05)
        self.bar.func_b()
class Bar:
    def __init__(self):
        self.baz = Baz()
    def func_b(self):
        time.sleep(0.01)
        self.baz.func_c()
class Baz:
    def __init__(self):
        self.qux = Qux()
    def func_c(self):
        time.sleep(0.03)
        self.qux.func_d()
class Qux:
    def __init__(self):
        self.bla = Bla()
    def func_d(self):
        time.sleep(0.02)
        self.bla.func_e()
class Bla:
    def __init__(self):
        time.sleep(0.01)
    def func_e(self):
        time.sleep(0.02)

foo = Foo()
foo.func_a()


stats()
