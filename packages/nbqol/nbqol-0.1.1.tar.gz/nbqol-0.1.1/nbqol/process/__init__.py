"""
Tools for processing and transforming Jupyter notebooks.

This module contains utilities for analyzing, cleaning, reformatting, and executing
Jupyter notebooks.
"""

from .analyze import (
    compare_notebooks,
    execute_notebook,
    check_notebook_runs,
    verify_notebook_variables,
    run_notebook_as_script,
    notebook_cell_dependencies,
)

from .reformat import (
    convert_notebook,
    clean_notebook,
    convert_to_vscode_script,
    VSCodeCellExporter,
    WidgetConverter,
    CleaningPreprocessor,
)

__all__ = [
    # Analysis and execution
    'compare_notebooks',
    'execute_notebook',
    'check_notebook_runs',
    'verify_notebook_variables',
    'run_notebook_as_script',
    'notebook_cell_dependencies',
    
    # Conversion and reformatting
    'convert_notebook',
    'clean_notebook',
    'convert_to_vscode_script',

    # conversion classes
    'VSCodeCellExporter',
    'WidgetConverter',
    'CleaningPreprocessor',
]