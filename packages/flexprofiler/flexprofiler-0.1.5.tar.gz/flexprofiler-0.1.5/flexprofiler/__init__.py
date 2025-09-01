"""FlexProfiler package exports.

Import the convenience helpers from ``default_profiler`` when using the
package at the command-line or in small scripts::

	from flexprofiler import track, stats

For advanced usage import and instantiate ``FlexProfiler`` directly from
``flexprofiler.profiler``.
"""

from .default_profiler import  stats, track, default_profiler
from .profiler import FlexProfiler

__version__ = "0.1.5"
__all__ = ["track", "stats", "FlexProfiler", "default_profiler"]
