from os import environ as ENVIRON

def is_running_in_jupyter():
    """Check if code is running in a Jupyter environment.
    
    This function checks if the code is running within an IPython kernel,
    which is the case for Jupyter notebooks and similar environments.
    
    Returns
    -------
    bool
        True if running in Jupyter, False otherwise
        
    Examples
    --------
    >>> from nbqol import stylizer
    >>> stylizer.is_running_in_jupyter()
    True  # If running in Jupyter
    False  # If running in a standard Python environment
    """
    try: # check for running IPyKernelApp
        from IPython import get_ipython
        return "IPKernelApp" in get_ipython().config
    except (ImportError, AttributeError):
        return False

def is_running_in_vscode():
    """Check if code is running in Visual Studio Code.
    
    This function checks environment variables to determine if the code
    is running within the Visual Studio Code environment.
    
    Returns
    -------
    bool
        True if running in VS Code, False otherwise
        
    Examples
    --------
    >>> from nbqol import stylizer
    >>> stylizer.is_running_in_vscode()
    True  # If running in VS Code
    False  # If running elsewhere
    """
    return any('VSCODE' in var for var in ENVIRON)

def is_running_in_vscode_jupyter():
    """Check if code is running in a Jupyter notebook within VS Code.
    
    This function combines checks for both Jupyter and VS Code to determine
    if the code is running in a Jupyter notebook specifically within VS Code.
    
    Returns
    -------
    bool
        True if running in a VS Code Jupyter notebook, False otherwise
        
    Examples
    --------
    >>> from nbqol import stylizer
    >>> stylizer.is_running_in_vscode_jupyter()
    True  # If running in a VS Code Jupyter notebook
    False  # If running elsewhere
    """
    return is_running_in_vscode() and is_running_in_jupyter()