"""
Analysis utilities for Jupyter notebooks.

This module provides tools for notebook execution, comparing notebook outputs,
analyzing cell dependencies, and verifying notebook content.
"""

import os
import sys
import re
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

import nbformat
from nbformat.notebooknode import NotebookNode

from ..env import notebook_path


def _check_nbformat_installed():
    try:
        import nbformat
    except ImportError:
        raise ImportError(
            "nbformat is required for notebook execution.",
            "Install it with 'pip install nbformat'.",
        )


def execute_notebook(
    notebook_path_str: Optional[str] = None,
    output_path: Optional[str] = None,
    timeout: int = 600,
    allow_errors: bool = False,
    kernel_name: Optional[str] = None,
) -> str:
    """
    Execute a notebook and save the result with outputs.

    Args:
        notebook_path_str: Path to the notebook file. If None, uses the current notebook.
        output_path: Path to save the executed notebook. If None, uses a '_executed'
                    suffix on the original name.
        timeout: Execution timeout in seconds.
        allow_errors: If True, continue execution even if cells raise exceptions.
        kernel_name: Name of the kernel to use. If None, uses the default kernel.

    Returns:
        Path to the saved executed notebook.

    Examples:
        >>> execute_notebook('my_notebook.ipynb', allow_errors=True)
        'my_notebook_executed.ipynb'
    """
    try:
        import nbconvert
        from nbconvert.preprocessors import ExecutePreprocessor
    except ImportError:
        raise ImportError(
            "nbconvert is required for notebook execution. "
            "Install it with 'pip install nbconvert'."
        )

    # Get notebook path if not provided
    if notebook_path_str is None:
        nb_path = notebook_path()
        if nb_path is None:
            raise ValueError("Not running in a notebook and no notebook path provided")
        notebook_path_str = str(nb_path)

    # Determine output path if not provided
    if output_path is None:
        base, ext = os.path.splitext(notebook_path_str)
        output_path = f"{base}_executed{ext}"

    # Load the notebook
    with open(notebook_path_str, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    # Configure the ExecutePreprocessor
    execute_kwargs = {
        "timeout": timeout,
        "allow_errors": allow_errors,
    }

    if kernel_name:
        execute_kwargs["kernel_name"] = kernel_name

    # Create ExecutePreprocessor
    executor = ExecutePreprocessor(**execute_kwargs)

    # Execute the notebook
    executed_notebook, _ = executor.preprocess(
        notebook, {"metadata": {"path": os.path.dirname(notebook_path_str)}}
    )

    # Save the executed notebook
    with open(output_path, "w", encoding="utf-8") as f:
        nbformat.write(executed_notebook, f)

    return output_path


def compare_notebooks(
    notebook1_path: str,
    notebook2_path: str,
    ignore_outputs: bool = False,
    ignore_metadata: bool = True,
) -> Dict[str, Any]:
    """
    Compare two notebooks and return differences.

    Args:
        notebook1_path: Path to the first notebook file.
        notebook2_path: Path to the second notebook file.
        ignore_outputs: If True, don't compare cell outputs.
        ignore_metadata: If True, don't compare notebook metadata.

    Returns:
        Dictionary of differences with cells that differ.

    Examples:
        >>> diff = compare_notebooks('notebook1.ipynb', 'notebook2.ipynb')
        >>> print(f"Found {len(diff['cells'])} different cells")
    """
    # Load notebooks
    with open(notebook1_path, "r", encoding="utf-8") as f1:
        nb1 = nbformat.read(f1, as_version=4)

    with open(notebook2_path, "r", encoding="utf-8") as f2:
        nb2 = nbformat.read(f2, as_version=4)

    # Initialize differences
    differences = {
        "cells": [],
        "metadata": {},
        "cell_count_diff": len(nb1.cells) - len(nb2.cells),
    }

    # Compare metadata if needed
    if not ignore_metadata:
        for key in set(nb1.metadata.keys()) | set(nb2.metadata.keys()):
            if key not in nb1.metadata:
                differences["metadata"][key] = {
                    "status": "only_in_notebook2",
                    "value": nb2.metadata[key],
                }
            elif key not in nb2.metadata:
                differences["metadata"][key] = {
                    "status": "only_in_notebook1",
                    "value": nb1.metadata[key],
                }
            elif nb1.metadata[key] != nb2.metadata[key]:
                differences["metadata"][key] = {
                    "status": "different",
                    "notebook1": nb1.metadata[key],
                    "notebook2": nb2.metadata[key],
                }

    # Compare cells
    min_cells = min(len(nb1.cells), len(nb2.cells))
    for i in range(min_cells):
        cell1 = nb1.cells[i]
        cell2 = nb2.cells[i]

        # Compare source
        if cell1.source != cell2.source:
            differences["cells"].append(
                {
                    "index": i,
                    "type": "source",
                    "notebook1": cell1.source,
                    "notebook2": cell2.source,
                }
            )

        # Compare outputs if needed
        if (
            not ignore_outputs
            and cell1.cell_type == "code"
            and cell2.cell_type == "code"
        ):
            if len(cell1.outputs) != len(cell2.outputs):
                differences["cells"].append(
                    {
                        "index": i,
                        "type": "output_count",
                        "notebook1": len(cell1.outputs),
                        "notebook2": len(cell2.outputs),
                    }
                )
            else:
                for j, (output1, output2) in enumerate(
                    zip(cell1.outputs, cell2.outputs)
                ):
                    if output1 != output2:
                        differences["cells"].append(
                            {
                                "index": i,
                                "output_index": j,
                                "type": "output_content",
                                "notebook1": output1,
                                "notebook2": output2,
                            }
                        )

    # Add information about extra cells
    if len(nb1.cells) > len(nb2.cells):
        differences["extra_cells_notebook1"] = [
            {
                "index": i,
                "content": (
                    cell.source[:100] + "..." if len(cell.source) > 100 else cell.source
                ),
            }
            for i, cell in enumerate(nb1.cells[min_cells:], start=min_cells)
        ]
    elif len(nb2.cells) > len(nb1.cells):
        differences["extra_cells_notebook2"] = [
            {
                "index": i,
                "content": (
                    cell.source[:100] + "..." if len(cell.source) > 100 else cell.source
                ),
            }
            for i, cell in enumerate(nb2.cells[min_cells:], start=min_cells)
        ]

    return differences


def check_notebook_runs(
    notebook_path_str: str, timeout: int = 600, kernel_name: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Check if a notebook runs without errors.

    Args:
        notebook_path_str: Path to the notebook file.
        timeout: Execution timeout in seconds.
        kernel_name: Name of the kernel to use. If None, uses the default kernel.

    Returns:
        Tuple of (success: bool, message: str) indicating if the notebook ran successfully.

    Examples:
        >>> success, msg = check_notebook_runs('my_notebook.ipynb')
        >>> if success:
        ...     print("Notebook runs successfully")
        ... else:
        ...     print(f"Notebook failed: {msg}")
    """
    try:
        # Create a temporary file for the executed notebook
        with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Execute the notebook
            execute_notebook(
                notebook_path_str,
                output_path=temp_path,
                timeout=timeout,
                allow_errors=False,
                kernel_name=kernel_name,
            )
            return True, "Notebook executed successfully"

        except Exception as e:
            # If execution failed, try to extract error information
            try:
                with open(temp_path, "r", encoding="utf-8") as f:
                    executed_nb = nbformat.read(f, as_version=4)

                # Look for the first cell with an error
                for i, cell in enumerate(executed_nb.cells):
                    if cell.cell_type == "code" and hasattr(cell, "outputs"):
                        for output in cell.outputs:
                            if output.output_type == "error":
                                error_name = output.get("ename", "Unknown error")
                                error_value = output.get("evalue", "")
                                traceback = "\n".join(output.get("traceback", []))

                                return False, (
                                    f"Error in cell {i+1}: {error_name}: {error_value}\n"
                                    f"Traceback:\n{traceback}"
                                )

                # If we couldn't find a specific error in the outputs
                return False, f"Notebook execution failed: {str(e)}"

            except Exception:
                # If we can't parse the executed notebook
                return False, f"Notebook execution failed: {str(e)}"

    finally:
        # Clean up the temporary file
        if "temp_path" in locals():
            try:
                os.unlink(temp_path)
            except Exception:
                pass


def verify_notebook_variables(
    notebook_path_str: str, variables: List[str], timeout: int = 600
) -> Dict[str, Any]:
    """
    Execute a notebook and verify that certain variables are defined and non-None.

    Args:
        notebook_path_str: Path to the notebook file.
        variables: List of variable names to check.
        timeout: Execution timeout in seconds.

    Returns:
        Dictionary mapping variable names to their status.

    Examples:
        >>> results = verify_notebook_variables('my_notebook.ipynb',
        ...                                    ['df', 'model', 'accuracy'])
        >>> for var, status in results.items():
        ...     print(f"{var}: {status['exists']}, {status.get('type', 'N/A')}")
    """
    # Create a temporary file for the injected notebook
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Load the notebook
        with open(notebook_path_str, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

        # Create a new cell that checks for the variables
        check_code = "import types\n_nbqol_var_check = {}\n"
        for var in variables:
            check_code += f"""
try:
    _nbqol_var_check['{var}'] = {{
        'exists': '{var}' in locals() or '{var}' in globals(),
        'is_none': {var} is None if '{var}' in locals() or '{var}' in globals() else None,
        'type': type({var}).__name__ if '{var}' in locals() or '{var}' in globals() else None
    }}
except NameError:
    _nbqol_var_check['{var}'] = {{'exists': False, 'is_none': None, 'type': None}}
_nbqol_var_check
"""

        # Add the check cell at the end
        notebook.cells.append(nbformat.v4.new_code_cell(check_code))

        # Save the modified notebook
        with open(temp_path, "w", encoding="utf-8") as f:
            nbformat.write(notebook, f)

        # Execute the notebook
        executed_path = execute_notebook(
            temp_path, output_path=None, timeout=timeout  # Will use default naming
        )

        # Load the executed notebook
        with open(executed_path, "r", encoding="utf-8") as f:
            executed_nb = nbformat.read(f, as_version=4)

        # Extract the variable check results
        last_cell = executed_nb.cells[-1]
        if (
            last_cell.cell_type == "code"
            and hasattr(last_cell, "outputs")
            and len(last_cell.outputs) > 0
        ):
            # Find the output with the variable check results
            for output in last_cell.outputs:
                if output.output_type == "execute_result":
                    if "data" in output and "text/plain" in output["data"]:
                        # Parse the text representation of the dictionary
                        result_text = output["data"]["text/plain"]
                        # Use exec to safely evaluate the expression
                        var_check_result = {}
                        try:
                            exec(f"var_check_result = {result_text}")
                            return var_check_result
                        except Exception:
                            return {
                                var: {
                                    "exists": False,
                                    "error": "Failed to parse results",
                                }
                                for var in variables
                            }

        # If we couldn't find the results
        return {
            var: {"exists": False, "error": "Failed to check variable"}
            for var in variables
        }

    finally:
        # Clean up temporary files
        for path in [temp_path, locals().get("executed_path")]:
            if path:
                try:
                    os.unlink(path)
                except Exception:
                    pass


def run_notebook_as_script(
    notebook_path_str: str,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
) -> Tuple[int, str, str]:
    """
    Convert a notebook to a Python script and run it as a standalone script.

    Args:
        notebook_path_str: Path to the notebook file.
        args: Command line arguments to pass to the script.
        env: Environment variables to set for the script execution.

    Returns:
        Tuple of (return_code, stdout, stderr).

    Examples:
        >>> code, stdout, stderr = run_notebook_as_script('my_notebook.ipynb')
        >>> if code == 0:
        ...     print("Script ran successfully")
        ... else:
        ...     print(f"Script failed with error: {stderr}")
    """
    from .reformat import convert_to_vscode_script

    # Convert notebook to a script
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        script_path = temp_file.name

    try:
        # Convert the notebook
        convert_to_vscode_script(notebook_path_str, output_path=script_path)

        # Prepare the command
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)

        # Prepare environment
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        # Run the script
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=process_env,
            text=True,
        )

        # Get output
        stdout, stderr = process.communicate()
        return_code = process.returncode

        return return_code, stdout, stderr

    finally:
        # Clean up the temporary file
        try:
            os.unlink(script_path)
        except Exception:
            pass


def notebook_cell_dependencies(notebook_path_str: str) -> Dict[int, Set[int]]:
    """
    Analyze a notebook to find dependencies between cells.

    This function looks for variable definitions and usage to determine which cells
    depend on each other.

    Args:
        notebook_path_str: Path to the notebook file.

    Returns:
        Dictionary mapping cell indices to sets of indices they depend on.

    Examples:
        >>> deps = notebook_cell_dependencies('my_notebook.ipynb')
        >>> for cell_idx, dependencies in deps.items():
        ...     print(f"Cell {cell_idx} depends on cells: {dependencies}")
    """
    # Load the notebook
    with open(notebook_path_str, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    # Track defined and used variables
    defined_vars = {}  # Maps variable names to cell indices where they're defined
    dependencies = {}  # Maps cell indices to sets of cell indices they depend on

    # Simple regex to find variable definitions and usage
    def_pattern = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=")
    use_pattern = re.compile(r"[^a-zA-Z0-9_]([a-zA-Z_][a-zA-Z0-9_]*)[^a-zA-Z0-9_]")

    # Skip common Python keywords
    python_keywords = {
        "if",
        "else",
        "elif",
        "for",
        "while",
        "def",
        "class",
        "return",
        "True",
        "False",
        "None",
        "import",
        "from",
        "as",
        "with",
        "try",
        "except",
        "finally",
        "break",
        "continue",
        "pass",
        "assert",
        "in",
        "is",
        "and",
        "or",
        "not",
        "print",
        "len",
        "range",
        "enumerate",
        "zip",
        "list",
        "dict",
        "set",
        "tuple",
        "int",
        "float",
        "str",
        "bool",
        "max",
        "min",
        "sum",
        "any",
        "all",
    }

    # Analyze each code cell
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type != "code":
            continue

        dependencies[i] = set()
        source = cell.source

        # Find variable definitions in this cell
        for line in source.split("\n"):
            match = def_pattern.search(line)
            if match:
                var_name = match.group(1)
                defined_vars[var_name] = i

        # Find variable usage in this cell
        used_vars = set()
        for line in source.split("\n"):
            for match in use_pattern.finditer(line):
                var_name = match.group(1)
                # Skip Python keywords and built-ins
                if var_name not in python_keywords:
                    used_vars.add(var_name)

        # Determine dependencies
        for var in used_vars:
            if var in defined_vars and defined_vars[var] != i:
                dependencies[i].add(defined_vars[var])

    return dependencies


__all__ = [
    "execute_notebook",
    "compare_notebooks",
    "check_notebook_runs",
    "verify_notebook_variables",
    "run_notebook_as_script",
    "notebook_cell_dependencies",
]