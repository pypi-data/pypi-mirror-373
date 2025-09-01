"""
Notebook conversion utilities for extending nbconvert functionality.

This module provides extended notebook conversion capabilities beyond standard
nbconvert, including VSCode-compatible interactive Python scripts, cleaning options
to remove non-essential content, and output conversion utilities.
"""

import os
import re
import json
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from pathlib import Path

import nbformat
from nbformat.notebooknode import NotebookNode
from nbconvert.exporters import PythonExporter, HTMLExporter, MarkdownExporter
from nbconvert.preprocessors import Preprocessor

from ..env import notebook_path


class VSCodeCellExporter(PythonExporter):
    """
    Exporter that converts Jupyter notebooks to VSCode-compatible Python scripts with cell markers.
    
    This exporter creates Python files that can be executed cell-by-cell in VSCode
    using the #%% cell markers that VSCode recognizes for interactive execution.
    """
    
    def __init__(self, config=None, **kwargs):
        super().__init__(config=config, **kwargs)
        self.exclude_input_prompt = True
        self.exclude_output_prompt = True

    def from_notebook_node(self, nb, resources=None, **kwargs):
        """
        Convert a notebook to a string with VSCode cell markers.
        
        Args:
            nb: Notebook node
            resources: Resources dict
            **kwargs: Additional arguments
            
        Returns:
            Tuple containing the converted content and resources dict
        """
        output, resources = super().from_notebook_node(nb, resources, **kwargs)
        
        # Add VSCode cell markers
        lines = output.splitlines()
        new_lines = []
        cell_count = 0
        
        for i, line in enumerate(lines):
            # Check if this is the start of a new cell (empty line followed by a non-empty line)
            if i > 0 and not lines[i-1].strip() and line.strip():
                cell_count += 1
                # Add VSCode cell marker
                new_lines.append(f"#%% [Cell {cell_count}]")
            
            new_lines.append(line)
            
        # Join the lines back together
        output = "\n".join(new_lines)
        
        return output, resources


class CleaningPreprocessor(Preprocessor):
    """
    Notebook preprocessor that removes specified elements like markdown cells,
    intermediate executions, large outputs, or images.
    """
    
    def __init__(self, 
                 remove_markdown: bool = False, 
                 remove_intermediates: bool = False,
                 remove_images: bool = False,
                 remove_large_outputs: bool = False,
                 large_output_threshold: int = 1000,
                 **kwargs):
        """
        Initialize the cleaning preprocessor.
        
        Args:
            remove_markdown: If True, remove all non-header markdown cells
            remove_intermediates: If True, remove cells that don't affect later execution
            remove_images: If True, remove image outputs
            remove_large_outputs: If True, remove outputs exceeding the threshold
            large_output_threshold: Size threshold in characters for large outputs
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.remove_markdown = remove_markdown
        self.remove_intermediates = remove_intermediates
        self.remove_images = remove_images
        self.remove_large_outputs = remove_large_outputs
        self.large_output_threshold = large_output_threshold

    def preprocess_cell(self, cell, resources, index):
        """
        Apply preprocessing to each cell based on configured options.
        
        Args:
            cell: The notebook cell to process
            resources: Resources dict
            index: Cell index
            
        Returns:
            Tuple of the processed cell and resources dict
        """
        # Handle markdown cells
        if cell.cell_type == 'markdown' and self.remove_markdown:
            # Keep markdown cells that are headers
            if not cell.source.startswith('#'):
                cell.source = ''
                
        # Handle code cells
        if cell.cell_type == 'code':
            # Check for intermediate expressions (expressions without assignment)
            if self.remove_intermediates:
                # Basic heuristic: look for lines that appear to be just expressions
                lines = cell.source.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    # Skip lines that appear to be just expressions
                    # (no assignment, not in a function call, etc.)
                    line = line.strip()
                    if (line and 
                        not re.search(r'=', line) and  # no assignment
                        not re.search(r'^print\(', line) and  # not a print statement
                        not re.search(r'^\s*#', line) and  # not a comment
                        not re.search(r'^\s*def\s+', line) and  # not a function definition
                        not re.search(r'^\s*if\s+|^\s*elif\s+|^\s*else\s*:|^\s*for\s+|^\s*while\s+', line) and  # not control flow
                        not line.endswith(':')):  # not a block starter
                        continue
                    
                    cleaned_lines.append(line)
                
                cell.source = '\n'.join(cleaned_lines)
            
            # Handle outputs
            if hasattr(cell, 'outputs') and len(cell.outputs) > 0:
                new_outputs = []
                
                for output in cell.outputs:
                    # Skip image outputs if configured
                    if self.remove_images and output.get('output_type') == 'display_data':
                        if 'data' in output and any(k.startswith('image/') for k in output['data']):
                            continue
                    
                    # Skip large text outputs if configured
                    if self.remove_large_outputs:
                        if output.get('output_type') in ['stream', 'execute_result']:
                            text = output.get('text', '')
                            if not isinstance(text, str):
                                text = str(text)
                            if len(text) > self.large_output_threshold:
                                continue
                            
                    new_outputs.append(output)
                
                cell.outputs = new_outputs
                
        return cell, resources


class WidgetConverter(Preprocessor):
    """
    Converts ipywidget outputs to other formats for better compatibility
    or static rendering.
    """
    
    def __init__(self, widget_format: str = 'html', **kwargs):
        """
        Initialize the widget converter.
        
        Args:
            widget_format: Target format for widget conversion ('html', 'image', or 'text')
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.widget_format = widget_format
    
    def preprocess_cell(self, cell, resources, index):
        """
        Process each cell, converting widget outputs to the specified format.
        
        Args:
            cell: The notebook cell to process
            resources: Resources dict
            index: Cell index
            
        Returns:
            Tuple of the processed cell and resources dict
        """
        if cell.cell_type != 'code' or not hasattr(cell, 'outputs'):
            return cell, resources
            
        # Process outputs
        new_outputs = []
        for output in cell.outputs:
            # Check if this is a widget output
            if (output.get('output_type') == 'display_data' and 
                'application/vnd.jupyter.widget-view+json' in output.get('data', {})):
                
                # Convert widget based on the specified format
                if self.widget_format == 'html':
                    # Convert to HTML representation (simplified)
                    widget_data = output['data']['application/vnd.jupyter.widget-view+json']
                    html_output = nbformat.v4.new_output(
                        output_type='display_data',
                        data={
                            'text/html': f'<div class="widget-placeholder">'
                                         f'Widget ID: {widget_data.get("model_id", "unknown")}</div>'
                        }
                    )
                    new_outputs.append(html_output)
                    
                elif self.widget_format == 'text':
                    # Convert to text representation
                    widget_data = output['data']['application/vnd.jupyter.widget-view+json']
                    text_output = nbformat.v4.new_output(
                        output_type='stream',
                        name='stdout',
                        text=f'[Interactive Widget: {widget_data.get("model_id", "unknown")}]'
                    )
                    new_outputs.append(text_output)
                    
                else:
                    # Default: keep the original output
                    new_outputs.append(output)
            else:
                new_outputs.append(output)
                
        cell.outputs = new_outputs
        return cell, resources


def convert_to_vscode_script(notebook_path_str: Optional[str] = None,
                            output_path: Optional[str] = None) -> str:
    """
    Convert a Jupyter notebook to a VSCode-compatible Python script with cell markers.
    
    Args:
        notebook_path_str: Path to the notebook file. If None, uses the current notebook.
        output_path: Path to save the converted script. If None, uses the same
                    name as the notebook with a .py extension.
    
    Returns:
        Path to the saved Python script.
        
    Examples:
        >>> convert_to_vscode_script('my_notebook.ipynb', 'my_script.py')
        'my_script.py'
        
        >>> # Convert current notebook
        >>> script_path = convert_to_vscode_script()
    """
    # Get notebook path if not provided
    if notebook_path_str is None:
        nb_path = notebook_path()
        if nb_path is None:
            raise ValueError("Not running in a notebook and no notebook path provided")
        notebook_path_str = str(nb_path)
    
    # Determine output path if not provided
    if output_path is None:
        output_path = os.path.splitext(notebook_path_str)[0] + '.py'
    
    # Load the notebook
    with open(notebook_path_str, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    # Convert to VSCode compatible Python
    exporter = VSCodeCellExporter()
    python_code, _ = exporter.from_notebook_node(notebook)
    
    # Save the output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(python_code)
    
    return output_path


def clean_notebook(notebook_path_str: Optional[str] = None,
                  output_path: Optional[str] = None,
                  remove_markdown: bool = False,
                  remove_intermediates: bool = False,
                  remove_images: bool = False,
                  remove_large_outputs: bool = False,
                  large_output_threshold: int = 1000) -> str:
    """
    Clean a Jupyter notebook by removing specified elements.
    
    Args:
        notebook_path_str: Path to the notebook file. If None, uses the current notebook.
        output_path: Path to save the cleaned notebook. If None, uses a '_clean' 
                    suffix on the original name.
        remove_markdown: If True, remove non-header markdown cells
        remove_intermediates: If True, remove intermediate expressions
        remove_images: If True, remove image outputs
        remove_large_outputs: If True, remove outputs exceeding the threshold
        large_output_threshold: Size threshold for large outputs in characters
    
    Returns:
        Path to the saved cleaned notebook.
        
    Examples:
        >>> clean_notebook('my_notebook.ipynb', remove_markdown=True, remove_images=True)
        'my_notebook_clean.ipynb'
    """
    # Get notebook path if not provided
    if notebook_path_str is None:
        nb_path = notebook_path()
        if nb_path is None:
            raise ValueError("Not running in a notebook and no notebook path provided")
        notebook_path_str = str(nb_path)
    
    # Determine output path if not provided
    if output_path is None:
        base, ext = os.path.splitext(notebook_path_str)
        output_path = f"{base}_clean{ext}"
    
    # Load the notebook
    with open(notebook_path_str, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    # Configure and apply the CleaningPreprocessor
    cleaner = CleaningPreprocessor(
        remove_markdown=remove_markdown,
        remove_intermediates=remove_intermediates,
        remove_images=remove_images,
        remove_large_outputs=remove_large_outputs,
        large_output_threshold=large_output_threshold
    )
    
    # Process the notebook
    cleaned_notebook, _ = cleaner.preprocess(notebook, {})
    
    # Save the output
    with open(output_path, 'w', encoding='utf-8') as f:
        nbformat.write(cleaned_notebook, f)
    
    return output_path


def convert_notebook(notebook_path_str: Optional[str] = None,
                    output_path: Optional[str] = None,
                    to_format: str = 'python',
                    clean_options: Optional[dict] = None,
                    widget_format: Optional[str] = None) -> str:
    """
    Convert a Jupyter notebook to different formats with extended options.
    
    Args:
        notebook_path_str: Path to the notebook file. If None, uses the current notebook.
        output_path: Path to save the converted file. If None, determines based on format.
        to_format: Target format ('python', 'vscode_python', 'html', 'markdown')
        clean_options: Dictionary of cleaning options (see clean_notebook)
        widget_format: How to convert ipywidgets ('html', 'text', or None to keep as-is)
    
    Returns:
        Path to the saved converted file.
        
    Examples:
        >>> convert_notebook('my_notebook.ipynb', to_format='vscode_python',
        ...                 clean_options={'remove_markdown': True},
        ...                 widget_format='html')
        'my_notebook.py'
    """
    # Get notebook path if not provided
    if notebook_path_str is None:
        nb_path = notebook_path()
        if nb_path is None:
            raise ValueError("Not running in a notebook and no notebook path provided")
        notebook_path_str = str(nb_path)
    
    # Determine the default output_path based on format if not provided
    if output_path is None:
        base = os.path.splitext(notebook_path_str)[0]
        if to_format in ['python', 'vscode_python']:
            output_path = f"{base}.py"
        elif to_format == 'html':
            output_path = f"{base}.html"
        elif to_format == 'markdown':
            output_path = f"{base}.md"
        else:
            output_path = f"{base}.{to_format}"
    
    # Load the notebook
    with open(notebook_path_str, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    # Apply cleaning if options provided
    if clean_options:
        cleaner = CleaningPreprocessor(**clean_options)
        notebook, _ = cleaner.preprocess(notebook, {})
    
    # Apply widget conversion if specified
    if widget_format:
        widget_converter = WidgetConverter(widget_format=widget_format)
        notebook, _ = widget_converter.preprocess(notebook, {})
    
    # Choose exporter based on format
    if to_format == 'vscode_python':
        exporter = VSCodeCellExporter()
    elif to_format == 'python':
        exporter = PythonExporter()
    elif to_format == 'html':
        exporter = HTMLExporter()
    elif to_format == 'markdown':
        exporter = MarkdownExporter()
    else:
        raise ValueError(f"Unsupported format: {to_format}")
    
    # Convert the notebook
    output, _ = exporter.from_notebook_node(notebook)
    
    # Save the output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    return output_path


__all__ = [
    'convert_to_vscode_script',
    'clean_notebook',
    'convert_notebook',
    'VSCodeCellExporter',
    'CleaningPreprocessor',
    'WidgetConverter',
]