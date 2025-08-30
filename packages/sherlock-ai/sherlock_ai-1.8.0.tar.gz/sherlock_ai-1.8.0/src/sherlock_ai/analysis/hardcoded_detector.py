import inspect
import functools
import warnings
import textwrap
from sherlock_ai.analysis.code_analyzer import CodeAnalyzer
import logging
import ast
import os

logger = logging.getLogger("MonitoringLogger")

def hardcoded_value_detector(func=None, *, analyzer=None):
    """
    Decorator to detect hardcoded values, suggest constant names, append to constants.py, and modify the function to use constants.
    Uses sherlock_ai.CodeAnalyzer for detection and code modification.
    
    Args:
        func: The function to be decorated (when used without parameters).
        analyzer (CodeAnalyzer, optional): CodeAnalyzer instance to use. Defaults to None, creating a new instance.
    
    Example:
        >>> from sherlock_ai import hardcoded_value_detector
        >>> @hardcoded_value_detector
        ... def my_function():
        ...     message = "Hello, World!"
        ...     print(message)
        >>> my_function()
        # Creates constants.py with HELLO_WORLD = "Hello, World!" (or GREETING_MESSAGE with API key)
        # Updates my_function to use the constant
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Initialize code analyzer
            code_analyzer = analyzer if analyzer is not None else CodeAnalyzer()
            logger.debug(f"Using constants file: {code_analyzer.constants_file}")

            # Determine if the function is async
            is_async = inspect.iscoroutinefunction(func) or (
                hasattr(func, '__call__') and inspect.iscoroutinefunction(getattr(func, '__call__', None))
            )
            logger.debug(f"Function {func.__name__} is async: {is_async}")

            # Get the file path where the function is defined
            try:
                main_file_path = inspect.getfile(func)
                if not os.path.exists(main_file_path):
                    logger.error(f"File {main_file_path} does not exist or is inaccessible")
                    return await func(*args, **kwargs) if is_async else func(*args, **kwargs)
                logger.debug(f"Function file path: {main_file_path}")
            except Exception as e:
                logger.error(f"Failed to get file path for {func.__name__}: {e}")
                return await func(*args, **kwargs) if is_async else func(*args, **kwargs)

            # Read the entire file source once
            try:
                with open(main_file_path, 'r') as f:
                    file_source = f.read()
                logger.debug(f"Current file content (first 500 chars):\n{file_source[:500]}")
            except Exception as e:
                logger.error(f"Failed to read {main_file_path}: {e}")
                raise

            # Parse the entire file to find all decorated functions
            try:
                tree = ast.parse(file_source)
                logger.debug(f"Successfully parsed {main_file_path}")
            except SyntaxError as e:
                logger.error(f"Syntax error in {main_file_path}: {e}")
                return await func(*args, **kwargs) if is_async else func(*args, **kwargs)

            # Find all function definitions with the decorator
            decorated_functions = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    logger.debug(f"Found function: {node.name} at line {node.lineno}")
                    for i, decorator_node in enumerate(node.decorator_list):
                        logger.debug(f"Checking decorator {i+1} for {node.name}: {ast.dump(decorator_node, indent=2)}")
                        if isinstance(decorator_node, ast.Name) and decorator_node.id == "hardcoded_value_detector":
                            decorated_functions.append(node.name)
                            logger.debug(f"Detected @hardcoded_value_detector on {node.name}")
                        elif isinstance(decorator_node, ast.Call) and hasattr(decorator_node.func, 'id') and decorator_node.func.id == "hardcoded_value_detector":
                            decorated_functions.append(node.name)
                            logger.debug(f"Detected @hardcoded_value_detector() on {node.name}")
                        elif isinstance(decorator_node, ast.Call) and isinstance(decorator_node.func, ast.Attribute):
                            logger.debug(f"Skipping non-hardcoded_value_detector decorator (likely FastAPI) on {node.name}")
                            continue
                        else:
                            logger.debug(f"Unrecognized decorator on {node.name}")

            logger.debug(f"Found decorated functions in {main_file_path}: {decorated_functions}")
            if not decorated_functions:
                logger.info(f"No decorated functions found in {main_file_path}. Executing function.")
                return await func(*args, **kwargs) if is_async else func(*args, **kwargs)

            # Process all decorated functions
            all_replacements = []
            for func_name in decorated_functions:
                try:
                    # Find the function node
                    target_func = None
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                            target_func = node
                            break
                    if not target_func:
                        logger.error(f"Function {func_name} not found in AST.")
                        continue

                    # Extract source code for the function
                    source_lines = file_source.split('\n')
                    func_source = '\n'.join(source_lines[target_func.lineno - 1:target_func.end_lineno])
                    func_source = textwrap.dedent(func_source)

                    # Remove decorator lines
                    clean_lines = [line for line in func_source.split('\n') if not line.strip().startswith('@')]
                    clean_source = '\n'.join(clean_lines)

                    logger.debug(f"Processing function {func_name} in {main_file_path}")
                    logger.debug(f"Clean source for {func_name}:\n{clean_source}")

                    # Detect hardcoded values in the current function
                    hardcoded_values = code_analyzer.detect_hardcoded_values(clean_source)
                    logger.debug(f"Hardcoded values in {func_name}: {[(v, t) for v, t, _ in hardcoded_values]}")

                    # Process each hardcoded value
                    func_replacements = []
                    for value, value_type, node in hardcoded_values:
                        constant_name = code_analyzer.suggest_constant_name(value, value_type, context=func_name)
                        logger.info(f"Processing hardcoded {value_type}: '{value}' -> '{constant_name}' in {func_name}")

                        warnings.warn(
                            f"Hardcoded {value_type} '{value}' found in function '{func_name}'. "
                            f"Replaced with constant '{constant_name}' and appended to constants.py.",
                            category=UserWarning,
                            stacklevel=2
                        )

                        # Add to constants file
                        try:
                            code_analyzer.append_to_constants_file(constant_name, value)
                            logger.info(f"Successfully added {constant_name} to constants file")
                        except Exception as e:
                            logger.error(f"Failed to add {constant_name} to constants file: {e}")
                            raise

                        func_replacements.append((value, constant_name, node))

                    all_replacements.append((func_name, func_replacements))
                except Exception as e:
                    logger.error(f"Failed to process function {func_name}: {e}")
                    continue

            # Modify the source file with all replacements
            if all_replacements:
                try:
                    with open(main_file_path, 'r') as f:
                        current_file_source = f.read()
                    logger.debug(f"About to modify {main_file_path} with replacements: {all_replacements}")
                    modified_code = code_analyzer.modify_function_code(current_file_source, all_replacements, main_file_path)
                    try:
                        with open(main_file_path, 'w') as f:
                            f.write(modified_code)
                        logger.info(f"Successfully modified {main_file_path} with replacements for {', '.join([r[0] for r in all_replacements])}")
                    except Exception as e:
                        logger.error(f"Failed to write modified code to {main_file_path}: {e}")
                        raise
                except Exception as e:
                    logger.error(f"Failed to modify {main_file_path}: {e}")
                    raise

            # Execute the original function
            try:
                return await func(*args, **kwargs) if is_async else func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Failed to execute function {func.__name__}: {e}")
                raise

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)