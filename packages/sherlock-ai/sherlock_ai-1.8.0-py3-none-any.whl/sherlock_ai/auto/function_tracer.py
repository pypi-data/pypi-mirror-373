"""
Function-level auto-tracing using sys.settrace
"""

import sys
import time
import logging
from typing import List, Dict, Any
from ..utils import get_request_id

logger = logging.getLogger("AutoInstrumentLogger")

class FunctionTracer:
    """Automatic function tracing and monitoring"""
    
    def __init__(self, exclude_modules: List[str] = None, min_duration: float = 0.0):
        self.exclude_modules = exclude_modules or []
        self.min_duration = min_duration
        self.call_stack: Dict[str, Dict[str, Any]] = {}
        self.active = False
        
    def start(self):
        """Start function tracing"""
        if not self.active:
            sys.settrace(self._trace_function)
            self.active = True
            logger.info("Auto-instrumentation function tracing enabled")
            
    def stop(self):
        """Stop function tracing"""
        if self.active:
            sys.settrace(None)
            self.active = False
            logger.info("Auto-instrumentation function tracing disabled")
            
    def _trace_function(self, frame, event, arg):
        """Trace function calls and returns"""
        try:
            module_name = frame.f_globals.get('__name__', '')
            
            # Skip excluded modules
            if any(module_name.startswith(excluded) for excluded in self.exclude_modules):
                return self._trace_function
                
            function_name = frame.f_code.co_name
            full_name = f"{module_name}.{function_name}"
            
            if event == 'call':
                self._handle_function_call(full_name)
            elif event == 'return':
                self._handle_function_return(full_name, arg)
            elif event == 'exception':
                self._handle_function_exception(full_name, arg)
                
        except Exception as e:
            # Don't let tracing break the application
            logger.error(f"Error in function tracer: {e}")
            
        return self._trace_function
        
    def _handle_function_call(self, function_name: str):
        """Handle function entry"""
        self.call_stack[function_name] = {
            'start_time': time.time(),
            'request_id': get_request_id()
        }
        
    def _handle_function_return(self, function_name: str, return_value):
        """Handle function exit"""
        if function_name in self.call_stack:
            call_info = self.call_stack.pop(function_name)
            duration = time.time() - call_info['start_time']
            
            if duration >= self.min_duration:
                logger.info(
                    f"AUTO_TRACE | {function_name} | SUCCESS | {duration:.3f}s | "
                    f"Request: {call_info['request_id']}"
                )
                
    def _handle_function_exception(self, function_name: str, exc_info):
        """Handle function exception"""
        if function_name in self.call_stack:
            call_info = self.call_stack.pop(function_name)
            duration = time.time() - call_info['start_time']
            
            logger.error(
                f"AUTO_TRACE | {function_name} | ERROR | {duration:.3f}s | "
                f"Request: {call_info['request_id']} | Exception: {exc_info}"
            )