"""Convenience single-instance profiler utilities.

This module creates a module-level ``FlexProfiler`` instance named
``_default_profiler`` and exposes commonly used helpers such as ``track`` and
``stats`` so callers can quickly add lightweight profiling to scripts.
"""

from .profiler import FlexProfiler

# Single shared profiler used by the convenience helpers below. The instance
# is intentionally created with detailed output enabled so examples and tests
# that rely on call-graph printing work out of the box.
_default_profiler = FlexProfiler(detailed=True, record_each_call=True)

stats = _default_profiler.stats
track = _default_profiler.track
default_profiler = _default_profiler