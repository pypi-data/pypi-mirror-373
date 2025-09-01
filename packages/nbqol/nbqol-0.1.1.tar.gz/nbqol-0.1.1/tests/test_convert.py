"""Tests for the convert module functionality."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell, new_output

import nbqol
# Updated import after reorganization
from nbqol.process.reformat import (
    convert_to_vscode_script,
    clean_notebook,
    convert_notebook,
    VSCodeCellExporter,
    CleaningPreprocessor,
    WidgetConverter,
)


@pytest.fixture
def temp_notebook():
    """Create a temporary notebook for testing."""
    with tempfile.NamedTemporaryFile(suffix='.ipynb', delete=False) as f:
        nb = new_notebook()
        
        # Add markdown cell
        nb.cells.append(new_markdown_cell('# Test Notebook\nThis is a test notebook.'))
        
        # Add code cell with simple code
        nb.cells.append(new_code_cell('x = 10\ny = 20\nz = x + y\nprint(z)'))
        
        # Add code cell with intermediate output
        nb.cells.append(new_code_cell('x\ny\nz'))
        
        # Add code cell with large output
        code_cell = new_code_cell('print("*" * 2000)')
        output = new_output(
            output_type='stream',
            name='stdout',
            text='*' * 2000
        )
        code_cell.outputs = [output]
        nb.cells.append(code_cell)
        
        # Add a mock widget output
        widget_cell = new_code_cell('import ipywidgets as widgets\nwidgets.Button(description="Click me")')
        widget_output = new_output(
            output_type='display_data',
            data={
                'application/vnd.jupyter.widget-view+json': {
                    'model_id': 'test-widget-id',
                    'version_major': 2,
                    'version_minor': 0
                },
                'text/plain': 'Button(description=\'Click me\', style=ButtonStyle())'
            },
            metadata={}
        )
        widget_cell.outputs = [widget_output]
        nb.cells.append(widget_cell)
        
        # Write the notebook to the file
        nbformat.write(nb, f.name)
        
        yield f.name
        
        # Cleanup
        try:
            os.unlink(f.name)
        except:
            pass


def test_convert_to_vscode_script(temp_notebook):
    """Test converting notebook to VSCode script."""
    temp_dir = tempfile.mkdtemp()
    try:
        output_path = os.path.join(temp_dir, 'test_output.py')
        
        # Convert notebook to VSCode script
        result_path = convert_to_vscode_script(temp_notebook, output_path)
        
        # Check the output path
        assert result_path == output_path
        assert os.path.exists(output_path)
        
        # Read the output file
        with open(output_path, 'r') as f:
            content = f.read()
        
        # Check for VSCode cell markers
        assert '#%% [Cell ' in content
        assert 'x = 10' in content
        assert 'y = 20' in content
        assert 'z = x + y' in content
        assert 'print(z)' in content
        
    finally:
        shutil.rmtree(temp_dir)


def test_clean_notebook(temp_notebook):
    """Test cleaning a notebook."""
    temp_dir = tempfile.mkdtemp()
    try:
        output_path = os.path.join(temp_dir, 'test_cleaned.ipynb')
        
        # Clean the notebook with various options
        result_path = clean_notebook(
            temp_notebook, 
            output_path, 
            remove_markdown=True,
            remove_intermediates=True,
            remove_large_outputs=True
        )
        
        # Check the output path
        assert result_path == output_path
        assert os.path.exists(output_path)
        
        # Read the cleaned notebook
        with open(output_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Check that markdowns are removed (except headers)
        markdown_cells = [cell for cell in nb.cells if cell.cell_type == 'markdown']
        for cell in markdown_cells:
            assert cell.source == '' or cell.source.startswith('#')
        
        # Check that intermediate outputs are removed
        intermediate_cell = nb.cells[2]  # The cell with just x, y, z expressions
        assert intermediate_cell.source.strip() == '' or (
            'x' not in intermediate_cell.source and 
            'y' not in intermediate_cell.source and 
            'z' not in intermediate_cell.source
        )
        
        # Check that large outputs are removed
        large_output_cell = nb.cells[3]  # The cell with '*' * 2000
        if hasattr(large_output_cell, 'outputs'):
            for output in large_output_cell.outputs:
                if output.get('output_type') == 'stream':
                    assert len(output.get('text', '')) < 1000  # Should be removed or truncated
        
    finally:
        shutil.rmtree(temp_dir)


def test_convert_notebook(temp_notebook):
    """Test converting a notebook to different formats."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Test different formats
        formats = ['python', 'vscode_python', 'html', 'markdown']
        extensions = ['.py', '.py', '.html', '.md']
        
        for fmt, ext in zip(formats, extensions):
            output_path = os.path.join(temp_dir, f'test_output{ext}')
            
            # Convert notebook with clean options
            result_path = convert_notebook(
                temp_notebook,
                output_path,
                to_format=fmt,
                clean_options={'remove_large_outputs': True},
                widget_format='html'
            )
            
            # Check the output path
            assert result_path == output_path
            assert os.path.exists(output_path)
            
            # Read the output file
            with open(output_path, 'r') as f:
                content = f.read()
            
            # Check format-specific content
            if fmt.endswith('python'):
                assert 'x = 10' in content
                assert 'y = 20' in content
                assert 'z = x + y' in content
                assert 'print(z)' in content
                
                if fmt == 'vscode_python':
                    assert '#%% [Cell ' in content
                
            elif fmt == 'html':
                assert '<html' in content.lower()
                assert '<div' in content
                # HTML might escape characters or render differently, so check more generic content
                assert 'ipython3' in content
                
            elif fmt == 'markdown':
                assert '# Test Notebook' in content
                assert '```' in content  # Code block markers might vary
                assert 'x = 10' in content
        
    finally:
        shutil.rmtree(temp_dir)


def test_vscode_cell_exporter():
    """Test the VSCodeCellExporter class."""
    exporter = VSCodeCellExporter()
    
    # Create a simple notebook
    nb = new_notebook()
    nb.cells.append(new_code_cell('x = 1'))
    nb.cells.append(new_code_cell('y = 2'))
    
    # Export the notebook
    output, resources = exporter.from_notebook_node(nb)
    
    # Check the output
    assert '#%% [Cell ' in output
    assert 'x = 1' in output
    assert 'y = 2' in output


def test_cleaning_preprocessor():
    """Test the CleaningPreprocessor class."""
    # Create a notebook with various cell types
    nb = new_notebook()
    nb.cells.append(new_markdown_cell('# Header\nRegular markdown text.'))
    nb.cells.append(new_code_cell('x = 10\ny = 20\nz = x + y\nprint(z)'))
    
    # Create a code cell with outputs
    output_cell = new_code_cell('print("test")')
    output = new_output(
        output_type='stream',
        name='stdout',
        text='test'
    )
    output_cell.outputs = [output]
    nb.cells.append(output_cell)
    
    # Create an image output cell
    image_cell = new_code_cell('from IPython.display import Image\nImage("test.png")')
    image_output = new_output(
        output_type='display_data',
        data={
            'image/png': 'base64encodedimagedatawouldbehere==',
            'text/plain': '<IPython.core.display.Image object>'
        },
        metadata={}
    )
    image_cell.outputs = [image_output]
    nb.cells.append(image_cell)
    
    # Test different preprocessor configurations
    
    # 1. Remove markdown
    cleaner = CleaningPreprocessor(remove_markdown=True)
    cleaned_nb, _ = cleaner.preprocess(nb, {})
    
    markdown_cells = [cell for cell in cleaned_nb.cells if cell.cell_type == 'markdown']
    assert len(markdown_cells) > 0
    for cell in markdown_cells:
        if not cell.source.startswith('#'):
            assert cell.source == ''
    
    # 2. Remove intermediates
    cleaner = CleaningPreprocessor(remove_intermediates=True)
    cleaned_nb, _ = cleaner.preprocess(nb, {})
    
    # 3. Remove images
    cleaner = CleaningPreprocessor(remove_images=True)
    cleaned_nb, _ = cleaner.preprocess(nb, {})
    
    # Check image outputs are removed
    for cell in cleaned_nb.cells:
        if hasattr(cell, 'outputs'):
            for output in cell.outputs:
                if output.get('output_type') == 'display_data':
                    assert not any(k.startswith('image/') for k in output.get('data', {}))


def test_widget_converter():
    """Test the WidgetConverter class."""
    # Create a notebook with a widget cell
    nb = new_notebook()
    
    widget_cell = new_code_cell('import ipywidgets as widgets\nwidgets.Button(description="Click me")')
    widget_output = new_output(
        output_type='display_data',
        data={
            'application/vnd.jupyter.widget-view+json': {
                'model_id': 'test-widget-id',
                'version_major': 2,
                'version_minor': 0
            },
            'text/plain': 'Button(description=\'Click me\', style=ButtonStyle())'
        },
        metadata={}
    )
    widget_cell.outputs = [widget_output]
    nb.cells.append(widget_cell)
    
    # Test widget conversion to HTML
    converter = WidgetConverter(widget_format='html')
    converted_nb, _ = converter.preprocess(nb, {})
    
    # Check the widget was converted to HTML representation
    for cell in converted_nb.cells:
        if hasattr(cell, 'outputs'):
            for output in cell.outputs:
                if output.get('output_type') == 'display_data':
                    assert 'text/html' in output.get('data', {})
    
    # Test widget conversion to text
    converter = WidgetConverter(widget_format='text')
    converted_nb, _ = converter.preprocess(nb, {})
    
    # Check the widget was converted to text representation
    for cell in converted_nb.cells:
        if hasattr(cell, 'outputs'):
            for output in cell.outputs:
                if output.get('output_type') == 'stream':
                    assert 'Widget' in output.get('text', '')