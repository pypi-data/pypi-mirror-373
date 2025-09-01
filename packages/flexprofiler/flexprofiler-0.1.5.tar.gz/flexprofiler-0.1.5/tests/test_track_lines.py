import time
from flexprofiler import FlexProfiler


def test_line_level_tracking():
    profiler = FlexProfiler(detailed=False, record_each_call=True)

    @profiler.track(lines=True)
    def foo(x):
        a = x + 1
        time.sleep(0.01)
        b = a * 2
        time.sleep(0.005)
        return b

    # Call function a few times to collect per-line timings
    foo(1)
    foo(2)

    keys = list(profiler.line_stats.keys())
    assert len(keys) == 1
    assert "foo" in keys[0], "Expected line stats for function 'foo' to be recorded"

    lines = """
a = x + 1
time.sleep(0.01)
b = a * 2
time.sleep(0.005)
return b
"""
    lines_list = lines.strip().split("\n")
    for i, (line_num, line_stats) in enumerate(profiler.line_stats[keys[0]].items()):

        assert lines_list[i] in line_stats["content"], f"Expected line stats for {lines_list[i]} to be recorded"