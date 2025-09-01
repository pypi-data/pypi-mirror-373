"""Integration tests for the CLI functionality."""

import subprocess
import sys
import os
import tempfile
from pathlib import Path
import pytest


def run_cli_command(args, cwd=None):
    """Helper function to run CLI commands and capture output."""
    cmd = [sys.executable, '-m', 'nbqol.cli'] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or os.getcwd()
    )
    return result


class TestCLIIntegration:
    """Test suite for CLI integration functionality."""
    
    def test_cli_help(self):
        """Test that CLI help command works."""
        result = run_cli_command(['--help'])
        
        assert result.returncode == 0
        assert 'NB-QOL: Quality-of-life toolkit for Jupyter notebooks' in result.stdout
        assert 'device-info' in result.stdout
        assert 'style' in result.stdout
    
    def test_cli_version(self):
        """Test that CLI version command works."""
        result = run_cli_command(['--version'])
        
        assert result.returncode == 0
        assert 'NB-QOL version' in result.stdout
        assert '0.1.0' in result.stdout
    
    def test_cli_no_command(self):
        """Test CLI behavior when no command is provided."""
        result = run_cli_command([])
        
        assert result.returncode == 0
        assert 'usage:' in result.stdout
        assert 'NB-QOL: Quality-of-life toolkit for Jupyter notebooks' in result.stdout
    
    def test_device_info_command(self):
        """Test the device-info command."""
        result = run_cli_command(['device-info'])
        
        # Command should complete (may succeed or fail depending on CUDA availability)
        assert result.returncode in [0, 1]
        
        if result.returncode == 0:
            # If command succeeds, there should be output (stdout or stderr)
            # Some CUDA operations might output to stderr even on success
            assert len(result.stdout) > 0 or len(result.stderr) > 0
        else:
            # If CUDA is not available, should show error message
            assert 'CUDA tools not available' in result.stdout or 'not available' in result.stderr
    
    def test_style_command(self):
        """Test the style command."""
        result = run_cli_command(['style'])
        
        # Style command should complete but may fail outside Jupyter environment
        assert result.returncode in [0, 1]
        
        if result.returncode == 0:
            assert 'Styling applied successfully' in result.stdout
        else:
            # Should show appropriate error message when not in Jupyter
            assert 'Styling not available' in result.stdout or 'intended to be run in a Jupyter environment' in result.stdout
    
    def test_invalid_command(self):
        """Test CLI behavior with invalid command."""
        result = run_cli_command(['invalid-command'])
        
        assert result.returncode != 0
        assert 'usage:' in result.stderr or 'error:' in result.stderr
    
    def test_cli_as_script(self):
        """Test running CLI as a script directly."""
        project_root = Path(__file__).parent.parent
        cli_path = project_root / 'nbqol' / 'cli.py'
        
        result = subprocess.run(
            [sys.executable, str(cli_path), '--version'],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        assert result.returncode == 0
        assert 'NB-QOL version' in result.stdout
    
    def test_cli_importable(self):
        """Test that CLI module can be imported without errors."""
        result = subprocess.run(
            [sys.executable, '-c', 'from nbqol.cli import main; print("CLI import successful")'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'CLI import successful' in result.stdout
    
    def test_cli_main_function(self):
        """Test that the main function can be called programmatically."""
        result = subprocess.run(
            [sys.executable, '-c', 
             'import sys; from nbqol.cli import main; '
             'sys.argv = ["nbqol", "--version"]; '
             'exit_code = main(); '
             'print(f"Exit code: {exit_code}")'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'NB-QOL version' in result.stdout
        assert 'Exit code: 0' in result.stdout


class TestCLIErrorHandling:
    """Test error handling in CLI commands."""
    
    def test_device_info_error_handling(self):
        """Test device-info command error handling."""
        # This tests the import error handling path
        result = run_cli_command(['device-info'])
        
        # Should not crash, regardless of CUDA availability
        assert result.returncode in [0, 1]
        
        # Should have some output (either device info or error message)
        assert len(result.stdout) > 0 or len(result.stderr) > 0
    
    def test_style_error_handling(self):
        """Test style command error handling."""
        result = run_cli_command(['style'])
        
        # Should not crash, even if styling is not available
        assert result.returncode in [0, 1]
        
        # Should have some output (either success message or error)
        assert len(result.stdout) > 0 or len(result.stderr) > 0


class TestCLIInDifferentEnvironments:
    """Test CLI behavior in different environments."""
    
    def test_cli_with_different_working_directories(self):
        """Test CLI works from different working directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_cli_command(['--version'], cwd=tmpdir)
            
            assert result.returncode == 0
            assert 'NB-QOL version' in result.stdout
    
    def test_cli_with_environment_variables(self):
        """Test CLI behavior with different environment variables."""
        # Test with NO_AUTO_STYLE environment variable
        env = os.environ.copy()
        env['NBQOL_NO_AUTO_STYLE'] = '1'
        
        result = subprocess.run(
            [sys.executable, '-m', 'nbqol.cli', '--version'],
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0
        assert 'NB-QOL version' in result.stdout


if __name__ == '__main__':
    # Allow running the test file directly
    pytest.main([__file__, '-v'])
