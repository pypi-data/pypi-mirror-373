#!/usr/bin/env python3
"""
GitHub Issue Reporter for Claude Code Indexer
Helps LLMs and users report issues directly to GitHub
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any
import platform
try:
    from importlib.metadata import version as get_version
except ImportError:
    # Python < 3.8 fallback
    from importlib_metadata import version as get_version

from .logger import log_info, log_error, log_warning


class GitHubIssueReporter:
    """Helper class for reporting issues to GitHub"""
    
    REPO_OWNER = "tuannx"
    REPO_NAME = "claude-prompts"
    REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
    
    def __init__(self):
        self.gh_available = self._check_gh_cli()
        
    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is available"""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def get_system_info(self) -> Dict[str, str]:
        """Gather system information for bug reports"""
        try:
            version = get_version("claude-code-indexer")
        except:
            version = "unknown"
            
        return {
            "version": version,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
        }
    
    def format_issue_body(
        self, 
        error_type: str,
        error_message: str,
        command: str,
        traceback: Optional[str] = None,
        additional_info: Optional[str] = None
    ) -> str:
        """Format issue body with all relevant information"""
        system_info = self.get_system_info()
        
        body = f"""## 🐛 Bug Report

### Description
Error occurred while running claude-code-indexer

### Error Details
- **Error Type**: `{error_type}`
- **Error Message**: `{error_message}`
- **Command**: `{command}`

### System Information
- **claude-code-indexer version**: {system_info['version']}
- **Python version**: {system_info['python']}
- **Platform**: {system_info['platform']}
- **System**: {system_info['system']}
- **Machine**: {system_info['machine']}

### Steps to Reproduce
1. Run command: `{command}`
2. Error occurs with message: `{error_message}`

"""
        
        if traceback:
            body += f"""### Full Traceback
```python
{traceback}
```

"""
        
        if additional_info:
            body += f"""### Additional Information
{additional_info}

"""
        
        body += """### Expected Behavior
The command should complete successfully without errors.

### Possible Solution
<!-- If you have suggestions on how to fix this issue -->

---
*This issue was automatically generated. Please add any additional context that might help.*
"""
        
        return body
    
    def create_issue_url(
        self,
        title: str,
        body: str,
        labels: Optional[list] = None
    ) -> str:
        """Create GitHub issue URL for manual reporting"""
        import urllib.parse
        
        params = {
            "title": title,
            "body": body,
        }
        
        if labels:
            params["labels"] = ",".join(labels)
            
        query_string = urllib.parse.urlencode(params)
        return f"{self.REPO_URL}/issues/new?{query_string}"
    
    def report_issue(
        self,
        error_type: str,
        error_message: str,
        command: str,
        traceback: Optional[str] = None,
        additional_info: Optional[str] = None,
        auto_create: bool = False
    ) -> bool:
        """Report an issue to GitHub"""
        
        title = f"[Bug] {error_type}: {error_message[:50]}..."
        body = self.format_issue_body(
            error_type, error_message, command, traceback, additional_info
        )
        labels = ["bug", "auto-reported"]
        
        if self.gh_available and auto_create:
            # Try to create issue using GitHub CLI
            try:
                result = subprocess.run(
                    [
                        "gh", "issue", "create",
                        "--repo", f"{self.REPO_OWNER}/{self.REPO_NAME}",
                        "--title", title,
                        "--body", body,
                        "--label", ",".join(labels)
                    ],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                if result.returncode == 0:
                    issue_url = result.stdout.strip()
                    log_info(f"✅ Issue created: {issue_url}")
                    return True
                else:
                    log_error(f"Failed to create issue: {result.stderr}")
                    
            except subprocess.CalledProcessError as e:
                log_error(f"GitHub CLI error: {e}")
                
        # Fallback: provide URL for manual reporting
        issue_url = self.create_issue_url(title, body, labels)
        
        print("\n" + "="*60)
        print("🐛 ERROR DETECTED - Please Report This Issue")
        print("="*60)
        print(f"\n📋 Error Summary:")
        print(f"  Type: {error_type}")
        print(f"  Message: {error_message}")
        print(f"  Command: {command}")
        
        if self.gh_available:
            print(f"\n🔧 To report with GitHub CLI:")
            print(f"  gh issue create --repo {self.REPO_OWNER}/{self.REPO_NAME} \\")
            print(f'    --title "{title}" \\')
            print(f'    --body "{body[:100]}..." \\')
            print(f'    --label "{",".join(labels)}"')
        
        print(f"\n🌐 Or report manually:")
        print(f"  {issue_url[:100]}...")
        print(f"\n💡 For LLMs: Use the GitHub CLI command above to auto-report")
        print("="*60 + "\n")
        
        return False


def suggest_github_issue(
    error_type: str,
    error_message: str, 
    command: str,
    traceback: Optional[str] = None
):
    """Convenience function to suggest reporting an issue"""
    reporter = GitHubIssueReporter()
    
    # Format command for display
    if command.startswith("claude-code-indexer"):
        display_command = command
    else:
        display_command = f"claude-code-indexer {command}"
    
    reporter.report_issue(
        error_type=error_type,
        error_message=error_message,
        command=display_command,
        traceback=traceback,
        auto_create=False
    )