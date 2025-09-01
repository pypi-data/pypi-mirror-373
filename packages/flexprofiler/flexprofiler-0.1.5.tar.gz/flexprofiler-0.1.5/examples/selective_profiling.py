"""Selective profiling example — shows how to use include/exclude to profile only specific methods with @track."""
from flexprofiler import track, stats
import time

# Example 1: Using 'include' to only profile selected methods
@track(include=["foo", "bar"])
class MyClassInclude:
    def foo(self):
        time.sleep(0.05)
    def bar(self):
        time.sleep(0.02)
    def baz(self):
        time.sleep(0.01)
    def run(self):
        self.foo()
        self.bar()
        self.baz()

obj_inc = MyClassInclude()
obj_inc.run()

print("\nStats with include=['foo', 'bar'] (baz is not tracked):")
stats()

# Example 2: Using 'exclude' to skip selected methods
@track(exclude=["bar"])
class MyClassExclude:
    def foo(self):
        time.sleep(0.05)
    def bar(self):
        time.sleep(0.02)
    def baz(self):
        time.sleep(0.01)
    def run(self):
        self.foo()
        self.bar()
        self.baz()

obj_exc = MyClassExclude()
obj_exc.run()

print("\nStats with exclude=['bar'] (bar is not tracked):")
stats()
