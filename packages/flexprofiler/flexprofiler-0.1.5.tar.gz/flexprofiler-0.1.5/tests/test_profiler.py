import time
import pytest
from flexprofiler import FlexProfiler

def test_simple_func_stats():
    profiler = FlexProfiler(detailed=True, record_each_call=True)
    @profiler.track
    def simple_func():
        for i in range(2):
            time.sleep(0.01)
    simple_func()
    simple_func()
    # Ensure the call_graph recorded two calls to simple_func and that
    # some non-zero time was accumulated for the function in the call_graph

    keys = list(profiler.call_graph.keys())
    assert len(keys) == 1
    assert 'simple_func' in keys[0]
    stats = profiler.call_graph[keys[0]]
    assert stats.get('count', 0) == 2
    assert stats.get('total_time', 0) > 0
