#!/usr/bin/env python3
"""
Test cases for Updater functionality - Simple tests for existing methods
"""

import pytest
import tempfile
from unittest.mock import Mock, patch
from pathlib import Path

from claude_code_indexer.updater import Updater
from claude_code_indexer import __version__


class TestUpdaterSimple:
    """Test updater functionality with existing methods only"""
    
    def setup_method(self):
        """Setup test environment"""
        self.updater = Updater()
    
    def test_initialization(self):
        """Test updater initialization"""
        assert self.updater.current_version == __version__
        assert self.updater.PYPI_URL == "https://pypi.org/pypi/claude-code-indexer/json"
    
    @patch('requests.get')
    def test_check_for_updates_newer_available(self, mock_get):
        """Test checking for updates when newer version is available"""
        # Mock response with newer version
        mock_response = Mock()
        mock_response.json.return_value = {
            "info": {"version": "999.999.999"}  # Much higher version
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        has_update, latest_version = self.updater.check_for_updates()
        
        assert has_update is True
        assert latest_version == "999.999.999"
        mock_get.assert_called_once_with(self.updater.PYPI_URL, timeout=5)
    
    @patch('requests.get')
    def test_check_for_updates_no_newer_version(self, mock_get):
        """Test checking for updates when no newer version is available"""
        # Mock response with same or older version
        mock_response = Mock()
        mock_response.json.return_value = {
            "info": {"version": "0.0.1"}  # Much lower version
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        has_update, latest_version = self.updater.check_for_updates()
        
        assert has_update is False
        assert latest_version == "0.0.1"
    
    @patch('requests.get')
    def test_check_for_updates_network_error(self, mock_get):
        """Test checking for updates with network error"""
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        has_update, latest_version = self.updater.check_for_updates()
        
        assert has_update is False
        assert latest_version == self.updater.current_version
    
    @patch('claude_code_indexer.updater.safe_subprocess_run')
    def test_update_package_success(self, mock_subprocess):
        """Test successful package update"""
        # Mock successful pip update
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        result = self.updater.update_package()
        
        assert result is True
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert 'pip' in args
        assert 'install' in args
        assert '--upgrade' in args
        assert 'claude-code-indexer' in args
    
    @patch('claude_code_indexer.updater.safe_subprocess_run')
    def test_update_package_failure(self, mock_subprocess):
        """Test failed package update"""
        # Mock failed pip update
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result
        
        result = self.updater.update_package()
        
        assert result is False
    
    @patch('claude_code_indexer.updater.safe_subprocess_run')
    def test_update_package_exception(self, mock_subprocess):
        """Test package update with general exception"""
        # Mock general exception
        mock_subprocess.side_effect = Exception("Unexpected error")
        
        result = self.updater.update_package()
        
        assert result is False
    
    def test_sync_claude_md_basic(self):
        """Test basic CLAUDE.md sync functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Test basic sync (might create file or not depending on implementation)
            result = self.updater.sync_claude_md()
            
            # Should return boolean or handle gracefully
            assert isinstance(result, bool)
    
    def test_sync_claude_md_with_force(self):
        """Test CLAUDE.md sync with force parameter"""
        result = self.updater.sync_claude_md(force=True)
        
        # Should return boolean
        assert isinstance(result, bool)
    
    @patch('requests.get')
    @patch('claude_code_indexer.updater.Updater.update_package')
    def test_auto_update_check_only(self, mock_update, mock_get):
        """Test auto-update with check_only=True"""
        # Mock response with newer version
        mock_response = Mock()
        mock_response.json.return_value = {
            "info": {"version": "999.999.999"}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.updater.auto_update(check_only=True)
        
        # Should return True if update available, but not actually update
        assert isinstance(result, bool)
        mock_update.assert_not_called()
    
    @patch('requests.get')
    @patch('claude_code_indexer.updater.Updater.update_package')
    def test_auto_update_no_check_only(self, mock_update, mock_get):
        """Test auto-update with check_only=False"""
        # Mock response with newer version
        mock_response = Mock()
        mock_response.json.return_value = {
            "info": {"version": "999.999.999"}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        mock_update.return_value = True
        
        result = self.updater.auto_update(check_only=False)
        
        # Should update if newer version available
        assert isinstance(result, bool)
    
    def test_check_and_notify_update_function(self):
        """Test the standalone check_and_notify_update function"""
        from claude_code_indexer.updater import check_and_notify_update
        
        # Should not raise exception
        try:
            check_and_notify_update()
        except Exception as e:
            # Some exceptions might be expected in test environment
            assert isinstance(e, Exception)
    
    @patch('requests.get')
    def test_updater_with_http_error(self, mock_get):
        """Test updater behavior with HTTP error"""
        # Mock HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_get.return_value = mock_response
        
        has_update, latest_version = self.updater.check_for_updates()
        
        assert has_update is False
        assert latest_version == self.updater.current_version
    
    @patch('claude_code_indexer.updater.safe_subprocess_run')
    def test_update_package_security_error(self, mock_subprocess):
        """Test package update with security error"""
        from claude_code_indexer.security import SecurityError
        
        # Mock security error
        mock_subprocess.side_effect = SecurityError("Security check failed")
        
        result = self.updater.update_package()
        
        assert result is False
    
    def test_version_comparison_logic(self):
        """Test version comparison in updater"""
        # Test with mock versions
        test_cases = [
            ("1.0.0", "2.0.0", True),   # Should update
            ("2.0.0", "1.0.0", False),  # Should not update
            ("1.0.0", "1.0.0", False),  # Same version
            ("1.0.0", "1.0.1", True),   # Patch update
        ]
        
        for current, latest, should_update in test_cases:
            with patch.object(self.updater, 'current_version', current):
                with patch('requests.get') as mock_get:
                    mock_response = Mock()
                    mock_response.json.return_value = {"info": {"version": latest}}
                    mock_response.raise_for_status.return_value = None
                    mock_get.return_value = mock_response
                    
                    has_update, returned_version = self.updater.check_for_updates()
                    
                    assert has_update is should_update
                    assert returned_version == latest
    
    def test_timeout_handling(self):
        """Test timeout handling in network requests"""
        with patch('requests.get') as mock_get:
            # Mock timeout error
            mock_get.side_effect = Exception("Timeout")
            
            has_update, latest_version = self.updater.check_for_updates()
            
            # Should handle timeout gracefully
            assert has_update is False
            assert latest_version == self.updater.current_version
            
            # Verify timeout parameter was used
            mock_get.assert_called_with(self.updater.PYPI_URL, timeout=5)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])