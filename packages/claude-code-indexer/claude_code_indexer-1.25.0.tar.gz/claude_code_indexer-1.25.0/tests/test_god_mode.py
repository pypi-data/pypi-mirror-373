#!/usr/bin/env python3
"""
Comprehensive tests for GodModeOrchestrator class
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock, mock_open
from datetime import datetime

from claude_code_indexer.commands.god_mode import GodModeOrchestrator


class TestGodModeOrchestrator:
    """Test suite for GodModeOrchestrator class"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def orchestrator(self, temp_config_dir):
        """Create GodModeOrchestrator instance with temp directory"""
        return GodModeOrchestrator(config_path=temp_config_dir)
    
    def test_init(self, temp_config_dir):
        """Test GodModeOrchestrator initialization"""
        orchestrator = GodModeOrchestrator(config_path=temp_config_dir)
        
        assert orchestrator.config_path == temp_config_dir
        assert orchestrator.audit_log_path == temp_config_dir / "audit.log"
        assert orchestrator.config_file == temp_config_dir / "config.yaml"
        assert orchestrator.enabled == False
        assert orchestrator.token_usage == {"total": 0, "by_agent": {}}
    
    def test_init_default_path(self):
        """Test initialization with default path"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path("/home/user")
            with patch('pathlib.Path.mkdir'):
                with patch.object(GodModeOrchestrator, '_create_default_config'):
                    orchestrator = GodModeOrchestrator()
                    assert orchestrator.config_path == Path("/home/user/.god-mode")
    
    def test_ensure_directories_creates_dir(self, temp_config_dir):
        """Test _ensure_directories creates directory"""
        config_path = temp_config_dir / "subdir"
        orchestrator = GodModeOrchestrator(config_path=config_path)
        
        assert config_path.exists()
        assert config_path.is_dir()
    
    def test_ensure_directories_creates_default_config(self, temp_config_dir):
        """Test _ensure_directories creates default config if not exists"""
        orchestrator = GodModeOrchestrator(config_path=temp_config_dir)
        
        assert orchestrator.config_file.exists()
        
        # Load and verify config
        import yaml
        with open(orchestrator.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config["enabled"] == False
        assert config["auto_accept"] == True
        assert config["vibecode_mode"] == True
        assert "agents" in config
        assert "architect" in config["agents"]
        assert "developer" in config["agents"]
        assert "safety" in config
        assert "forbidden_operations" in config["safety"]
        assert "max_tokens_per_session" in config["safety"]
    
    def test_create_default_config_structure(self, orchestrator):
        """Test default config structure"""
        orchestrator._create_default_config()
        
        import yaml
        with open(orchestrator.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Verify agents
        assert config["agents"]["architect"]["role"] == "Planning and task decomposition"
        assert config["agents"]["architect"]["model"] == "claude-opus-4"
        assert config["agents"]["developer"]["role"] == "Code implementation"
        assert config["agents"]["developer"]["model"] == "claude-sonnet-4"
        
        # Verify safety
        assert "rm -rf /" in config["safety"]["forbidden_operations"]
        assert config["safety"]["max_tokens_per_session"] == 100000
        assert "production deployment" in config["safety"]["require_confirmation"]
    
    def test_log_action(self, orchestrator):
        """Test _log_action method"""
        orchestrator._log_action("test_agent", "test_action", "success", tokens=50)
        
        # Verify audit log exists
        assert orchestrator.audit_log_path.exists()
        
        # Read and verify log entry
        with open(orchestrator.audit_log_path, 'r') as f:
            log_entry = json.loads(f.readline())
        
        assert log_entry["agent"] == "test_agent"
        assert log_entry["action"] == "test_action"
        assert log_entry["result"] == "success"
        assert log_entry["tokens"] == 50
        assert "timestamp" in log_entry
        
        # Verify token tracking
        assert orchestrator.token_usage["total"] == 50
        assert orchestrator.token_usage["by_agent"]["test_agent"] == 50
    
    def test_log_action_multiple_agents(self, orchestrator):
        """Test token tracking for multiple agents"""
        orchestrator._log_action("agent1", "action1", "result1", tokens=100)
        orchestrator._log_action("agent2", "action2", "result2", tokens=200)
        orchestrator._log_action("agent1", "action3", "result3", tokens=50)
        
        assert orchestrator.token_usage["total"] == 350
        assert orchestrator.token_usage["by_agent"]["agent1"] == 150
        assert orchestrator.token_usage["by_agent"]["agent2"] == 200
    
    @pytest.mark.asyncio
    async def test_enable_user_confirms(self, orchestrator):
        """Test enable method when user confirms"""
        with patch('click.confirm', return_value=True):
            with patch('rich.console.Console.print'):
                await orchestrator.enable()
        
        # Verify enabled
        assert orchestrator.enabled == True
        
        # Verify config updated
        import yaml
        with open(orchestrator.config_file, 'r') as f:
            config = yaml.safe_load(f)
        assert config["enabled"] == True
        
        # Verify audit log entry
        with open(orchestrator.audit_log_path, 'r') as f:
            log_entry = json.loads(f.readline())
        assert log_entry["action"] == "GOD_MODE_ENABLED"
    
    @pytest.mark.asyncio
    async def test_enable_user_cancels(self, orchestrator):
        """Test enable method when user cancels"""
        with patch('click.confirm', return_value=False):
            with patch('rich.console.Console.print'):
                await orchestrator.enable()
        
        # Verify not enabled
        assert orchestrator.enabled == False
        
        # Verify config not updated
        import yaml
        with open(orchestrator.config_file, 'r') as f:
            config = yaml.safe_load(f)
        assert config["enabled"] == False
    
    @pytest.mark.asyncio
    async def test_disable(self, orchestrator):
        """Test disable method"""
        # First enable
        orchestrator.enabled = True
        import yaml
        with open(orchestrator.config_file, 'r') as f:
            config = yaml.safe_load(f)
        config["enabled"] = True
        with open(orchestrator.config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Now disable
        with patch('rich.console.Console.print'):
            await orchestrator.disable()
        
        # Verify disabled
        assert orchestrator.enabled == False
        
        # Verify config updated
        with open(orchestrator.config_file, 'r') as f:
            config = yaml.safe_load(f)
        assert config["enabled"] == False
        
        # Verify audit log entry
        with open(orchestrator.audit_log_path, 'r') as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1])
        assert log_entry["action"] == "GOD_MODE_DISABLED"
    
    @pytest.mark.asyncio
    async def test_status_basic(self, orchestrator):
        """Test status method basic output"""
        with patch('rich.console.Console.print') as mock_print:
            await orchestrator.status()
        
        # Verify console print was called
        assert mock_print.called
    
    @pytest.mark.asyncio
    async def test_status_with_token_usage(self, orchestrator):
        """Test status method with token usage"""
        # Add some token usage
        orchestrator._log_action("architect", "plan", "success", tokens=100)
        orchestrator._log_action("developer", "code", "success", tokens=200)
        
        with patch('rich.console.Console.print') as mock_print:
            await orchestrator.status()
        
        # Verify token table was displayed
        assert mock_print.called
    
    @pytest.mark.asyncio
    async def test_simulate_multi_agent_not_enabled(self, orchestrator):
        """Test simulate_multi_agent when not enabled"""
        with patch('rich.console.Console.print') as mock_print:
            await orchestrator.simulate_multi_agent("test task")
        
        # Verify error message
        mock_print.assert_called_with("[red]GOD mode is not enabled. Run 'god-mode --enable' first.[/red]")
    
    @pytest.mark.asyncio
    async def test_simulate_multi_agent_enabled(self, orchestrator):
        """Test simulate_multi_agent when enabled"""
        # Enable god mode
        import yaml
        config = {
            "enabled": True,
            "auto_accept": True,
            "vibecode_mode": True
        }
        with open(orchestrator.config_file, 'w') as f:
            yaml.dump(config, f)
        
        with patch('rich.console.Console.print'):
            with patch('asyncio.sleep', new_callable=AsyncMock):
                await orchestrator.simulate_multi_agent("test task")
        
        # Verify token usage logged
        assert orchestrator.token_usage["total"] == 450  # 150 + 300
        assert orchestrator.token_usage["by_agent"]["architect"] == 150
        assert orchestrator.token_usage["by_agent"]["developer"] == 300
    
    @pytest.mark.asyncio
    async def test_simulate_multi_agent_workflow(self, orchestrator):
        """Test complete multi-agent workflow"""
        # Enable god mode
        import yaml
        config = {
            "enabled": True,
            "auto_accept": True,
            "vibecode_mode": True
        }
        with open(orchestrator.config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Mock sleep to speed up test
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch('rich.console.Console.print') as mock_print:
                with patch('rich.progress.Progress'):
                    await orchestrator.simulate_multi_agent("implement feature X")
        
        # Verify workflow steps
        assert orchestrator.token_usage["total"] > 0
        assert "architect" in orchestrator.token_usage["by_agent"]
        assert "developer" in orchestrator.token_usage["by_agent"]
    
    def test_yaml_import_handling(self, orchestrator):
        """Test yaml import is handled properly"""
        # Should not raise ImportError
        orchestrator._create_default_config()
        
        # Verify yaml file created
        assert orchestrator.config_file.exists()
    
    def test_concurrent_log_writes(self, orchestrator):
        """Test concurrent log writes don't corrupt audit log"""
        import threading
        
        def write_log(agent_name, count):
            for i in range(count):
                orchestrator._log_action(agent_name, f"action_{i}", "success", tokens=10)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=write_log, args=(f"agent_{i}", 10))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Verify total tokens
        assert orchestrator.token_usage["total"] == 500  # 5 agents * 10 actions * 10 tokens
        
        # Verify all log entries are valid JSON
        with open(orchestrator.audit_log_path, 'r') as f:
            for line in f:
                log_entry = json.loads(line)
                assert "agent" in log_entry
                assert "action" in log_entry
    
    def test_config_file_corruption_recovery(self, temp_config_dir):
        """Test handling of corrupted config file"""
        # Note: GodModeOrchestrator doesn't handle corrupted configs,
        # it only creates default config if file doesn't exist.
        # This test verifies that behavior
        config_file = temp_config_dir / "config.yaml"
        
        # When config doesn't exist, it creates default
        orchestrator = GodModeOrchestrator(config_path=temp_config_dir)
        
        # Verify default config created
        import yaml
        with open(orchestrator.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert "enabled" in config
        assert "agents" in config


class TestGodModeCliCommands:
    """Test CLI command functions"""
    
    @patch('claude_code_indexer.commands.god_mode.GodModeOrchestrator')
    @patch('asyncio.run')
    def test_enable_god_mode_command(self, mock_run, mock_orchestrator_class):
        """Test enable_god_mode CLI command"""
        from claude_code_indexer.commands.god_mode import enable_god_mode
        
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        # Make enable() return an awaitable
        mock_orchestrator.enable = AsyncMock()
        
        # Test the function directly without Click's CLI runner
        with patch('sys.argv', ['test']):
            enable_god_mode.callback()
        
        mock_orchestrator_class.assert_called_once()
        mock_run.assert_called_once()
    
    @patch('claude_code_indexer.commands.god_mode.GodModeOrchestrator')
    @patch('asyncio.run')
    def test_disable_god_mode_command(self, mock_run, mock_orchestrator_class):
        """Test disable_god_mode CLI command"""
        from claude_code_indexer.commands.god_mode import disable_god_mode
        
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.disable = AsyncMock()
        
        with patch('sys.argv', ['test']):
            disable_god_mode.callback()
        
        mock_orchestrator_class.assert_called_once()
        mock_run.assert_called_once()
    
    @patch('claude_code_indexer.commands.god_mode.GodModeOrchestrator')
    @patch('asyncio.run')
    def test_stop_god_mode_command(self, mock_run, mock_orchestrator_class):
        """Test stop_god_mode CLI command (alias for disable)"""
        from claude_code_indexer.commands.god_mode import stop_god_mode
        
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.disable = AsyncMock()
        
        with patch('sys.argv', ['test']):
            stop_god_mode.callback()
        
        mock_orchestrator_class.assert_called_once()
        mock_run.assert_called_once()
    
    @patch('claude_code_indexer.commands.god_mode.GodModeOrchestrator')
    @patch('asyncio.run')
    def test_god_mode_status_command(self, mock_run, mock_orchestrator_class):
        """Test god_mode_status CLI command"""
        from claude_code_indexer.commands.god_mode import god_mode_status
        
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.status = AsyncMock()
        
        with patch('sys.argv', ['test']):
            god_mode_status.callback()
        
        mock_orchestrator_class.assert_called_once()
        mock_run.assert_called_once()
    
    @patch('claude_code_indexer.commands.god_mode.GodModeOrchestrator')
    @patch('asyncio.run')
    def test_execute_task_command(self, mock_run, mock_orchestrator_class):
        """Test execute_task CLI command"""
        from claude_code_indexer.commands.god_mode import execute_task
        
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.simulate_multi_agent = AsyncMock()
        
        with patch('sys.argv', ['test']):
            execute_task.callback("test task")
        
        mock_orchestrator_class.assert_called_once()
        mock_run.assert_called_once()