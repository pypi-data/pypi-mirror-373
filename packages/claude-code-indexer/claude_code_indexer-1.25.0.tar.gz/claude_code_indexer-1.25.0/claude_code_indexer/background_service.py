#!/usr/bin/env python3
"""
Background indexing service for automatic periodic updates
"""

import os
import sys
import time
import json
import signal
import threading
import subprocess
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .storage_manager import get_storage_manager
from .indexer import CodeGraphIndexer
from .logger import log_info, log_warning, log_error


class BackgroundIndexingService:
    """Service for automatic background indexing of projects"""
    
    def __init__(self):
        self.storage_manager = get_storage_manager()
        self.service_config_path = self.storage_manager.app_home / "background_service.json"
        self.pid_file = self.storage_manager.app_home / "background_service.pid"
        self.log_file = self.storage_manager.app_home / "background_service.log"
        self.config = self._load_config()
        self.running = False
        self.threads = {}
        self.project_start_offsets = {}  # Store random offsets for projects
        
        # Rate limiting configuration
        self.max_concurrent_indexing = 2  # Max concurrent indexing operations
        self.max_cpu_percent = 50  # Max CPU usage percentage
        self.max_memory_mb = 500  # Max memory usage in MB
        self.indexing_semaphore = threading.Semaphore(self.max_concurrent_indexing)
        
    def _load_config(self) -> Dict:
        """Load service configuration"""
        default_config = {
            "enabled": True,
            "default_interval": 300,  # 5 minutes
            "projects": {}  # project_path: {"interval": seconds, "last_indexed": timestamp}
        }
        
        if self.service_config_path.exists():
            try:
                with open(self.service_config_path, 'r') as f:
                    config = json.load(f)
                    # Ensure all required keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                log_error(f"Error loading background service config: {e}")
        
        return default_config
    
    def _save_config(self):
        """Save service configuration"""
        try:
            with open(self.service_config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            log_error(f"Error saving background service config: {e}")
    
    def set_project_interval(self, project_path: str, interval: int):
        """Set indexing interval for a specific project
        
        Args:
            project_path: Path to the project
            interval: Interval in seconds (-1 to disable)
        """
        project_path = str(Path(project_path).resolve())
        
        if interval == -1:
            # Remove project from background indexing
            if project_path in self.config["projects"]:
                del self.config["projects"][project_path]
                log_info(f"Disabled background indexing for {project_path}")
        else:
            # Add or update project
            if project_path not in self.config["projects"]:
                self.config["projects"][project_path] = {}
            
            self.config["projects"][project_path]["interval"] = interval
            self.config["projects"][project_path]["last_indexed"] = 0  # Force immediate index
            log_info(f"Set background indexing interval to {interval}s for {project_path}")
        
        self._save_config()
        
        # Restart service if running
        if self.is_running():
            self.restart()
    
    def set_default_interval(self, interval: int):
        """Set default interval for all projects"""
        self.config["default_interval"] = interval
        self._save_config()
        log_info(f"Set default background indexing interval to {interval}s")
        
        # Restart service if running
        if self.is_running():
            self.restart()
    
    def enable(self):
        """Enable background indexing service"""
        self.config["enabled"] = True
        self._save_config()
        log_info("Background indexing service enabled")
    
    def disable(self):
        """Disable background indexing service"""
        self.config["enabled"] = False
        self._save_config()
        self.stop()
        log_info("Background indexing service disabled")
    
    def is_running(self) -> bool:
        """Check if service is running"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            if PSUTIL_AVAILABLE:
                return psutil.pid_exists(pid)
            else:
                # Fallback: try to send signal 0
                try:
                    os.kill(pid, 0)
                    return True
                except OSError:
                    return False
        except:
            return False
    
    def start(self):
        """Start the background indexing service"""
        if not self.config["enabled"]:
            log_warning("Background indexing service is disabled")
            return
        
        if self.is_running():
            log_warning("Background indexing service is already running")
            return
        
        # Fork a daemon process
        pid = os.fork()
        if pid > 0:
            # Parent process
            log_info(f"Background indexing service started (PID: {pid})")
            return
        
        # Child process - become a daemon
        os.setsid()
        os.umask(0)
        
        # Redirect stdout/stderr to log file
        sys.stdout = open(self.log_file, 'a')
        sys.stderr = sys.stdout
        
        # Write PID file
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Start the service
        self.running = True
        self._run_service()
    
    def stop(self):
        """Stop the background indexing service"""
        if not self.is_running():
            log_info("Background indexing service is not running")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to stop
            for _ in range(10):
                if PSUTIL_AVAILABLE:
                    if not psutil.pid_exists(pid):
                        break
                else:
                    try:
                        os.kill(pid, 0)
                    except OSError:
                        break
                time.sleep(0.5)
            
            # Clean up PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            log_info("Background indexing service stopped")
        except Exception as e:
            log_error(f"Error stopping background service: {e}")
    
    def restart(self):
        """Restart the background indexing service"""
        self.stop()
        time.sleep(1)
        self.start()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        log_info(f"Received signal {signum}, shutting down...")
        self.running = False
        
        # Stop all indexing threads
        for thread in self.threads.values():
            if thread.is_alive():
                thread.join(timeout=5)
        
        # Clean up PID file
        if self.pid_file.exists():
            self.pid_file.unlink()
        
        sys.exit(0)
    
    def _run_service(self):
        """Main service loop"""
        log_info("Background indexing service started")
        
        while self.running:
            try:
                # Get all projects that need indexing
                projects_to_index = self._get_projects_to_index()
                
                for project_path in projects_to_index:
                    if not self.running:
                        break
                    
                    # Check system resources before indexing
                    if not self._check_system_resources():
                        log_info("System resources insufficient, waiting...")
                        time.sleep(30)  # Wait 30 seconds before checking again
                        continue
                    
                    # Skip if already being indexed
                    if project_path in self.threads and self.threads[project_path].is_alive():
                        continue
                    
                    # Start indexing in a separate thread
                    thread = threading.Thread(
                        target=self._index_project,
                        args=(project_path,),
                        daemon=True
                    )
                    thread.start()
                    self.threads[project_path] = thread
                
                # Clean up finished threads
                self.threads = {
                    path: thread 
                    for path, thread in self.threads.items() 
                    if thread.is_alive()
                }
                
                # Sleep for a bit
                time.sleep(10)
                
            except Exception as e:
                log_error(f"Error in background service loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _get_projects_to_index(self) -> List[str]:
        """Get list of projects that need indexing"""
        projects_to_index = []
        current_time = time.time()
        
        # Get all managed projects first
        all_projects = self.storage_manager.list_projects()
        managed_project_paths = {p["path"] for p in all_projects if Path(p["path"]).exists()}
        
        # Check configured projects (only if they're managed)
        for project_path, config in self.config["projects"].items():
            if project_path not in managed_project_paths:
                continue
            
            interval = config.get("interval", self.config["default_interval"])
            if interval == -1:
                continue
            
            # Generate random offset for this project if not exists
            if project_path not in self.project_start_offsets:
                # Random offset between 0 and interval/2
                self.project_start_offsets[project_path] = random.uniform(0, interval / 2)
            
            last_indexed = config.get("last_indexed", 0)
            offset = self.project_start_offsets[project_path]
            
            # Apply random offset to avoid all projects starting at once
            if current_time - last_indexed + offset >= interval:
                projects_to_index.append(project_path)
        
        # Check all other managed projects using default interval
        for project_info in all_projects:
            project_path = project_info["path"]
            
            # Skip if already configured or doesn't exist
            if project_path in self.config["projects"] or not Path(project_path).exists():
                continue
            
            # Use default interval
            interval = self.config["default_interval"]
            if interval == -1:
                continue
            
            # Generate random offset for this project if not exists
            if project_path not in self.project_start_offsets:
                # Random offset between 0 and interval/2
                self.project_start_offsets[project_path] = random.uniform(0, interval / 2)
            
            # Check last indexed time from project info
            last_indexed = project_info.get("last_indexed_timestamp", 0)
            offset = self.project_start_offsets[project_path]
            
            if current_time - last_indexed + offset >= interval:
                projects_to_index.append(project_path)
        
        return projects_to_index
    
    def _check_system_resources(self) -> bool:
        """Check if system resources allow for indexing"""
        if not PSUTIL_AVAILABLE:
            return True  # If psutil not available, allow indexing
        
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.max_cpu_percent:
                log_warning(f"CPU usage too high: {cpu_percent}% > {self.max_cpu_percent}%")
                return False
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_used_mb = (memory.used / 1024 / 1024)
            memory_available_mb = (memory.available / 1024 / 1024)
            
            if memory_available_mb < self.max_memory_mb:
                log_warning(f"Available memory too low: {memory_available_mb:.1f}MB < {self.max_memory_mb}MB")
                return False
            
            return True
            
        except Exception as e:
            log_warning(f"Error checking system resources: {e}")
            return True  # Allow indexing if we can't check resources
    
    def _index_project(self, project_path: str):
        """Index a single project with rate limiting"""
        # Acquire semaphore for rate limiting
        if not self.indexing_semaphore.acquire(blocking=False):
            log_warning(f"Rate limit reached, skipping {project_path}")
            return
        
        try:
            log_info(f"Starting background index of {project_path}")
            start_time = time.time()
            
            # Create indexer
            indexer = CodeGraphIndexer(project_path=Path(project_path))
            
            # Get supported patterns
            extensions = indexer.parser.get_supported_extensions()
            patterns = [f"*{ext}" for ext in extensions]
            
            # Run indexing
            indexer.index_directory(project_path, patterns=patterns)
            
            # Update last indexed time
            if project_path not in self.config["projects"]:
                self.config["projects"][project_path] = {}
            
            self.config["projects"][project_path]["last_indexed"] = time.time()
            self._save_config()
            
            elapsed = time.time() - start_time
            log_info(f"Background index of {project_path} completed in {elapsed:.1f}s")
            
        except Exception as e:
            log_error(f"Error indexing {project_path}: {e}")
        finally:
            # Always release semaphore
            self.indexing_semaphore.release()
    
    def get_status(self) -> Dict:
        """Get service status and statistics"""
        status = {
            "enabled": self.config["enabled"],
            "running": self.is_running(),
            "default_interval": self.config["default_interval"],
            "projects": {}
        }
        
        # Get all managed projects
        all_projects = self.storage_manager.list_projects()
        managed_projects = {p["path"]: p for p in all_projects if Path(p["path"]).exists()}
        
        # Get project-specific status (only for managed projects)
        for project_path, config in self.config["projects"].items():
            if project_path not in managed_projects:
                continue
                
            interval = config.get("interval", self.config["default_interval"])
            last_indexed = config.get("last_indexed", 0)
            
            status["projects"][project_path] = {
                "interval": interval,
                "last_indexed": datetime.fromtimestamp(last_indexed).isoformat() if last_indexed > 0 else "Never",
                "next_index": datetime.fromtimestamp(last_indexed + interval).isoformat() if last_indexed > 0 and interval > 0 else "N/A",
                "indexing": project_path in self.threads and self.threads[project_path].is_alive(),
                "managed": True
            }
        
        # Add other managed projects not in config
        for project_path, project_info in managed_projects.items():
            if project_path not in status["projects"]:
                interval = self.config["default_interval"]
                last_indexed = project_info.get("last_indexed_timestamp", 0)
                
                status["projects"][project_path] = {
                    "interval": interval,
                    "last_indexed": datetime.fromtimestamp(last_indexed).isoformat() if last_indexed > 0 else "Never",
                    "next_index": datetime.fromtimestamp(last_indexed + interval).isoformat() if last_indexed > 0 and interval > 0 else "N/A",
                    "indexing": project_path in self.threads and self.threads[project_path].is_alive(),
                    "managed": True
                }
        
        return status


def get_background_service() -> BackgroundIndexingService:
    """Get the background indexing service instance"""
    return BackgroundIndexingService()