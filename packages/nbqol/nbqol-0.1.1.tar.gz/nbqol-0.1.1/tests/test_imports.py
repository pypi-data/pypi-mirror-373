"""Basic import tests to ensure the package can be imported correctly."""

# Modified to match the new module structure
from nbqol import settings, stylizer


def test_import_package():
    """Test that the package can be imported."""
    import nbqol
    assert nbqol is not None

def test_import_modules():
    """Test that all submodules can be imported."""
    from nbqol import devices, outputs, env, process
    assert all(module is not None for module in [devices, outputs, env, process, settings, stylizer])

def test_import_functions():
    """Test that key functions can be imported."""
    from nbqol import (
        set_autoreload, 
        hide_warnings,
        get_main_env_settings,
        set_cuda_visibles,
        notebook_path,
        path_to_git_root,
        capture_output,
        auto_style
    )
    # Just testing that imports work, not functionality
    assert callable(set_autoreload)
    assert callable(hide_warnings)
    assert callable(get_main_env_settings)
    assert callable(set_cuda_visibles)
    assert callable(notebook_path)
    assert callable(path_to_git_root)
    assert callable(capture_output)
    assert callable(auto_style)

def test_version():
    """Test that the package has a version."""
    import nbqol
    assert hasattr(nbqol, '__version__')
    assert isinstance(nbqol.__version__, str)
    assert nbqol.__version__ != ''