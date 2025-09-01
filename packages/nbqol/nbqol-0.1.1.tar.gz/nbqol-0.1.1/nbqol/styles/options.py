from os import environ as ENVIRON
from pathlib import Path
from IPython.display import display, HTML

__all__ = ['get_jupyter_css', 'load_vscode_styles']

def get_jupyter_css(text_only=False, as_style=False, **kwargs):
    """Generate CSS styling for Jupyter outputs.
    
    Parameters
    ----------
    text_only : bool, optional
        If True, return only text-related styles (default False)
    as_style : bool, optional
        If True, return CSS as a formatted string (default False)
    **kwargs : dict
        Additional CSS properties to include
        
    Returns
    -------
    dict or str
        CSS properties as a dictionary or formatted string
        
    Examples
    --------
    >>> css = get_jupyter_css(text_only=True)
    >>> css['font-family']
    'monospace'
    
    >>> css = get_jupyter_css(as_style=True)
    >>> print(css)
    'font-family: monospace; font-size: 13px; ...'
    """
    text_style = {'font-family': 'monospace',
                  'font-weight': 'normal',
                  'font-size': '13px',
                  'line-height': '16px'}
    
    div_style = {'padding-bottom': '0px',
                  'margin-bottom': '0px',
                  'padding-top': '0px',
                  'padding-left': '8px',
                  'margin-right': '-20px'}

    style_dict = {**text_style, **div_style}

    if text_only:
        style_dict = text_style

    for key, value in kwargs.items():
        style_dict[key.replace('_', '-')] = value

    if not as_style:
        return style_dict

    return '; '.join([f'{k}: {v}' for k,v in style_dict.items()])

def load_vscode_styles(style_filepath='auto'):
    """Load VSCode-specific CSS styles for Jupyter outputs.
    
    Parameters
    ----------
    style_filepath : str or Path, optional
        Path to CSS file (default 'auto' uses built-in styles)
        
    Returns
    -------
    None
        Displays styled HTML in Jupyter environment
        
    Examples
    --------
    >>> load_vscode_styles()  # Load default styles
    >>> load_vscode_styles('custom.css')  # Load custom styles
    """
    if style_filepath == 'auto':
        # Use pathlib to get the directory of this file and locate the CSS file
        current_dir = Path(__file__).parent
        style_filepath = current_dir / 'css' / 'vscode.css'
    else:
        style_filepath = Path(style_filepath)
        
    css_inject = style_filepath.read_text(encoding='utf-8')
        
    init_msg = 'Jupyter styling updated for VSCode'
    
    text_css = get_jupyter_css(text_only=True, 
                              as_style=True,
                              font_size='12px')
        
    display(HTML(f"<style type='text/css'>{css_inject}</style>"+
                f"<span style='{text_css}'>{init_msg}</span>"))