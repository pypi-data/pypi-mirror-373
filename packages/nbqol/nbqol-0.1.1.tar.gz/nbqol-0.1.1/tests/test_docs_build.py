#!/usr/bin/env python
"""Test script to verify Sphinx documentation build."""

import os
import subprocess
import sys
import tempfile
import shutil

def test_docs_build():
    """Test if the Sphinx documentation can be built successfully."""
    print("Testing Sphinx documentation build...")
    
    # Create a temporary directory for the build output
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Adjust path since test file is now in tests/ directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        docs_dir = os.path.join(project_root, 'docs')
        source_dir = os.path.join(docs_dir, 'source')
        conf_dir = docs_dir  # Configuration directory is the docs directory
        
        # Run the sphinx-build command with named arguments for clarity
        cmd = [
            'sphinx-build',
            '-b', 'html',           # Build format: HTML
            '-W',                   # Treat warnings as errors
            '-v',                   # Verbose output
            '-c', conf_dir,         # Configuration directory
            source_dir,             # Source directory
            temp_dir                # Output directory
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,    # Capture stdout and stderr
            text=True,              # Return strings rather than bytes
            check=False             # Don't raise exception on non-zero return code
        )
        
        # Print the output for debugging
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Check if the build was successful
        build_success = False
        if result.returncode == 0:
            index_path = os.path.join(temp_dir, 'index.html')
            if os.path.exists(index_path):
                print(f"✓ Documentation build successful: index.html found")
                build_success = True
            else:
                print(f"✗ Documentation build failed: index.html not found")
        else:
            print(f"✗ Documentation build failed with return code: {result.returncode}")
        
        # Use assert instead of returning a value
        assert build_success, "Documentation build failed"
    
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    try:
        test_docs_build()
        sys.exit(0)
    except AssertionError as e:
        print(f"Error: {e}")
        sys.exit(1)