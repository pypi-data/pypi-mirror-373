from ..env import (
    is_running_in_vscode_jupyter
)

from ..styles import (
    load_vscode_styles
)
    
def auto_style(verbose=False):
    """Automatically apply appropriate styling based on the environment.
    
    This function detects the current environment and applies appropriate
    styling for Jupyter notebooks. Currently supports VS Code-specific styling.
    
    Parameters
    ----------
    verbose : bool, optional
        If True, print a message when no styling is applied (default False)
        
    Returns
    -------
    None
        
    Examples
    --------
    >>> from nbqol import stylizer
    >>> stylizer.auto_style()  # Apply appropriate styling
    >>> stylizer.auto_style(verbose=True)  # With verbose messages
    """
    
    if is_running_in_vscode_jupyter():
        return load_vscode_styles()
            
    else: # message if verbose
        if verbose:
            print('No IDE-specific styling added.')