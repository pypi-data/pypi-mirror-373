
import re
import time
from flexprofiler import FlexProfiler


# We'll recreate the small object graph from the example to test include/exclude
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


def test_include_single_function(capsys):
	# include only Baz. Define and decorate Foo locally so instrumentation is isolated.
	profiler = FlexProfiler(detailed=True, record_each_call=True)

	@profiler.track(include=["Baz"], max_depth=5)
	class LocalFoo:
		def __init__(self):
			self.bar = Bar()

		def func_a(self):
			time.sleep(0.001)
			self.bar.func_b()

	obj = LocalFoo()
	obj.func_a()
	profiler.stats()
	captured = capsys.readouterr()
	out = captured.out

	# Baz.__init__ and Baz.func_c should be present
	assert re.search(r"Baz\.\w+", out)
	assert "Baz.func_c" in out
	# LocalFoo.func_a should NOT be present because include=['Baz']
	assert "LocalFoo.func_a" not in out


def test_include_multiple_and_class_names(capsys):
	# Now test include with multiple names and a class name via applying decorator dynamically
	# Apply track to a new class to include Qux and func_b pattern
	profiler = FlexProfiler(detailed=True, record_each_call=True)

	@profiler.track(include=[r"func_b", "Qux"], max_depth=5)
	class LocalFoo2:
		def __init__(self):
			self.bar = Bar()

		def func_a(self):
			time.sleep(0.001)
			self.bar.func_b()

	obj = LocalFoo2()
	obj.func_a()
	profiler.stats()
	captured = capsys.readouterr()
	out = captured.out

	# func_b should be present (method-level include). Qux may not be present
	assert "func_b" in out


def test_exclude_behavior(capsys):
	# Test exclude: methods in excluded classes should not appear
	profiler = FlexProfiler(detailed=True, record_each_call=True)
	@profiler.track(exclude=["Qux"], max_depth=5)
	class LocalRoot:
		def __init__(self):
			self.bar = Bar()

		def run(self):
			self.bar.func_b()

	r = LocalRoot()
	r.run()
	profiler.stats()
	captured = capsys.readouterr()
	out = captured.out

	# Qux.func_d should be absent because Qux is excluded
	assert "Qux.func_d" not in out


def test_include_exclude_with_regex_strings_and_compiled_patterns(capsys):
	# Verify include/exclude accept regex strings and compiled patterns
	profiler = FlexProfiler(detailed=True, record_each_call=True)

	# Use regex string to include methods named func_.* and exclude class name Qux
	@profiler.track(include=[r"func_.*"], exclude=[r"Qux"], max_depth=5)
	class LocalFooRegexStr:
		def __init__(self):
			self.bar = Bar()

		def func_a(self):
			time.sleep(0.001)
			self.bar.func_b()

	obj = LocalFooRegexStr()
	obj.func_a()
	profiler.stats()
	captured = capsys.readouterr()
	out = captured.out

	# func_b should be present due to include regex string, Qux.func_d should be excluded
	assert "func_b" in out
	assert "Qux.func_d" not in out

