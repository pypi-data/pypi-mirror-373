
import time
from flexprofiler import FlexProfiler, track, stats

@track(include=[r"Baz|func_b"], exclude=[r"Qux"], max_depth=5)
class Foo:
	def __init__(self):
		self.bar = Bar()
	def func_a(self):
		time.sleep(0.001)
		self.bar.func_b()

class Bar:
	def __init__(self):
		self.baz = Baz()
	def func_b(self):
		time.sleep(0.001)
		self.baz.func_c()

class Baz:
	def __init__(self):
		self.qux = Qux()
	def func_c(self):
		time.sleep(0.001)
		self.qux.func_d()

class Qux:
	def __init__(self):
		self.bla = Bla()
	def func_d(self):
		time.sleep(0.001)
		self.bla.func_e()

class Bla:
	def __init__(self):
		time.sleep(0.001)
	def func_e(self):
		time.sleep(0.001)

obj = Foo()
obj.func_a()
stats()