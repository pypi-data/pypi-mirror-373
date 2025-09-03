#!/usr/bin/env python3
"""
Test update functionality to ensure users don't get stuck
"""

import os
import subprocess
import tempfile
import shutil
import pytest
from pathlib import Path


class TestUpdateFunctionality:
    """Test suite for update functionality"""
    
    def test_update_command_exists(self):
        """Test that update command is available"""
        # Create a temporary virtual environment
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            subprocess.run([
                "python", "-m", "venv", str(venv_path)
            ], check=True)
            
            # Install the package
            pip_path = venv_path / "bin" / "pip"
            subprocess.run([
                str(pip_path), "install", "claude-code-indexer"
            ], check=True)
            
            # Check if update command exists
            cci_path = venv_path / "bin" / "cci"
            result = subprocess.run([
                str(cci_path), "update", "--help"
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            assert "Update claude-code-indexer" in result.stdout
    
    def test_update_check_functionality(self):
        """Test update check works without errors"""
        # Create a temporary virtual environment
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            subprocess.run([
                "python", "-m", "venv", str(venv_path)
            ], check=True)
            
            # Install older version first
            pip_path = venv_path / "bin" / "pip"
            subprocess.run([
                str(pip_path), "install", "setuptools"  # Required for older versions
            ], check=True)
            
            subprocess.run([
                str(pip_path), "install", "claude-code-indexer==1.19.0"
            ], check=True)
            
            # Run update check
            cci_path = venv_path / "bin" / "cci"
            result = subprocess.run([
                str(cci_path), "update", "--check"
            ], capture_output=True, text=True)
            
            # Should detect newer version available
            assert result.returncode == 0
            assert ("New version available" in result.stdout or 
                   "already up to date" in result.stdout)
    
    def test_cli_aliases_work(self):
        """Test that both claude-code-indexer and cci aliases work"""
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            subprocess.run([
                "python", "-m", "venv", str(venv_path)
            ], check=True)
            
            # Install the package
            pip_path = venv_path / "bin" / "pip"
            subprocess.run([
                str(pip_path), "install", "claude-code-indexer"
            ], check=True)
            
            # Test cci alias
            cci_path = venv_path / "bin" / "cci"
            result = subprocess.run([
                str(cci_path), "--version"
            ], capture_output=True, text=True)
            assert result.returncode == 0
            
            # Test claude-code-indexer command
            full_path = venv_path / "bin" / "claude-code-indexer"
            result = subprocess.run([
                str(full_path), "--version"
            ], capture_output=True, text=True)
            assert result.returncode == 0
    
    def test_dependencies_installed_correctly(self):
        """Test that all required dependencies are installed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            subprocess.run([
                "python", "-m", "venv", str(venv_path)
            ], check=True)
            
            # Install the package
            pip_path = venv_path / "bin" / "pip"
            subprocess.run([
                str(pip_path), "install", "claude-code-indexer"
            ], check=True)
            
            # Check critical imports work
            python_path = venv_path / "bin" / "python"
            test_imports = [
                "import claude_code_indexer",
                "from claude_code_indexer import CodeGraphIndexer",
                "import click",
                "import rich",
                "import pandas",
                "import networkx",
                "import ensmallen"
            ]
            
            for import_stmt in test_imports:
                result = subprocess.run([
                    str(python_path), "-c", import_stmt
                ], capture_output=True, text=True)
                assert result.returncode == 0, f"Failed to import: {import_stmt}"
    
    def test_no_breaking_changes_in_api(self):
        """Test that basic API remains compatible"""
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            subprocess.run([
                "python", "-m", "venv", str(venv_path)
            ], check=True)
            
            # Install the package
            pip_path = venv_path / "bin" / "pip"
            subprocess.run([
                str(pip_path), "install", "claude-code-indexer"
            ], check=True)
            
            # Test basic API compatibility
            python_path = venv_path / "bin" / "python"
            test_code = '''
import tempfile
from pathlib import Path
from claude_code_indexer import CodeGraphIndexer

# Create test directory
with tempfile.TemporaryDirectory() as temp_dir:
    # Test basic initialization
    indexer = CodeGraphIndexer(project_path=temp_dir)
    
    # Test basic methods exist
    assert hasattr(indexer, 'index_codebase')
    assert hasattr(indexer, 'search')
    assert hasattr(indexer, 'query_important_code')
    assert hasattr(indexer, 'get_project_stats')
    
    print("API compatibility test passed")
'''
            
            result = subprocess.run([
                str(python_path), "-c", test_code
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            assert "API compatibility test passed" in result.stdout


@pytest.mark.skipif(
    os.getenv("SKIP_INTEGRATION_TESTS", "false").lower() == "true",
    reason="Skipping integration tests"
)
class TestUpdateIntegration:
    """Integration tests for update functionality"""
    
    def test_actual_update_process(self):
        """Test actual update from older to newer version"""
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"
            
            # Create virtual environment
            subprocess.run([
                "python", "-m", "venv", str(venv_path)
            ], check=True)
            
            pip_path = venv_path / "bin" / "pip"
            
            # Install setuptools first (required for older versions)
            subprocess.run([
                str(pip_path), "install", "setuptools"
            ], check=True)
            
            # Install older version
            subprocess.run([
                str(pip_path), "install", "claude-code-indexer==1.19.0"
            ], check=True)
            
            # Verify old version
            cci_path = venv_path / "bin" / "cci"
            result = subprocess.run([
                str(cci_path), "--version"
            ], capture_output=True, text=True)
            assert "1.19.0" in result.stdout
            
            # Update to latest
            result = subprocess.run([
                str(cci_path), "update", "--yes"
            ], capture_output=True, text=True)
            
            # Should succeed
            assert result.returncode == 0
            
            # Verify new version
            result = subprocess.run([
                str(cci_path), "--version"
            ], capture_output=True, text=True)
            assert "1.19.0" not in result.stdout  # Should be updated


if __name__ == "__main__":
    pytest.main([__file__, "-v"])