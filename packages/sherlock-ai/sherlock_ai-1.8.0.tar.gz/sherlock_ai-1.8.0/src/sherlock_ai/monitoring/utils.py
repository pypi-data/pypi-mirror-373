"""
Utility functions for monitoring
"""

import logging
from typing import Optional
from groq import Groq
import os
import ast
import inspect
import textwrap
from types import FunctionType
from typing import Dict, Set

from .snapshots import ResourceSnapshot, MemorySnapshot
from .resource_monitor import ResourceMonitor

logger = logging.getLogger("MonitoringLogger")

# Helper functions for logging
def log_memory_usage(function_name: str, start_memory: MemorySnapshot, end_memory: MemorySnapshot,
                     execution_time: float, success: bool, log_level: str, error: str = None):
    """Log memory usage information"""
    status = "SUCCESS" if success else "ERROR"
    
    # Calculate memory changes
    memory_change = end_memory.current_size - start_memory.current_size
    memory_change_str = ResourceMonitor.format_bytes(abs(memory_change))
    memory_change_sign = "+" if memory_change >= 0 else "-"
    
    current_memory_str = ResourceMonitor.format_bytes(end_memory.current_size)
    
    # Build log message
    log_msg = f"MEMORY | {function_name} | {status} | {execution_time:.3f}s | Current: {current_memory_str} | Change: {memory_change_sign}{memory_change_str}"
    
    # Add tracemalloc info if available
    if end_memory.traced_memory[0] > 0:
        traced_current = ResourceMonitor.format_bytes(end_memory.traced_memory[0])
        traced_peak = ResourceMonitor.format_bytes(end_memory.traced_memory[1])
        log_msg += f" | Traced: {traced_current} (Peak: {traced_peak})"
    
    if error:
        log_msg += f" | Error: {error}"
    
    log_method = getattr(logger, log_level.lower())
    log_method(log_msg)


def log_resource_usage(function_name: str, start_resources: Optional[ResourceSnapshot], 
                       end_resources: Optional[ResourceSnapshot], execution_time: float,
                       success: bool, log_level: str, include_io: bool, include_network: bool, error: str = None):
    """Log comprehensive resource usage information"""
    status = "SUCCESS" if success else "ERROR"
    
    if start_resources is None or end_resources is None:
        log_msg = f"RESOURCES | {function_name} | {status} | {execution_time:.3f}s | Resource monitoring unavailable"
    else:
        diff = ResourceMonitor.calculate_resource_diff(start_resources, end_resources)
        
        # Build basic log message
        current_memory = ResourceMonitor.format_bytes(end_resources.memory_rss)
        memory_change = ResourceMonitor.format_bytes(abs(diff["memory_rss_change"]))
        memory_sign = "+" if diff["memory_rss_change"] >= 0 else "-"
        
        log_msg = (f"RESOURCES | {function_name} | {status} | {execution_time:.3f}s | "
                  f"CPU: {end_resources.cpu_percent:.1f}% | "
                  f"Memory: {current_memory} ({memory_sign}{memory_change}) | "
                  f"Threads: {end_resources.num_threads}")
        
        # Add I/O information if requested
        if include_io and (diff["io_read_bytes"] > 0 or diff["io_write_bytes"] > 0):
            io_read = ResourceMonitor.format_bytes(diff["io_read_bytes"])
            io_write = ResourceMonitor.format_bytes(diff["io_write_bytes"])
            log_msg += f" | I/O: R:{io_read} W:{io_write}"
        
        # Add network information if requested
        if include_network and (diff["net_bytes_sent"] > 0 or diff["net_bytes_recv"] > 0):
            net_sent = ResourceMonitor.format_bytes(diff["net_bytes_sent"])
            net_recv = ResourceMonitor.format_bytes(diff["net_bytes_recv"])
            log_msg += f" | Net: S:{net_sent} R:{net_recv}"
    
    if error:
        log_msg += f" | Error: {error}"
    
    log_method = getattr(logger, log_level.lower())
    log_method(log_msg)

def get_llm_cause(error_message: str, stack_trace: str):
    """Get the probable cause of an error using LLM"""
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes error messages and stack traces to determine the probable cause of an error. Keep the reason and solution crisp and to the point."},
            {"role": "user", "content": f"Error message: {error_message}\nStack trace: {stack_trace}"}
        ]
    )
    return response.choices[0].message.content

def generate_performance_insights(function_name: str, args: list, kwargs: dict, duration: float, function_source_str: str):
    """Generate performance insights using LLM"""
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes performance data to generate insights. Keep the insights crisp and to the point."},
            {"role": "user", "content": f"Function name: {function_name}\nArgs: {args}\nKwargs: {kwargs}\nDuration: {duration}\nFunction source: {function_source_str}"}
        ]
    )
    return response.choices[0].message.content

class FunctionSource:

    @staticmethod
    def _get_called_functions_from_source(source: str) -> Set[str]:
        tree = ast.parse(source)
        return {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }

    @staticmethod
    def _get_function_object_from_scope(func_obj: FunctionType, name: str):
        """
        Try to find the function object for `name` in the global scope of `func_obj`.
        """
        try:
            return func_obj.__globals__[name]
        except KeyError:
            return None
        
    @staticmethod
    def _extract_user_function_sources_only(
        func: FunctionType,
        exclude_patterns: Set[str] = None
    ) -> Dict[str, str]:
        """
        Extract function sources but exclude decorator and monitoring functions(internal functions).
        Only gets the target function and its called functions, excluding sherlock_ai decorators.
        """
        if exclude_patterns is None:
            exclude_patterns = {
                'sherlock_performance_insights',
                'log_performance',
                'generate_performance_insights',
                'async_wrapper', 
                'sync_wrapper', 
                'decorator',
                'run_insight_job',
                'run_in_executor'
            }

        sources = {}
        seen = set()

        # NEW: Get the original function if this is a decorated function
        # original_func = func
        def unwrap_function(func):
            seen = set()
            original_func = func
            while hasattr(original_func, '__wrapped__') and original_func not in seen:
                seen.add(original_func)
                original_func = original_func.__wrapped__
            # print(f"Found wrapped function: {func.__name__} -> {original_func.__name__}")
            return original_func
        original_func = unwrap_function(func)

        # if hasattr(func, '__wrapped__'):
        #     original_func = func.__wrapped__
        #     print(f"Found wrapped function: {func.__name__} -> {original_func.__name__}")
        
        def _recursive_extract(current_func: FunctionType):
            func_name = current_func.__name__

            # Skip if already processed or if it's a decorator function
            if func_name in seen:
                return
            
            seen.add(func_name)
            
            try:
                src = textwrap.dedent(inspect.getsource(current_func))              

                if func_name not in exclude_patterns:
                    print(f"Processing {func_name}")        
                    sources[func_name] = src
                called_names = FunctionSource._get_called_functions_from_source(src)
                    
                # Recursive case: process all called functions
                for called_name in called_names:
                    obj = FunctionSource._get_function_object_from_scope(current_func, called_name)
                    if isinstance(obj, FunctionType):
                        _recursive_extract(obj)
            except Exception as e:
                print(f"Skipped {func_name}: {e}")
        
        # _recursive_extract(original_func)
        _recursive_extract(original_func)
            
        return sources

    @staticmethod
    def _extract_all_function_sources_recursive(
        func: FunctionType,
        seen: Set[str] = None
    ) -> Dict[str, str]:
        
        if seen is None:
            seen = set()

        # NEW: Get the original function if this is a decorated function
        original_func = func
        if hasattr(original_func, '__wrapped__'):
            original_func = original_func.__wrapped__
            print(f"Found wrapped function: {func.__name__} -> {original_func.__name__}")

        sources = {}
        
        def _recursive_extract(current_func: FunctionType):
            func_name = current_func.__name__
            
            # Base case: already processed this function
            if func_name in seen:
                return
            
            seen.add(func_name)
            
            try:
                src = textwrap.dedent(inspect.getsource(current_func))
                sources[func_name] = src
                called_names = FunctionSource._get_called_functions_from_source(src)
                
                # Recursive case: process all called functions
                for called_name in called_names:
                    obj = FunctionSource._get_function_object_from_scope(current_func, called_name)
                    if isinstance(obj, FunctionType):
                        _recursive_extract(obj)  # Recursive call
                        
            except Exception as e:
                print(f"Skipped {func_name}: {e}")
        
        _recursive_extract(original_func)
        return sources
