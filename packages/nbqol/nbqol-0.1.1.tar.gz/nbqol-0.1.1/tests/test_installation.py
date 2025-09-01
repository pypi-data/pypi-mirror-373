#!/usr/bin/env python
"""Test script to verify NB-QOL installation."""

import importlib
import sys
import pytest

@pytest.mark.parametrize("module_name", [
    "nbqol", "nbqol.devices", "nbqol.outputs", "nbqol.env", "nbqol.options", "nbqol.stylizer", 
    "nbqol.process", "nbqol.process.analyze", "nbqol.process.reformat"
])
def test_import(module_name):
    """Test if a module can be imported.
    
    Args:
        module_name: Name of the module to import
    """
    module = importlib.import_module(module_name)
    assert module is not None

def test_import_script():
    """Script-mode test function to verify imports from command line."""
    # Updated to match the new module structure
    modules_to_test = [
        "nbqol",
        "nbqol.devices",
        "nbqol.outputs",
        "nbqol.env",
        "nbqol.options",
        "nbqol.stylizer",
        "nbqol.process"
    ]
    
    all_passed = True
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✓ Successfully imported {module}")
        except ImportError as e:
            all_passed = False
            print(f"✗ Failed to import {module}: {e}")
    
    print("\nInstallation test result:", "PASSED" if all_passed else "FAILED")
    # Use assert instead of returning value
    assert all_passed

if __name__ == "__main__":
    success = test_import_script()
    sys.exit(0 if success else 1)