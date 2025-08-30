import inspect
import functools
from typing import Callable, TypeVar, Any, Union
from groq import Groq
import os
import logging
import asyncio

# Type variable for better type hints
F = TypeVar("F", bound=Callable[..., Any])

# Set up logging
logger = logging.getLogger("MonitoringLogger")

def smart_check(func: F = None) -> Union[F, Callable[[F], F]]:
    def decorator(f: F) -> F:
        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            # Get the source code of the function
            source_code = inspect.getsource(f)

            # Send to LLM for analysis
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You're a helpful code reviewer. Suggest improvements related to config management and type safety. Also keep the suggest short and concise"},
                    {"role": "user", "content": f"Here's a Python function:\n\n{source_code}\n\nPlease suggest improvements."}
                ]
            )

            # Print the LLM's suggestions
            suggestions = response.choices[0].message.content
            logger.info(f"LLM Suggestions: {suggestions}")

            # Continue with the original function
            return await f(*args, **kwargs)

        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs):
            groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            # Get the source code of the function
            source_code = inspect.getsource(f)

            # Send to LLM for analysis
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You're a helpful code reviewer. Suggest improvements related to config management and type safety. Also keep the suggest short and concise"},
                    {"role": "user", "content": f"Here's a Python function:\n\n{source_code}\n\nPlease suggest improvements."}
                ]
            )

            # Print the LLM's suggestions - FIXED logging
            suggestions = response.choices[0].message.content
            logger.info(f"LLM Suggestions:{suggestions}")

            # Continue with the original function - NO await for sync
            return f(*args, **kwargs)
        
        # Return the appropriate wrapper based on function type
        return async_wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)
