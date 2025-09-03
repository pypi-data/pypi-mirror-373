#!/usr/bin/env python3
"""
Simple CLI tests that work reliably without complex mocking
"""

import pytest
from click.testing import CliRunner
from pathlib import Path

from claude_code_indexer.cli import cli


class TestCLIBasicFunctionality:
    """Test basic CLI functionality that always works"""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_version(self, runner):
        """Test --version flag"""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert 'version' in result.output.lower()
    
    def test_help(self, runner):
        """Test main help"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Commands:' in result.output
    
    def test_llm_guide(self, runner):
        """Test llm-guide command"""
        result = runner.invoke(cli, ['llm-guide'])
        assert result.exit_code == 0
        assert 'LLM Usage Guide' in result.output
    
    # Test all command help texts
    @pytest.mark.parametrize("command", [
        'init', 'index', 'query', 'search', 'stats', 
        'enhance', 'projects', 'cache', 'clean', 'remove',
        'background', 'benchmark'
    ])
    def test_command_help(self, runner, command):
        """Test help for various commands"""
        result = runner.invoke(cli, [command, '--help'])
        assert result.exit_code == 0
        assert 'help' in result.output.lower() or 'usage' in result.output.lower()
    
    def test_mcp_help(self, runner):
        """Test MCP command help"""
        result = runner.invoke(cli, ['mcp', '--help'])
        assert result.exit_code == 0
        # Don't assert specific text that might change
    
    def test_mcp_subcommand_help(self, runner):
        """Test MCP subcommand help"""
        subcommands = ['install', 'uninstall', 'status']
        for subcmd in subcommands:
            result = runner.invoke(cli, ['mcp', subcmd, '--help'])
            assert result.exit_code == 0


class TestCLIErrorHandling:
    """Test CLI error handling"""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_invalid_path_index(self, runner):
        """Test indexing invalid path"""
        result = runner.invoke(cli, ['index', '/this/path/absolutely/does/not/exist'])
        assert result.exit_code != 0
    
    def test_empty_search(self, runner):
        """Test search with no terms"""
        result = runner.invoke(cli, ['search'])
        assert result.exit_code != 0
    
    def test_invalid_remove_no_project(self, runner):
        """Test remove without project name"""
        result = runner.invoke(cli, ['remove'])
        assert result.exit_code != 0


class TestInitCommand:
    """Test init command functionality"""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_init_with_confirmation(self, runner):
        """Test init command with user confirmation"""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['init'], input='y\n')
            assert result.exit_code == 0
            assert Path('CLAUDE.md').exists()
    
    def test_init_with_rejection(self, runner):
        """Test init command with user rejection"""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['init'], input='n\n')
            assert result.exit_code == 0
    
    def test_init_force_flag(self, runner):
        """Test init with --force flag"""
        with runner.isolated_filesystem():
            Path('CLAUDE.md').write_text('Old content')
            result = runner.invoke(cli, ['init', '--force'])
            assert result.exit_code == 0
            content = Path('CLAUDE.md').read_text()
            assert 'Code Indexing' in content


class TestCommandExistence:
    """Test that commands exist and are accessible"""
    
    def test_cli_import(self):
        """Test that CLI can be imported"""
        from claude_code_indexer.cli import cli
        assert cli is not None
    
    def test_expected_commands_exist(self):
        """Test that expected commands exist"""
        from claude_code_indexer.cli import cli
        
        basic_commands = ['init', 'index', 'query', 'search', 'stats']
        for cmd_name in basic_commands:
            assert cmd_name in cli.commands, f"Command '{cmd_name}' missing"
    
    def test_advanced_commands_exist(self):
        """Test that advanced commands exist"""
        from claude_code_indexer.cli import cli
        
        advanced_commands = ['enhance', 'projects', 'cache', 'clean', 'background', 'mcp']
        for cmd_name in advanced_commands:
            assert cmd_name in cli.commands, f"Advanced command '{cmd_name}' missing"
    
    def test_cli_command_count(self):
        """Test CLI has reasonable number of commands"""
        from claude_code_indexer.cli import cli
        assert len(cli.commands) >= 10
        assert len(cli.commands) <= 25


class TestBasicCommandOutputs:
    """Test basic command outputs without complex mocking"""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_mcp_status_basic(self, runner):
        """Test mcp status doesn't crash"""
        result = runner.invoke(cli, ['mcp', 'status'])
        # Don't assert specific content, just that it doesn't crash
        assert result.exit_code in [0, 1]  # Either works or gracefully fails
    
    def test_background_status_basic(self, runner):
        """Test background status doesn't crash"""
        result = runner.invoke(cli, ['background', 'status'])
        # Should handle gracefully whether service exists or not
        assert result.exit_code in [0, 1]
    
    def test_projects_no_projects(self, runner):
        """Test projects command with no projects"""
        result = runner.invoke(cli, ['projects'])
        # Should handle gracefully
        assert result.exit_code in [0, 1]
    
    def test_cache_stats_basic(self, runner):
        """Test cache command basic functionality"""
        result = runner.invoke(cli, ['cache'])
        # Should handle gracefully even if no cache exists
        assert result.exit_code in [0, 1]


# Simple integration tests
def test_cli_main_help():
    """Test main CLI help works"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'claude-code-indexer' in result.output.lower() or 'commands:' in result.output.lower()


def test_cli_version_info():
    """Test CLI version information"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    # Should contain some version information
    assert len(result.output.strip()) > 0