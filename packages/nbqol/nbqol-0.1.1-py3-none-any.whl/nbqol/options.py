import os, json, warnings
from IPython import get_ipython
    
def set_autoreload(level='complete'):
    """Configure IPython's autoreload extension with specified level.
    
    This function configures IPython's autoreload extension to automatically reload
    Python modules before executing code. This is useful during development to see
    changes to imported modules without restarting the kernel.
    
    Parameters
    ----------
    level : str, optional
        The autoreload level to set. Options are:
        - 'off': Disable autoreload
        - 'light': Reload only modules imported with %aimport
        - 'complete': Automatically reload all modules (default)
        
    Returns
    -------
    None
    
    Examples
    --------
    >>> from nbqol import set_autoreload
    >>> set_autoreload('complete') # Enable full autoreload
    >>> set_autoreload('off')  # Disable autoreload
    
    Notes
    -----
    This function must be run in an IPython environment (e.g., Jupyter notebook).
    It will raise an EnvironmentError if run in a standard Python interpreter.
    """
    # Define the mapping between string levels and their numeric equivalents
    levels = {'off': 0, 'light': 1, 'complete': 2}

    # Convert string levels to their numeric equivalents if necessary
    if isinstance(level, str):
        level = levels.get(level.lower(), 2)  # Default to 'complete' if not found

    # Get the IPython interactive shell instance
    ip = get_ipython()
    if ip is None:
        raise EnvironmentError("This function can only be run inside an IPython environment.")

    # Load the autoreload extension if it's not already loaded
    if 'autoreload' not in ip.extension_manager.loaded:
        ip.run_line_magic('reload_ext', 'autoreload')

    elif 'autoreload' in ip.extension_manager.loaded:
        ip.run_line_magic('reload_ext', 'autoreload')

    # Always set the autoreload level to the specified level
    ip.run_line_magic('autoreload', str(level))

def get_main_env_settings(specs_only=True, sort=True,
                          include_prefix='default', 
                          exclude_prefix='default'):
    
    if exclude_prefix == 'default':
        exclude_prefix = ['LANG','LS','NIX', 'XDG','KRB', 'P9K', 'F90', 
                          'DBUS', 'MOTD', 'CONDA_BACKUP', '_CE', '_P9K']

    if exclude_prefix is None:
        exclude_prefix = [] # empty

    if not isinstance(exclude_prefix, list):
        exclude_prefix = [exclude_prefix]

    exclusions = [] # iter fill
    if len(exclude_prefix) >= 1:
        for prefix in exclude_prefix:
            exclusions += [key for key in os.environ.keys()
                           if key.startswith(prefix)]

    directory = ['HOME','HOST','USER','PWD','PATH']

    shell = ['LOGNAME','SHELL','SHLVL','TMUX','TMUX_PANE']
    
    mambaconda = ['CONDA_EXE','MAMBA_EXE','CONDA_PREFIX',
                  'CONDA_PYTHON_EXE','CONDA_PROMPT_MODIFIER']

    if include_prefix == 'default':
        include_prefix = ['JPY', 'CUDA', 'MPL', 'WORKSPACE', 'DEEPJUICE',]

    if include_prefix is None:
        include_prefix = [] # empty

    if not isinstance(include_prefix, list):
        include_prefix = [include_prefix]

    inclusions = [] # iterfill
    if len(include_prefix) >= 1:
        for prefix in include_prefix:
            inclusions += [key for key in os.environ.keys()
                           if key.startswith(prefix)]
        
    specs = [*directory, *shell, *mambaconda, *inclusions]

    env_items = os.environ.items()
    
    if sort: # put keys in order
        env_items = sorted(env_items)

    if specs_only:
        return {key: val for key, val in env_items
                if key in specs} # positive filter

    return {key: value for key, value in env_items
            if key not in exclusions} # negative filter

def save_main_env_settings_to_json(filepath, **kwargs):
    main_settings = get_main_env_settings()
    if not '.' in filepath:
        filepath += '.json'
    
    with open(filepath, 'w') as file:
        json.dump(main_settings, file)

def hide_warnings(): # all warnings
    warnings.filterwarnings('ignore')