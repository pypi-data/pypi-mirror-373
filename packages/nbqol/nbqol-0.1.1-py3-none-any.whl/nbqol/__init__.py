"""
NB-QOL: Quality of Life tools for Jupyter Notebooks

A cross-platform, modular toolkit for enhancing the Jupyter notebook experience.
"""

__version__ = '0.1.1'

from . import process
from . import env
from . import options
from . import outputs
from . import devices
from . import stylizer

# Function imports
from .outputs.capture import capture_output

# For backward compatibility
path_op = env
settings = options

from os import environ as ENVIRON

# Stylizer functions
from .stylizer import (
    auto_style,
)

# Settings functions
from .options import (
    set_autoreload,
    hide_warnings,
    get_main_env_settings,
    save_main_env_settings_to_json,
)

# Device functions
from .devices import (
    set_cuda_visibles,
    cuda_visibles,
    count_cuda_devices,
    cuda_device_report,
)

# Environment and path functions
from .env import (
    notebook_path,
    path_to_git_root,
    add_git_root_to_sys_path,
    diffpath,
)

# Processing functions - Reformat
from .process.reformat import (
    convert_to_vscode_script,
    clean_notebook,
    convert_notebook,
)

# Processing functions - Analysis
from .process.analyze import (
    execute_notebook,
    compare_notebooks,
    check_notebook_runs,
    verify_notebook_variables,
    run_notebook_as_script,
    notebook_cell_dependencies,
)

__all__ = [
    # Modules
    'devices',
    'outputs',
    'env',
    'options',
    'stylizer',
    'process',
    
    # Settings functions
    'set_autoreload',
    'hide_warnings',
    'get_main_env_settings',
    'save_main_env_settings_to_json',
    
    # Device functions
    'set_cuda_visibles',
    'cuda_visibles', 
    'count_cuda_devices',
    'cuda_device_report',
    
    # Path functions
    'notebook_path',
    'path_to_git_root',
    'add_git_root_to_sys_path',
    'diffpath',
    
    # Output functions
    'capture_output',
    
    # Stylizer functions
    'auto_style',
    
    # Convert functions
    'convert_to_vscode_script',
    'clean_notebook',
    'convert_notebook',
    
    # Analyzer functions
    'execute_notebook',
    'compare_notebooks',
    'check_notebook_runs',
    'verify_notebook_variables',
    'run_notebook_as_script',
    'notebook_cell_dependencies',
]

# Commenting out auto-styling until stylizer module is fixed
# NO_AUTO_STYLE_KEYS = [
#     'NBQOL_NO_AUTO_STYLE',
#     'NBQOL_NO_AUTODETECT'
# ]
# 
# if not any(key in ENVIRON for key in NO_AUTO_STYLE_KEYS):
#     auto_style() # apply styling
