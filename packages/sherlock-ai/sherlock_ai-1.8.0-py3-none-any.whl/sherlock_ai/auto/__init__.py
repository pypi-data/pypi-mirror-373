"""
Auto-instrumentation package for Sherlock AI
"""

from .framework_patcher import patch_frameworks
from .function_tracer import FunctionTracer

def enable_auto_instrumentation(config):
    """Enable automatic instrumentation based on configuration"""
    if config.auto_instrument:
        # Patch supported frameworks
        patch_frameworks(config.auto_frameworks)
        
    if config.auto_trace_functions:
        # Enable function-level tracing
        tracer = FunctionTracer(
            exclude_modules=config.auto_exclude_modules,
            min_duration=config.auto_min_duration
        )
        tracer.start()

__all__ = ["enable_auto_instrumentation"]