import ast
import os
import re
import logging
from groq import Groq

# Set up logging for debugging
logger = logging.getLogger("MonitoringLogger")

class CodeAnalyzer:
    """A class to analyze Python code, detect hardcoded values, suggest constant names, append to constants.py, and modify source code."""
    
    def __init__(self, api_key=None, constants_file=None):
        """Initialize with optional Groq API key and constants file path.
        
        Args:
            api_key (str, optional): Groq API key for LLM-based constant naming. Defaults to None.
            constants_file (str, optional): Path to constants.py. Defaults to 'constants.py' in current directory.
        """
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print(
                "Groq API key not found. Set GROQ_API_KEY environment variable for descriptive LLM-based "
                "constant names (e.g., GREETING_MESSAGE, API_URL). Falling back to heuristic names "
                "(e.g., HELLO_WORLD, URL_HTTPS_EXAMPLE_COM). Run: $env:GROQ_API_KEY='your-api-key' in PowerShell."
            )
        self.model = "llama3-70b-8192"
        self.constants_file = constants_file or os.path.join(os.getcwd(), "constants.py")

    @staticmethod
    def detect_hardcoded_values(source_code):
        """
        Detects hardcoded values (strings, numbers, URLs) in the given source code using AST parsing.
        Skips f-strings and their components, only considering standalone constants.
        
        Args:
            source_code (str): The source code to analyze.
        
        Returns:
            list: A list of tuples (value, type, node) for hardcoded values with their AST nodes.
        """
        try:
            tree = ast.parse(source_code)
            logger.debug(f"Successfully parsed source code")
        except SyntaxError as e:
            logger.error(f"Syntax error in source code: {e}")
            return []
        
        # Add parent references to AST nodes
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        hardcoded_values = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                logger.debug(f"Found constant node at line {node.lineno}: value={node.value}, type={type(node.value).__name__}")
                if isinstance(node.value, str) and node.value.strip():
                    # Skip if part of an f-string
                    if not isinstance(getattr(node, 'parent', None), ast.JoinedStr):
                        # Skip dictionary keys
                        parent = getattr(node, 'parent', None)
                        if isinstance(parent, ast.Dict) and node in parent.keys:
                            logger.debug(f"Skipping dictionary key: '{node.value}'")
                            continue
                        
                        value_type = "url" if re.match(r'https?://[^\s"]+', node.value) else "string"
                        hardcoded_values.append((node.value, value_type, node))
                elif isinstance(node.value, (int, float)) and node.value != 0:
                    hardcoded_values.append((str(node.value), "number", node))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_values = []
        for value, value_type, node in hardcoded_values:
            if value not in seen:
                seen.add(value)
                unique_values.append((value, value_type, node))
        
        logger.info(f"Detected {len(unique_values)} hardcoded values: {[(v, t) for v, t, _ in unique_values]}")
        return unique_values

    def suggest_constant_name(self, value, value_type, context=""):
        """
        Suggest a constant name for a hardcoded value using heuristics or LLM.
        
        Args:
            value (str): The hardcoded value.
            value_type (str): The type of the value (string, number, url).
            context (str): Optional context (e.g., function name).
        
        Returns:
            str: Suggested constant name.
        """
        def heuristic_name(value, value_type):
            value = str(value).strip().replace(" ", "_").replace("-", "_").replace(".", "_").upper()
            value = re.sub(r'[^A-Z0-9_]', '', value)
            if not value:
                value = "CONST_VALUE"
            elif value[0].isdigit():
                value = f"CONST_{value}"
            elif value.startswith('_'):
                value = f"CONST{value}"
            # Add type-specific prefixes for clarity
            if value_type == "url":
                value = f"URL_{value}" if not value.startswith("URL_") else value
            elif value_type == "number":
                value = f"NUM_{value}" if not value.startswith("NUM_") else value
            return value[:30]

        if self.api_key:
            try:
                llm_name = self.suggest_constant_name_with_llm(value, context)
                if llm_name:
                    logger.info(f"LLM suggested constant name: {llm_name} for value: {value} (type: {value_type})")
                    return llm_name
            except Exception as e:
                logger.warning(f"LLM failed: {e}. Falling back to heuristic name for value: {value} (type: {value_type}).")
        
        heuristic = heuristic_name(value, value_type)
        logger.info(f"Heuristic suggested constant name: {heuristic} for value: {value} (type: {value_type})")
        return heuristic

    def suggest_constant_name_with_llm(self, value, context):
        """
        Use Groq LLM to suggest a context-aware constant name.
        
        Args:
            value (str): The hardcoded value.
            context (str): The context (e.g., function name).
        
        Returns:
            str: Suggested constant name or None if invalid.
        """
        client = Groq(api_key=self.api_key)
        prompt = f"""
You are a code analysis assistant tasked with suggesting a meaningful constant name for a hardcoded value in Python code.

Hardcoded value: '{value}'
Context (e.g., function name): '{context}'
Code usage: The value appears in a function named '{context}'.

Suggest a descriptive, uppercase constant name following Python naming conventions (e.g., GREETING_MESSAGE, API_URL, TIMEOUT_SECONDS).
The name should be concise, relevant to the value and context, and no longer than 30 characters.
Avoid naming constants for formatting strings (e.g., punctuation like '!', prefixes like 'Timeout: ', or conjunctions like ', URL: ').
Return only the suggested constant name, nothing else.
"""
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=50,
                temperature=0.2,
            )
            response_text = chat_completion.choices[0].message.content.strip()
            if response_text and re.match(r'^[A-Z][A-Z0-9_]*$', response_text) and len(response_text) <= 30:
                return response_text
            logger.warning(f"Invalid LLM response: {response_text}")
            return None
        except Exception:
            return None

    def append_to_constants_file(self, constant_name, value):
        """
        Append a constant to constants.py if it doesn't already exist.
        
        Args:
            constant_name (str): The name of the constant.
            value (str): The value of the constant.
        """
        if isinstance(value, str):
            value = f'"{value}"'
        else:
            value = str(value)
        
        constant_line = f"{constant_name} = {value}\n"
        
        # Initialize constants.py with header if it doesn't exist
        if not os.path.exists(self.constants_file):
            try:
                with open(self.constants_file, "w") as f:
                    f.write("# constants.py\n# This file is automatically updated with detected constants\n")
                logger.info(f"Created {self.constants_file}")
            except Exception as e:
                logger.error(f"Failed to create {self.constants_file}: {e}")
                raise
        
        existing_content = ""
        try:
            with open(self.constants_file, "r") as f:
                existing_content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {self.constants_file}: {e}")
            raise
        
        if f"{constant_name} =" not in existing_content:
            try:
                with open(self.constants_file, "a") as f:
                    f.write(constant_line)
                logger.info(f"Appended constant {constant_name} to {self.constants_file}")
            except Exception as e:
                logger.error(f"Failed to append to {self.constants_file}: {e}")
                raise

    def modify_function_code(self, source_code, replacements, main_file_path):
        """
        Modify the functions in the source code to use constants and add imports.
        
        Args:
            source_code (str): The full source code of the file.
            replacements (list): List of tuples (function_name, [(value, constant_name, node), ...]) for replacements.
            main_file_path (str): Path to the main file to update.
        
        Returns:
            str: Modified source code with updated functions and imports.
        """
        if not replacements:
            logger.info("No replacements provided. Skipping code modification.")
            return source_code

        try:
            tree = ast.parse(source_code)
            logger.debug(f"Successfully parsed source code for {main_file_path}")
        except SyntaxError as e:
            logger.error(f"Syntax error in source code for {main_file_path}: {e}")
            return source_code
        
        class FunctionTransformer(ast.NodeTransformer):
            def __init__(self, replacements):
                self.replacements = {}
                for func_name, func_replacements in replacements:
                    self.replacements[func_name] = {value: constant_name for value, constant_name, _ in func_replacements}
                self.target_functions = {func_name for func_name, _ in replacements}

            def visit_FunctionDef(self, node):
                if node.name in self.target_functions:
                    logger.info(f"Transforming function: {node.name}")
                    return self.generic_visit(node)
                return node
            
            def visit_AsyncFunctionDef(self, node):
                if node.name in self.target_functions:
                    logger.info(f"Transforming async function: {node.name}")
                    return self.generic_visit(node)
                return node
            
            def visit_Constant(self, node):
                if isinstance(node.value, (str, int, float)):
                    value = str(node.value)
                    # Check if the node is in a function being transformed
                    parent_func = None
                    current = node
                    while hasattr(current, 'parent'):
                        current = current.parent
                        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            parent_func = current.name
                            break
                    if parent_func in self.replacements and value in self.replacements[parent_func]:
                        logger.info(f"Replacing constant value '{value}' with '{self.replacements[parent_func][value]}' in {parent_func}")
                        return ast.Name(id=self.replacements[parent_func][value], ctx=ast.Load())
                return node

        # Add parent references to AST nodes
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

        transformer = FunctionTransformer(replacements)
        new_tree = transformer.visit(tree)
        
        try:
            import astor
            modified_code = astor.to_source(new_tree)
            logger.debug(f"Successfully converted AST to source for {main_file_path}")
        except Exception as e:
            logger.error(f"Failed to convert AST to source for {main_file_path}: {e}")
            return source_code
        
        # Add or update import statement
        constant_names = sorted(set(
            constant_name for _, func_replacements in replacements
            for _, constant_name, _ in func_replacements
        ))
        if constant_names:
            import_statement = f"from constants import {', '.join(constant_names)}\n"
            # Remove any existing 'from constants import' line to avoid duplicates
            modified_code = re.sub(r'^from constants import.*\n', '', modified_code, flags=re.MULTILINE)
            # Add new import statement at the top, after any shebang or encoding lines
            lines = modified_code.split('\n')
            insert_index = 0
            for i, line in enumerate(lines):
                if not line.startswith('#') and not line.startswith('"""'):
                    insert_index = i
                    break
            lines.insert(insert_index, import_statement)
            modified_code = '\n'.join(lines)
        
        # Write back to the file
        try:
            with open(main_file_path, "w") as f:
                f.write(modified_code)
            logger.info(f"Updated {main_file_path} with constants: {', '.join(constant_names)}")
        except Exception as e:
            logger.error(f"Failed to write to {main_file_path}: {e}")
            raise
        
        return modified_code