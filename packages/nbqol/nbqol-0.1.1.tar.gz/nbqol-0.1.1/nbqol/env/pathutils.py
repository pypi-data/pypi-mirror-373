"""
Path utilities for Jupyter notebooks and Git repositories.

This module provides utilities for finding notebook paths, locating Git
repositories, and manipulating path relationships.
"""

import os
import sys

def diffpath(path, root):
    """Get the relative path between two paths.
    
    Args:
        path (str): The target path.
        root (str): The root path to compute the relative path from.
    
    Returns:
        str: The relative path from root to path.
    """

    # Convert both paths to absolute paths
    abs_path = os.path.abspath(path)
    abs_root = os.path.abspath(root)
    return os.path.relpath(abs_path, abs_root)


def notebook_path():
    """Get the path to the current notebook.
    
    Returns:
        str: The path to the current notebook.
    """
    return os.path.abspath(sys.argv[0])

def path_to_git_root(max_depth=3):
    """Get the path to the root of the current git repository, up to max_depth levels.

    This function searches for a .git directory starting from the current working directory
    and moving up through parent directories, up to max_depth levels.

    Args:
        max_depth (int): The maximum depth to search for the git root.
    
    Returns:
        str: The path to the root of the git repository, if found.
        None: If no git repository is found within max_depth levels.
    
    Examples:
        >>> from nbqol.env import path_to_git_root
        >>> git_root = path_to_git_root()
        >>> print(git_root)
        '/path/to/git/repo'
    """
    current_dir = os.path.abspath(os.getcwd())
    for _ in range(max_depth + 1):
        if os.path.isdir(os.path.join(current_dir, '.git')):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached the root directory
            break
        current_dir = parent_dir
    return None

def add_git_root_to_sys_path(**kwargs):
    """Add the git root to the sys.path.
    
    This function finds the git repository root and adds it to sys.path, allowing
    imports from the git repository root.
    
    Args:
        **kwargs: Keyword arguments to pass to path_to_git_root.
    
    Returns:
        str: The path that was added to sys.path if successful.
        None: If no git repository is found.
    
    Examples:
        >>> from nbqol.env import add_git_root_to_sys_path
        >>> add_git_root_to_sys_path()
        '/path/to/git/repo'
    """
    verbose = kwargs.pop('verbose', False)
    git_root = path_to_git_root(**kwargs)
    
    if git_root is not None:
        if git_root not in sys.path:
            sys.path.insert(0, git_root)
            if verbose:
                print(f"Added {git_root} to sys.path")
        return git_root
    return None