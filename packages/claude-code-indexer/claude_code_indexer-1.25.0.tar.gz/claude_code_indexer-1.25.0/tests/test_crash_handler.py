#!/usr/bin/env python3
"""
Comprehensive tests for CrashHandler class
"""

import pytest
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open, call

from claude_code_indexer.crash_handler import CrashHandler, install_crash_handler


class TestCrashHandler:
    """Test suite for CrashHandler class"""
    
    @pytest.fixture
    def temp_crash_dir(self):
        """Create temporary crash directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def crash_handler(self, temp_crash_dir):
        """Create CrashHandler instance with temp directory"""
        with patch('pathlib.Path.home', return_value=temp_crash_dir):
            handler = CrashHandler()
            handler.crash_dir = temp_crash_dir / ".claude-code-indexer" / "crashes"
            handler.crash_dir.mkdir(parents=True, exist_ok=True)
            return handler
    
    def test_init(self):
        """Test CrashHandler initialization"""
        with patch('pathlib.Path.home', return_value=Path("/home/user")):
            with patch('pathlib.Path.mkdir'):
                handler = CrashHandler()
                
                assert handler.crash_dir == Path("/home/user/.claude-code-indexer/crashes")
                assert handler.reporter is not None
                assert handler._original_excepthook == sys.excepthook
                assert handler._crash_id is None
    
    def test_init_creates_crash_directory(self, temp_crash_dir):
        """Test that initialization creates crash directory"""
        with patch('pathlib.Path.home', return_value=temp_crash_dir):
            handler = CrashHandler()
            
            expected_dir = temp_crash_dir / ".claude-code-indexer" / "crashes"
            assert expected_dir.exists()
            assert expected_dir.is_dir()
    
    def test_save_crash_dump(self, crash_handler):
        """Test save_crash_dump creates proper crash file"""
        # Create test exception
        try:
            raise ValueError("Test error message")
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        
        with patch('claude_code_indexer.crash_handler.__version__', '1.0.0'):
            with patch.object(crash_handler.reporter, 'get_system_info', return_value={"os": "TestOS"}):
                crash_file = crash_handler.save_crash_dump(exc_type, exc_value, exc_traceback)
        
        # Verify crash file created
        assert crash_file.exists()
        assert crash_file.parent == crash_handler.crash_dir
        assert crash_file.name.startswith("crash_")
        assert crash_file.name.endswith(".json")
        
        # Verify crash data
        with open(crash_file, 'r') as f:
            crash_data = json.load(f)
        
        assert crash_data["crash_id"] == crash_handler._crash_id
        assert crash_data["error_type"] == "ValueError"
        assert crash_data["error_message"] == "Test error message"
        assert "Traceback" in crash_data["traceback"]
        assert crash_data["version"] == "1.0.0"
        assert crash_data["system_info"] == {"os": "TestOS"}
        assert "command" in crash_data
    
    def test_save_crash_dump_with_complex_exception(self, crash_handler):
        """Test save_crash_dump with complex exception chain"""
        # Create nested exception
        try:
            try:
                raise RuntimeError("Inner error")
            except RuntimeError as e:
                raise ValueError("Outer error") from e
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        
        crash_file = crash_handler.save_crash_dump(exc_type, exc_value, exc_traceback)
        
        # Verify nested traceback captured
        with open(crash_file, 'r') as f:
            crash_data = json.load(f)
        
        assert "RuntimeError: Inner error" in crash_data["traceback"]
        assert "ValueError: Outer error" in crash_data["traceback"]
        assert "The above exception was the direct cause" in crash_data["traceback"]
    
    def test_prompt_user_action_option_1(self, crash_handler):
        """Test prompt_user_action when user selects option 1 (create issue)"""
        crash_data = {
            "crash_id": "test_crash_123",
            "error_type": "TestError",
            "error_message": "Test message",
            "traceback": "Test traceback"
        }
        
        with patch('rich.console.Console.print'):
            with patch('rich.prompt.Prompt.ask', return_value="1"):
                result = crash_handler.prompt_user_action(crash_data)
        
        assert result == True
    
    def test_prompt_user_action_option_2_then_yes(self, crash_handler):
        """Test prompt_user_action when user views details then creates issue"""
        crash_data = {
            "crash_id": "test_crash_123",
            "error_type": "TestError",
            "error_message": "Test message",
            "traceback": "Test traceback\nLine 2\nLine 3"
        }
        
        with patch('rich.console.Console.print'):
            with patch('rich.prompt.Prompt.ask', return_value="2"):
                with patch('rich.prompt.Confirm.ask', return_value=True):
                    result = crash_handler.prompt_user_action(crash_data)
        
        assert result == True
    
    def test_prompt_user_action_option_2_then_no(self, crash_handler):
        """Test prompt_user_action when user views details then declines"""
        crash_data = {
            "crash_id": "test_crash_123",
            "error_type": "TestError",
            "error_message": "Test message",
            "traceback": "Test traceback"
        }
        
        with patch('rich.console.Console.print'):
            with patch('rich.prompt.Prompt.ask', return_value="2"):
                with patch('rich.prompt.Confirm.ask', return_value=False):
                    result = crash_handler.prompt_user_action(crash_data)
        
        assert result == False
    
    def test_prompt_user_action_option_3(self, crash_handler):
        """Test prompt_user_action when user exits without reporting"""
        crash_data = {
            "crash_id": "test_crash_123",
            "error_type": "TestError",
            "error_message": "Test message",
            "traceback": "Test traceback"
        }
        
        with patch('rich.console.Console.print'):
            with patch('rich.prompt.Prompt.ask', return_value="3"):
                result = crash_handler.prompt_user_action(crash_data)
        
        assert result == False
    
    def test_handle_crash_keyboard_interrupt(self, crash_handler):
        """Test handle_crash ignores KeyboardInterrupt"""
        mock_excepthook = Mock()
        crash_handler._original_excepthook = mock_excepthook
        
        # Create KeyboardInterrupt
        try:
            raise KeyboardInterrupt()
        except KeyboardInterrupt:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        
        crash_handler.handle_crash(exc_type, exc_value, exc_traceback)
        
        # Should call original excepthook
        mock_excepthook.assert_called_once_with(exc_type, exc_value, exc_traceback)
    
    def test_handle_crash_interactive_mode_report(self, crash_handler):
        """Test handle_crash in interactive mode when user reports"""
        # Create test exception
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        
        with patch('sys.stdin.isatty', return_value=True):
            with patch('sys.stdout.isatty', return_value=True):
                with patch.object(crash_handler, 'save_crash_dump') as mock_save:
                    with patch.object(crash_handler, 'prompt_user_action', return_value=True) as mock_prompt:
                        with patch.object(crash_handler, 'create_github_issue') as mock_create:
                            # Create mock crash file
                            mock_crash_file = crash_handler.crash_dir / "test_crash.json"
                            mock_crash_file.write_text('{"crash_id": "test"}')
                            mock_save.return_value = mock_crash_file
                            
                            crash_handler.handle_crash(exc_type, exc_value, exc_traceback)
        
        mock_save.assert_called_once()
        mock_prompt.assert_called_once()
        mock_create.assert_called_once()
    
    def test_handle_crash_interactive_mode_no_report(self, crash_handler):
        """Test handle_crash in interactive mode when user declines"""
        # Create test exception
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        
        with patch('sys.stdin.isatty', return_value=True):
            with patch('sys.stdout.isatty', return_value=True):
                with patch.object(crash_handler, 'save_crash_dump') as mock_save:
                    with patch.object(crash_handler, 'prompt_user_action', return_value=False) as mock_prompt:
                        with patch.object(crash_handler, 'create_github_issue') as mock_create:
                            # Create mock crash file
                            mock_crash_file = crash_handler.crash_dir / "test_crash.json"
                            mock_crash_file.write_text('{"crash_id": "test"}')
                            mock_save.return_value = mock_crash_file
                            
                            crash_handler.handle_crash(exc_type, exc_value, exc_traceback)
        
        mock_save.assert_called_once()
        mock_prompt.assert_called_once()
        mock_create.assert_not_called()
    
    def test_handle_crash_non_interactive_mode(self, crash_handler):
        """Test handle_crash in non-interactive mode"""
        # Create test exception
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        
        with patch('sys.stdin.isatty', return_value=False):
            with patch('sys.stdout.isatty', return_value=False):
                with patch('rich.console.Console.print'):
                    with patch.object(crash_handler, 'save_crash_dump') as mock_save:
                        with patch.object(crash_handler, 'show_reporting_instructions') as mock_show:
                            # Create mock crash file
                            mock_crash_file = crash_handler.crash_dir / "test_crash.json"
                            mock_crash_file.write_text('{"crash_id": "test"}')
                            mock_save.return_value = mock_crash_file
                            
                            crash_handler.handle_crash(exc_type, exc_value, exc_traceback)
        
        mock_save.assert_called_once()
        mock_show.assert_called_once()
    
    def test_handle_crash_handler_failure(self, crash_handler):
        """Test handle_crash when crash handler itself fails"""
        # Create test exception
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        
        mock_excepthook = Mock()
        crash_handler._original_excepthook = mock_excepthook
        
        with patch.object(crash_handler, 'save_crash_dump', side_effect=Exception("Handler error")):
            with patch('claude_code_indexer.crash_handler.log_error') as mock_log:
                crash_handler.handle_crash(exc_type, exc_value, exc_traceback)
        
        # Should log error and call original excepthook
        mock_log.assert_called_once_with("Crash handler failed: Handler error")
        mock_excepthook.assert_called_once_with(exc_type, exc_value, exc_traceback)
    
    def test_create_github_issue(self, crash_handler):
        """Test create_github_issue method"""
        crash_data = {
            "crash_id": "test_crash_123",
            "timestamp": "20240101_120000",
            "error_type": "TestError",
            "error_message": "This is a very long error message that should be truncated in the title",
            "command": "test command",
            "traceback": "Test traceback"
        }
        
        with patch('rich.console.Console.print'):
            with patch.object(crash_handler.reporter, 'report_issue', return_value=True) as mock_report:
                crash_handler.create_github_issue(crash_data)
        
        # Verify reporter called with correct parameters
        mock_report.assert_called_once()
        call_args = mock_report.call_args[1]
        
        assert call_args["error_type"] == "TestError"
        assert call_args["error_message"] == crash_data["error_message"]
        assert call_args["command"] == "test command"
        assert call_args["traceback"] == "Test traceback"
        assert "Crash ID" in call_args["additional_info"]
        assert "test_crash_123" in call_args["additional_info"]
        assert call_args["auto_create"] == False
    
    def test_create_github_issue_failure(self, crash_handler):
        """Test create_github_issue when reporting fails"""
        crash_data = {
            "crash_id": "test_crash_123",
            "timestamp": "20240101_120000",
            "error_type": "TestError",
            "error_message": "Test error",
            "command": "test command",
            "traceback": "Test traceback"
        }
        
        with patch('rich.console.Console.print') as mock_print:
            with patch.object(crash_handler.reporter, 'report_issue', return_value=False):
                crash_handler.create_github_issue(crash_data)
        
        # Should print tip about attaching crash dump
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("crash dump file" in str(call) for call in print_calls)
    
    def test_show_reporting_instructions_with_gh(self, crash_handler):
        """Test show_reporting_instructions when GitHub CLI is available"""
        crash_data = {
            "crash_id": "test_crash_123",
            "error_type": "TestError",
            "error_message": "Test error message"
        }
        
        crash_handler.reporter.gh_available = True
        
        with patch('rich.console.Console.print') as mock_print:
            crash_handler.show_reporting_instructions(crash_data)
        
        # Should show gh command
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("gh issue create" in str(call) for call in print_calls)
        assert any("https://github.com/tuannx/claude-prompts/issues/new" in str(call) for call in print_calls)
        assert any("test_crash_123" in str(call) for call in print_calls)
    
    def test_show_reporting_instructions_without_gh(self, crash_handler):
        """Test show_reporting_instructions when GitHub CLI is not available"""
        crash_data = {
            "crash_id": "test_crash_123",
            "error_type": "TestError",
            "error_message": "Test error"
        }
        
        crash_handler.reporter.gh_available = False
        
        with patch('rich.console.Console.print') as mock_print:
            crash_handler.show_reporting_instructions(crash_data)
        
        # Should still show manual reporting URL
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("https://github.com/tuannx/claude-prompts/issues/new" in str(call) for call in print_calls)
    
    def test_install(self, crash_handler):
        """Test install method"""
        original_hook = sys.excepthook
        
        with patch('claude_code_indexer.crash_handler.log_info') as mock_log:
            crash_handler.install()
        
        assert sys.excepthook == crash_handler.handle_crash
        mock_log.assert_called_once_with("Crash handler installed")
        
        # Restore original
        sys.excepthook = original_hook
    
    def test_uninstall(self, crash_handler):
        """Test uninstall method"""
        # First install
        crash_handler.install()
        
        with patch('claude_code_indexer.crash_handler.log_info') as mock_log:
            crash_handler.uninstall()
        
        assert sys.excepthook == crash_handler._original_excepthook
        mock_log.assert_called_once_with("Crash handler uninstalled")
    
    def test_crash_id_generation(self, crash_handler):
        """Test unique crash ID generation"""
        # Create two exceptions
        try:
            raise ValueError("Error 1")
        except ValueError:
            exc_type1, exc_value1, exc_traceback1 = sys.exc_info()
        
        try:
            raise ValueError("Error 2")
        except ValueError:
            exc_type2, exc_value2, exc_traceback2 = sys.exc_info()
        
        # Save both crashes
        crash_file1 = crash_handler.save_crash_dump(exc_type1, exc_value1, exc_traceback1)
        crash_id1 = crash_handler._crash_id
        
        # Small delay to ensure different timestamp
        import time
        time.sleep(0.01)
        
        crash_file2 = crash_handler.save_crash_dump(exc_type2, exc_value2, exc_traceback2)
        crash_id2 = crash_handler._crash_id
        
        # Crash IDs should be different
        assert crash_id1 != crash_id2
        assert crash_file1 != crash_file2
    
    def test_concurrent_crash_handling(self, crash_handler):
        """Test handling multiple crashes concurrently"""
        import threading
        
        crash_files = []
        
        def cause_crash(thread_id):
            try:
                raise ValueError(f"Error from thread {thread_id}")
            except ValueError:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                crash_file = crash_handler.save_crash_dump(exc_type, exc_value, exc_traceback)
                crash_files.append(crash_file)
        
        # Create multiple threads that crash
        threads = []
        for i in range(5):
            t = threading.Thread(target=cause_crash, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # All crash files should be created
        assert len(crash_files) == 5
        assert all(f.exists() for f in crash_files)
        
        # All crash files should be unique
        assert len(set(crash_files)) == 5


class TestInstallCrashHandler:
    """Test the install_crash_handler function"""
    
    def test_install_crash_handler_function(self):
        """Test install_crash_handler convenience function"""
        original_hook = sys.excepthook
        
        with patch('claude_code_indexer.crash_handler.CrashHandler.install') as mock_install:
            handler = install_crash_handler()
        
        assert handler is not None
        assert isinstance(handler, CrashHandler)
        mock_install.assert_called_once()
        
        # Restore original
        sys.excepthook = original_hook
    
    def test_crash_handler_integration(self):
        """Test crash handler integration with actual exception"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                handler = CrashHandler()
                
                # Install handler
                handler.install()
                
                # Simulate crash in non-interactive mode
                with patch('sys.stdin.isatty', return_value=False):
                    with patch('sys.stdout.isatty', return_value=False):
                        with patch('rich.console.Console.print'):
                            try:
                                raise RuntimeError("Test crash")
                            except RuntimeError:
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                handler.handle_crash(exc_type, exc_value, exc_traceback)
                
                # Verify crash file created
                crash_files = list(handler.crash_dir.glob("crash_*.json"))
                assert len(crash_files) == 1
                
                # Verify crash data
                with open(crash_files[0], 'r') as f:
                    crash_data = json.load(f)
                assert crash_data["error_type"] == "RuntimeError"
                assert crash_data["error_message"] == "Test crash"
                
                # Uninstall
                handler.uninstall()