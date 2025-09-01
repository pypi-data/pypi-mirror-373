"""
Environment detection and path utilities for Jupyter notebooks.

This module provides tools for detecting notebook paths, Git repository paths,
and other environment-related functionality.
"""

from .pathutils import (
    notebook_path,
    path_to_git_root,
    add_git_root_to_sys_path,
    diffpath,
)

from .detect import (
    is_running_in_jupyter,
    is_running_in_vscode,
    is_running_in_vscode_jupyter,
)

__all__ = [
    'notebook_path',
    'path_to_git_root',
    'add_git_root_to_sys_path',
    'diffpath',
    'is_running_in_jupyter',
    'is_running_in_vscode',
    'is_running_in_vscode_jupyter',
]