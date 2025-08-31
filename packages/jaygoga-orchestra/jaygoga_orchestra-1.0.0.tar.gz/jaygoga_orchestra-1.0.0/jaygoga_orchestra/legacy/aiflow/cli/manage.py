"""
Management commands for AIFlow CLI.

Provides commands for project management, monitoring, and maintenance.
"""

import json
import asyncio
import psutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .base import BaseCLICommand, CLIContext


class ManageCommand(BaseCLICommand):
    """Command for managing AIFlow projects."""
    
    def __init__(self):
        super().__init__(
            name="manage",
            description="Manage AIFlow projects, monitoring, and maintenance"
        )
    
    def add_arguments(self, parser) -> None:
        """Add manage command arguments."""
        subparsers = parser.add_subparsers(
            dest="action",
            help="Management actions",
            metavar="<action>"
        )
        
        # Status command
        status_parser = subparsers.add_parser(
            "status",
            help="Show project and system status"
        )
        status_parser.add_argument(
            "--detailed",
            action="store_true",
            help="Show detailed status information"
        )
        
        # Logs command
        logs_parser = subparsers.add_parser(
            "logs",
            help="View application logs"
        )
        logs_parser.add_argument(
            "--lines", "-n",
            type=int,
            default=100,
            help="Number of log lines to show (default: 100)"
        )
        logs_parser.add_argument(
            "--follow", "-f",
            action="store_true",
            help="Follow log output"
        )
        logs_parser.add_argument(
            "--level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            help="Filter by log level"
        )
        
        # Clean command
        clean_parser = subparsers.add_parser(
            "clean",
            help="Clean project artifacts and cache"
        )
        clean_parser.add_argument(
            "--all",
            action="store_true",
            help="Clean all artifacts including logs and data"
        )
        clean_parser.add_argument(
            "--cache-only",
            action="store_true",
            help="Clean only cache files"
        )
        
        # Config command
        config_parser = subparsers.add_parser(
            "config",
            help="Manage project configuration"
        )
        config_parser.add_argument(
            "config_action",
            choices=["show", "set", "get", "validate"],
            help="Configuration action"
        )
        config_parser.add_argument(
            "key",
            nargs="?",
            help="Configuration key"
        )
        config_parser.add_argument(
            "value",
            nargs="?",
            help="Configuration value (for set action)"
        )
        
        # Monitor command
        monitor_parser = subparsers.add_parser(
            "monitor",
            help="Monitor system resources and performance"
        )
        monitor_parser.add_argument(
            "--interval", "-i",
            type=int,
            default=5,
            help="Monitoring interval in seconds (default: 5)"
        )
        monitor_parser.add_argument(
            "--duration", "-d",
            type=int,
            help="Monitoring duration in seconds"
        )
    
    async def execute(self, context: CLIContext, args) -> int:
        """Execute the manage command."""
        try:
            if not args.action:
                self.print_error("No action specified. Use --help for available actions.", context)
                return 1
            
            if args.action == "status":
                return await self._show_status(args, context)
            elif args.action == "logs":
                return await self._show_logs(args, context)
            elif args.action == "clean":
                return await self._clean_project(args, context)
            elif args.action == "config":
                return await self._manage_config(args, context)
            elif args.action == "monitor":
                return await self._monitor_system(args, context)
            else:
                self.print_error(f"Unknown action: {args.action}", context)
                return 1
                
        except Exception as e:
            self.print_error(f"Management command failed: {e}", context)
            return 1
    
    async def _show_status(self, args, context: CLIContext) -> int:
        """Show project and system status."""
        try:
            status_info = {
                "project": await self._get_project_status(context),
                "system": await self._get_system_status(),
                "timestamp": datetime.now().isoformat()
            }
            
            if args.detailed:
                status_info["detailed"] = await self._get_detailed_status(context)
            
            if context.output_format == "json":
                print(json.dumps(status_info, indent=2))
            else:
                self._print_status_table(status_info, context)
            
            return 0
            
        except Exception as e:
            self.print_error(f"Error getting status: {e}", context)
            return 1
    
    async def _get_project_status(self, context: CLIContext) -> Dict[str, Any]:
        """Get project status information."""
        project_config_path = context.project_root / "aiflow.json"
        
        if not project_config_path.exists():
            return {"status": "No AIFlow project found"}
        
        with open(project_config_path, 'r') as f:
            config = json.load(f)
        
        # Check for common project files
        files_status = {
            "main.py": (context.project_root / "main.py").exists(),
            "requirements.txt": (context.project_root / "requirements.txt").exists(),
            "agents/": (context.project_root / "agents").exists(),
            "tasks/": (context.project_root / "tasks").exists(),
        }
        
        return {
            "name": config.get("name", "Unknown"),
            "version": config.get("version", "Unknown"),
            "status": "Active",
            "files": files_status,
            "agents_count": len(config.get("agents", {})),
            "tasks_count": len(config.get("tasks", {}))
        }
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get system status information."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}"
            }
        except Exception:
            return {"status": "Unable to get system information"}
    
    async def _get_detailed_status(self, context: CLIContext) -> Dict[str, Any]:
        """Get detailed status information."""
        detailed = {}
        
        # Check logs
        logs_dir = context.project_root / "logs"
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            detailed["logs"] = {
                "count": len(log_files),
                "latest": max(log_files, key=lambda x: x.stat().st_mtime).name if log_files else None
            }
        
        # Check data directory
        data_dir = context.project_root / "data"
        if data_dir.exists():
            data_files = list(data_dir.rglob("*"))
            detailed["data"] = {
                "files_count": len([f for f in data_files if f.is_file()]),
                "total_size": sum(f.stat().st_size for f in data_files if f.is_file())
            }
        
        return detailed
    
    def _print_status_table(self, status_info: Dict[str, Any], context: CLIContext):
        """Print status information in table format."""
        print("="*60)
        print("AIFLOW PROJECT STATUS")
        print("="*60)
        
        # Project info
        project = status_info["project"]
        print(f"Project Name: {project.get('name', 'N/A')}")
        print(f"Version: {project.get('version', 'N/A')}")
        print(f"Status: {project.get('status', 'N/A')}")
        print(f"Agents: {project.get('agents_count', 0)}")
        print(f"Tasks: {project.get('tasks_count', 0)}")
        
        # System info
        system = status_info["system"]
        print(f"\nSystem Status:")
        print(f"  CPU Usage: {system.get('cpu_percent', 'N/A')}%")
        print(f"  Memory Usage: {system.get('memory_percent', 'N/A')}%")
        print(f"  Disk Usage: {system.get('disk_percent', 'N/A')}%")
        
        # File status
        if "files" in project:
            print(f"\nProject Files:")
            for file, exists in project["files"].items():
                status = "✓" if exists else "✗"
                print(f"  {status} {file}")
        
        print("="*60)
    
    async def _show_logs(self, args, context: CLIContext) -> int:
        """Show application logs."""
        try:
            logs_dir = context.project_root / "logs"
            
            if not logs_dir.exists():
                self.print_warning("No logs directory found", context)
                return 0
            
            # Find log files
            log_files = list(logs_dir.glob("*.log"))
            if not log_files:
                self.print_warning("No log files found", context)
                return 0
            
            # Get the most recent log file
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            
            self.print_info(f"Showing logs from: {latest_log.name}", context)
            
            if args.follow:
                await self._follow_logs(latest_log, args, context)
            else:
                await self._show_log_lines(latest_log, args, context)
            
            return 0
            
        except Exception as e:
            self.print_error(f"Error showing logs: {e}", context)
            return 1
    
    async def _show_log_lines(self, log_file: Path, args, context: CLIContext):
        """Show specific number of log lines."""
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Get last N lines
            display_lines = lines[-args.lines:] if len(lines) > args.lines else lines
            
            # Filter by level if specified
            if args.level:
                display_lines = [line for line in display_lines if args.level in line]
            
            for line in display_lines:
                print(line.rstrip())
                
        except Exception as e:
            self.print_error(f"Error reading log file: {e}", context)
    
    async def _follow_logs(self, log_file: Path, args, context: CLIContext):
        """Follow log file output."""
        try:
            self.print_info("Following logs (Ctrl+C to stop)...", context)
            
            with open(log_file, 'r') as f:
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        if not args.level or args.level in line:
                            print(line.rstrip())
                    else:
                        await asyncio.sleep(0.1)
                        
        except KeyboardInterrupt:
            self.print_info("\nStopped following logs", context)
        except Exception as e:
            self.print_error(f"Error following logs: {e}", context)
    
    async def _clean_project(self, args, context: CLIContext) -> int:
        """Clean project artifacts and cache."""
        try:
            cleaned_items = []
            
            if args.cache_only or args.all:
                # Clean cache directories
                cache_dirs = [
                    context.project_root / "__pycache__",
                    context.project_root / ".pytest_cache",
                    context.project_root / "aiflow_memory.db"
                ]
                
                for cache_dir in cache_dirs:
                    if cache_dir.exists():
                        if cache_dir.is_dir():
                            import shutil
                            shutil.rmtree(cache_dir)
                        else:
                            cache_dir.unlink()
                        cleaned_items.append(str(cache_dir.name))
            
            if args.all:
                # Clean logs
                logs_dir = context.project_root / "logs"
                if logs_dir.exists():
                    import shutil
                    shutil.rmtree(logs_dir)
                    cleaned_items.append("logs/")
                
                # Clean temporary data
                temp_files = list(context.project_root.glob("*.tmp"))
                for temp_file in temp_files:
                    temp_file.unlink()
                    cleaned_items.append(temp_file.name)
            
            if cleaned_items:
                self.print_success(f"Cleaned: {', '.join(cleaned_items)}", context)
            else:
                self.print_info("Nothing to clean", context)
            
            return 0
            
        except Exception as e:
            self.print_error(f"Error cleaning project: {e}", context)
            return 1
    
    async def _manage_config(self, args, context: CLIContext) -> int:
        """Manage project configuration."""
        try:
            config_file = context.project_root / "aiflow.json"
            
            if args.config_action == "show":
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    print(json.dumps(config, indent=2))
                else:
                    self.print_error("No configuration file found", context)
                    return 1
            
            elif args.config_action == "validate":
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    # Basic validation
                    required_fields = ["name", "version", "agents"]
                    missing_fields = [field for field in required_fields if field not in config]
                    
                    if missing_fields:
                        self.print_error(f"Missing required fields: {', '.join(missing_fields)}", context)
                        return 1
                    else:
                        self.print_success("Configuration is valid", context)
                else:
                    self.print_error("No configuration file found", context)
                    return 1
            
            elif args.config_action in ["get", "set"]:
                if not args.key:
                    self.print_error("Key is required for get/set actions", context)
                    return 1
                
                if args.config_action == "set" and not args.value:
                    self.print_error("Value is required for set action", context)
                    return 1
                
                # Implementation for get/set would go here
                self.print_info(f"Config {args.config_action} not yet implemented", context)
            
            return 0
            
        except Exception as e:
            self.print_error(f"Error managing config: {e}", context)
            return 1
    
    async def _monitor_system(self, args, context: CLIContext) -> int:
        """Monitor system resources and performance."""
        try:
            self.print_info(f"Monitoring system (interval: {args.interval}s)...", context)
            self.print_info("Press Ctrl+C to stop", context)
            
            start_time = datetime.now()
            
            while True:
                # Get current metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Print metrics
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] CPU: {cpu_percent:5.1f}% | "
                      f"Memory: {memory.percent:5.1f}% | "
                      f"Disk: {disk.percent:5.1f}%")
                
                # Check duration
                if args.duration:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= args.duration:
                        break
                
                await asyncio.sleep(args.interval)
            
            return 0
            
        except KeyboardInterrupt:
            self.print_info("\nMonitoring stopped", context)
            return 0
        except Exception as e:
            self.print_error(f"Error monitoring system: {e}", context)
            return 1
