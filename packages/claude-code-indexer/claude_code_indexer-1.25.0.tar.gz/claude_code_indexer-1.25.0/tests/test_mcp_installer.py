#!/usr/bin/env python3
"""
Comprehensive tests for MCPInstaller class
"""

import pytest
import json
import platform
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

from claude_code_indexer.mcp_installer import MCPInstaller


class TestMCPInstaller:
    """Test suite for MCPInstaller class"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def installer(self):
        """Create MCPInstaller instance"""
        return MCPInstaller()
    
    def test_init(self):
        """Test MCPInstaller initialization"""
        installer = MCPInstaller()
        
        assert installer.platform == platform.system()
        assert installer.desktop_config_path is not None
        assert installer.code_config_path is not None
        assert installer.config_path == installer.desktop_config_path  # Default
    
    @pytest.mark.parametrize("system,expected_desktop,expected_code", [
        ("Darwin", "Library/Application Support/Claude/claude_desktop_config.json",
         "Library/Application Support/Claude Code/claude_desktop_config.json"),
        ("Windows", "AppData/Roaming/Claude/claude_desktop_config.json",
         "AppData/Roaming/Claude Code/claude_desktop_config.json"),
        ("Linux", ".config/Claude/claude_desktop_config.json",
         ".config/Claude Code/claude_desktop_config.json"),
    ])
    def test_config_paths_by_platform(self, system, expected_desktop, expected_code):
        """Test config path detection for different platforms"""
        with patch('platform.system', return_value=system):
            with patch('pathlib.Path.home', return_value=Path("/home/user")):
                installer = MCPInstaller()
                
                assert str(installer.desktop_config_path).endswith(expected_desktop)
                assert str(installer.code_config_path).endswith(expected_code)
    
    def test_config_path_unsupported_platform(self):
        """Test config path on unsupported platform"""
        with patch('platform.system', return_value="UnknownOS"):
            installer = MCPInstaller()
            assert installer.desktop_config_path is None
            assert installer.code_config_path is None
    
    def test_check_claude_desktop_exists(self, temp_config_dir):
        """Test check_claude_desktop when directory exists"""
        with patch.object(MCPInstaller, '_get_desktop_config_path', return_value=temp_config_dir / "claude_desktop_config.json"):
            installer = MCPInstaller()
            
            # Create parent directory
            installer.desktop_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            assert installer.check_claude_desktop() == True
    
    def test_check_claude_desktop_not_exists(self, temp_config_dir):
        """Test check_claude_desktop when directory doesn't exist"""
        with patch.object(MCPInstaller, '_get_desktop_config_path', return_value=temp_config_dir / "nonexistent" / "claude_desktop_config.json"):
            installer = MCPInstaller()
            assert installer.check_claude_desktop() == False
    
    def test_check_claude_desktop_no_path(self):
        """Test check_claude_desktop when path is None"""
        installer = MCPInstaller()
        installer.desktop_config_path = None
        assert installer.check_claude_desktop() == False
    
    def test_check_claude_code_exists(self, temp_config_dir):
        """Test check_claude_code when directory exists"""
        with patch.object(MCPInstaller, '_get_code_config_path', return_value=temp_config_dir / "claude_code_config.json"):
            installer = MCPInstaller()
            
            # Create parent directory
            installer.code_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            assert installer.check_claude_code() == True
    
    def test_check_claude_code_not_exists(self, temp_config_dir):
        """Test check_claude_code when directory doesn't exist"""
        with patch.object(MCPInstaller, '_get_code_config_path', return_value=temp_config_dir / "nonexistent" / "claude_code_config.json"):
            installer = MCPInstaller()
            assert installer.check_claude_code() == False
    
    def test_detect_claude_app_code_installed(self, installer):
        """Test detect_claude_app when Claude Code is installed"""
        with patch.object(installer, 'check_claude_code', return_value=True):
            with patch.object(installer, 'check_claude_desktop', return_value=False):
                result = installer.detect_claude_app()
                
                assert result == "code"
                assert installer.config_path == installer.code_config_path
    
    def test_detect_claude_app_desktop_installed(self, installer):
        """Test detect_claude_app when only Claude Desktop is installed"""
        with patch.object(installer, 'check_claude_code', return_value=False):
            with patch.object(installer, 'check_claude_desktop', return_value=True):
                result = installer.detect_claude_app()
                
                assert result == "desktop"
                assert installer.config_path == installer.desktop_config_path
    
    def test_detect_claude_app_both_installed(self, installer):
        """Test detect_claude_app when both apps are installed (prefers Code)"""
        with patch.object(installer, 'check_claude_code', return_value=True):
            with patch.object(installer, 'check_claude_desktop', return_value=True):
                result = installer.detect_claude_app()
                
                assert result == "code"
                assert installer.config_path == installer.code_config_path
    
    def test_detect_claude_app_none_installed(self, installer):
        """Test detect_claude_app when no apps are installed"""
        with patch.object(installer, 'check_claude_code', return_value=False):
            with patch.object(installer, 'check_claude_desktop', return_value=False):
                result = installer.detect_claude_app()
                
                assert result == "none"
    
    def test_load_config_file_exists(self, temp_config_dir):
        """Test load_config when config file exists"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        test_config = {"mcpServers": {"test": {"command": "test"}}}
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        installer = MCPInstaller()
        installer.config_path = config_file
        
        loaded_config = installer.load_config()
        assert loaded_config == test_config
    
    def test_load_config_file_not_exists(self, temp_config_dir):
        """Test load_config when config file doesn't exist"""
        installer = MCPInstaller()
        installer.config_path = temp_config_dir / "nonexistent.json"
        
        loaded_config = installer.load_config()
        assert loaded_config == {"mcpServers": {}}
    
    def test_load_config_no_path(self):
        """Test load_config when config_path is None"""
        installer = MCPInstaller()
        installer.config_path = None
        
        loaded_config = installer.load_config()
        assert loaded_config == {"mcpServers": {}}
    
    def test_load_config_corrupted_json(self, temp_config_dir):
        """Test load_config with corrupted JSON"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        
        with open(config_file, 'w') as f:
            f.write("{invalid json}")
        
        installer = MCPInstaller()
        installer.config_path = config_file
        
        loaded_config = installer.load_config()
        assert loaded_config == {"mcpServers": {}}
    
    def test_save_config_success(self, temp_config_dir):
        """Test save_config successful save"""
        config_file = temp_config_dir / "subdir" / "claude_desktop_config.json"
        test_config = {"mcpServers": {"test": {"command": "test"}}}
        
        installer = MCPInstaller()
        installer.config_path = config_file
        
        with patch('rich.console.Console.print'):
            result = installer.save_config(test_config)
        
        assert result == True
        assert config_file.exists()
        
        # Verify saved content
        with open(config_file, 'r') as f:
            saved_config = json.load(f)
        assert saved_config == test_config
    
    def test_save_config_with_backup(self, temp_config_dir):
        """Test save_config creates backup of existing file"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        original_config = {"mcpServers": {"old": {"command": "old"}}}
        
        # Create original file
        with open(config_file, 'w') as f:
            json.dump(original_config, f)
        
        installer = MCPInstaller()
        installer.config_path = config_file
        
        new_config = {"mcpServers": {"new": {"command": "new"}}}
        
        with patch('rich.console.Console.print'):
            result = installer.save_config(new_config)
        
        assert result == True
        
        # Verify backup created
        backup_file = config_file.with_suffix('.json.backup')
        assert backup_file.exists()
        
        # Verify backup content
        with open(backup_file, 'r') as f:
            backup_config = json.load(f)
        assert backup_config == original_config
    
    def test_save_config_no_path(self):
        """Test save_config when config_path is None"""
        installer = MCPInstaller()
        installer.config_path = None
        
        result = installer.save_config({"test": "config"})
        assert result == False
    
    def test_save_config_io_error(self, temp_config_dir):
        """Test save_config handling IO error"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        
        installer = MCPInstaller()
        installer.config_path = config_file
        
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with patch('rich.console.Console.print') as mock_print:
                result = installer.save_config({"test": "config"})
        
        assert result == False
        # Verify error message printed
        mock_print.assert_called_with("[red]❌ Failed to save config: Permission denied[/red]")
    
    def test_install_no_apps_user_cancels(self, installer):
        """Test install when no apps found and user cancels"""
        with patch.object(installer, 'detect_claude_app', return_value="none"):
            with patch('rich.prompt.Confirm.ask', return_value=False):
                with patch('rich.console.Console.print'):
                    result = installer.install()
        
        assert result == False
    
    def test_install_no_apps_user_continues(self, installer, temp_config_dir):
        """Test install when no apps found but user continues"""
        installer.config_path = temp_config_dir / "claude_desktop_config.json"
        
        with patch.object(installer, 'detect_claude_app', return_value="none"):
            with patch('rich.prompt.Confirm.ask', return_value=True):
                with patch('rich.console.Console.print'):
                    result = installer.install()
        
        assert result == True
        assert installer.config_path.exists()
        
        # Verify MCP server configured
        with open(installer.config_path, 'r') as f:
            config = json.load(f)
        assert "claude-code-indexer" in config["mcpServers"]
    
    def test_install_claude_code_found(self, installer, temp_config_dir):
        """Test install when Claude Code is found"""
        installer.config_path = temp_config_dir / "claude_desktop_config.json"
        
        with patch.object(installer, 'detect_claude_app', return_value="code"):
            with patch('rich.console.Console.print'):
                result = installer.install()
        
        assert result == True
        
        # Verify correct app name in output
        with open(installer.config_path, 'r') as f:
            config = json.load(f)
        assert "claude-code-indexer" in config["mcpServers"]
    
    def test_install_already_configured_user_updates(self, installer, temp_config_dir):
        """Test install when already configured and user updates"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        existing_config = {
            "mcpServers": {
                "claude-code-indexer": {
                    "command": "old-command",
                    "args": []
                }
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(existing_config, f)
        
        installer.config_path = config_file
        
        with patch.object(installer, 'detect_claude_app', return_value="desktop"):
            with patch('rich.prompt.Confirm.ask', return_value=True):
                with patch('rich.console.Console.print'):
                    result = installer.install()
        
        assert result == True
        
        # Verify config updated
        with open(config_file, 'r') as f:
            config = json.load(f)
        assert config["mcpServers"]["claude-code-indexer"]["command"] == "cci-mcp-server"
    
    def test_install_already_configured_user_cancels(self, installer, temp_config_dir):
        """Test install when already configured and user cancels"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        existing_config = {"mcpServers": {"claude-code-indexer": {"command": "existing"}}}
        
        with open(config_file, 'w') as f:
            json.dump(existing_config, f)
        
        installer.config_path = config_file
        
        with patch.object(installer, 'detect_claude_app', return_value="desktop"):
            with patch('rich.prompt.Confirm.ask', return_value=False):
                with patch('rich.console.Console.print'):
                    result = installer.install()
        
        assert result == False
    
    def test_install_force_flag(self, installer, temp_config_dir):
        """Test install with force flag bypasses prompts"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        existing_config = {"mcpServers": {"claude-code-indexer": {"command": "old"}}}
        
        with open(config_file, 'w') as f:
            json.dump(existing_config, f)
        
        installer.config_path = config_file
        
        with patch.object(installer, 'detect_claude_app', return_value="desktop"):
            with patch('rich.console.Console.print'):
                # No prompts should be shown with force=True
                result = installer.install(force=True)
        
        assert result == True
    
    def test_install_mcp_server_config_structure(self, installer, temp_config_dir):
        """Test the structure of MCP server configuration"""
        installer.config_path = temp_config_dir / "claude_desktop_config.json"
        
        with patch.object(installer, 'detect_claude_app', return_value="desktop"):
            with patch('rich.console.Console.print'):
                installer.install()
        
        with open(installer.config_path, 'r') as f:
            config = json.load(f)
        
        mcp_config = config["mcpServers"]["claude-code-indexer"]
        assert mcp_config["command"] == "cci-mcp-server"
        assert mcp_config["args"] == []
        assert mcp_config["env"] == {}
        assert mcp_config["autoStart"] == True
        assert mcp_config["capabilities"]["tools"] == True
        assert mcp_config["capabilities"]["resources"] == True
    
    def test_uninstall_no_config(self, installer):
        """Test uninstall when no config exists"""
        installer.config_path = Path("/nonexistent/config.json")
        
        with patch('rich.console.Console.print'):
            result = installer.uninstall()
        
        assert result == True
    
    def test_uninstall_not_configured(self, installer, temp_config_dir):
        """Test uninstall when MCP server not configured"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        config = {"mcpServers": {"other-server": {"command": "other"}}}
        
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        installer.config_path = config_file
        
        with patch.object(installer, 'detect_claude_app', return_value="desktop"):
            with patch('rich.console.Console.print'):
                result = installer.uninstall()
        
        assert result == True
    
    def test_uninstall_success(self, installer, temp_config_dir):
        """Test successful uninstall"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        config = {
            "mcpServers": {
                "claude-code-indexer": {"command": "cci-mcp-server"},
                "other-server": {"command": "other"}
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        installer.config_path = config_file
        
        with patch.object(installer, 'detect_claude_app', return_value="desktop"):
            with patch('rich.console.Console.print'):
                result = installer.uninstall()
        
        assert result == True
        
        # Verify server removed but others remain
        with open(config_file, 'r') as f:
            updated_config = json.load(f)
        assert "claude-code-indexer" not in updated_config["mcpServers"]
        assert "other-server" in updated_config["mcpServers"]
    
    def test_status_all_components(self, installer, temp_config_dir):
        """Test status method with all components"""
        config_file = temp_config_dir / "claude_desktop_config.json"
        config = {"mcpServers": {"claude-code-indexer": {"command": "cci-mcp-server"}}}
        
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        installer.config_path = config_file
        
        with patch.object(installer, 'check_claude_desktop', return_value=True):
            with patch.object(installer, 'check_claude_code', return_value=True):
                with patch('rich.console.Console.print') as mock_print:
                    installer.status()
        
        # Verify console print called (status shown)
        assert mock_print.called
    
    def test_status_unsupported_platform(self):
        """Test status on unsupported platform"""
        with patch('platform.system', return_value="UnknownOS"):
            installer = MCPInstaller()
            
            with patch('rich.console.Console.print') as mock_print:
                installer.status()
            
            # Should show unsupported platform message
            assert mock_print.called
    
    def test_concurrent_config_access(self, installer, temp_config_dir):
        """Test concurrent access to config file"""
        import threading
        
        config_file = temp_config_dir / "claude_desktop_config.json"
        installer.config_path = config_file
        
        results = []
        
        def save_config_thread(thread_id):
            config = {"mcpServers": {f"server_{thread_id}": {"command": f"cmd_{thread_id}"}}}
            with patch('rich.console.Console.print'):
                result = installer.save_config(config)
            results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=save_config_thread, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # All saves should succeed
        assert all(results)
        assert config_file.exists()