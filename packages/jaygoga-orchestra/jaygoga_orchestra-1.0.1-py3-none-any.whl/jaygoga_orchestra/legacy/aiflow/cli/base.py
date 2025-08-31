"""
Base CLI framework for AIFlow.

Provides foundational classes and utilities for CLI commands.
"""

import os
import sys
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CLIContext:
    """Context object for CLI commands."""
    
    # Project settings
    project_root: Path
    config_file: Optional[Path] = None
    
    # CLI settings
    verbose: bool = False
    quiet: bool = False
    debug: bool = False
    
    # Output settings
    output_format: str = "text"  # text, json, yaml
    no_color: bool = False
    
    # Environment
    environment: str = "development"
    
    def __post_init__(self):
        if self.config_file is None:
            self.config_file = self.project_root / "aiflow.json"
    
    def load_config(self) -> Dict[str, Any]:
        """Load project configuration."""
        if self.config_file and self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading config: {e}")
        return {}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save project configuration."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def setup_logging(self):
        """Setup logging based on CLI options."""
        if self.debug:
            level = logging.DEBUG
        elif self.verbose:
            level = logging.INFO
        elif self.quiet:
            level = logging.ERROR
        else:
            level = logging.WARNING
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


class BaseCLICommand(ABC):
    """Abstract base class for CLI commands."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def add_arguments(self, parser) -> None:
        """Add command-specific arguments to parser."""
        pass
    
    @abstractmethod
    async def execute(self, context: CLIContext, args) -> int:
        """Execute the command. Return exit code (0 = success)."""
        pass
    
    def validate_args(self, args) -> bool:
        """Validate command arguments. Override if needed."""
        return True
    
    def print_success(self, message: str, context: CLIContext):
        """Print success message."""
        if not context.quiet:
            if context.output_format == "json":
                print(json.dumps({"status": "success", "message": message}))
            else:
                color = "" if context.no_color else "\033[92m"
                reset = "" if context.no_color else "\033[0m"
                print(f"{color}✓ {message}{reset}")
    
    def print_error(self, message: str, context: CLIContext):
        """Print error message."""
        if context.output_format == "json":
            print(json.dumps({"status": "error", "message": message}))
        else:
            color = "" if context.no_color else "\033[91m"
            reset = "" if context.no_color else "\033[0m"
            print(f"{color}✗ {message}{reset}", file=sys.stderr)
    
    def print_info(self, message: str, context: CLIContext):
        """Print info message."""
        if not context.quiet:
            if context.output_format == "json":
                print(json.dumps({"status": "info", "message": message}))
            else:
                color = "" if context.no_color else "\033[94m"
                reset = "" if context.no_color else "\033[0m"
                print(f"{color}ℹ {message}{reset}")
    
    def print_warning(self, message: str, context: CLIContext):
        """Print warning message."""
        if not context.quiet:
            if context.output_format == "json":
                print(json.dumps({"status": "warning", "message": message}))
            else:
                color = "" if context.no_color else "\033[93m"
                reset = "" if context.no_color else "\033[0m"
                print(f"{color}⚠ {message}{reset}")


class CLIUtils:
    """Utility functions for CLI operations."""
    
    @staticmethod
    def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
        """Find the project root by looking for aiflow.json."""
        current = start_path or Path.cwd()
        
        while current != current.parent:
            if (current / "aiflow.json").exists():
                return current
            current = current.parent
        
        return None
    
    @staticmethod
    def create_project_structure(project_path: Path) -> bool:
        """Create basic project directory structure."""
        try:
            directories = [
                "agents",
                "tasks", 
                "tools",
                "configs",
                "data",
                "logs",
                "tests"
            ]
            
            for directory in directories:
                (project_path / directory).mkdir(parents=True, exist_ok=True)
                
                # Create __init__.py files for Python packages
                if directory in ["agents", "tasks", "tools"]:
                    init_file = project_path / directory / "__init__.py"
                    if not init_file.exists():
                        init_file.write_text("# AIFlow project module\n")
            
            return True
        except Exception as e:
            logger.error(f"Error creating project structure: {e}")
            return False
    
    @staticmethod
    def validate_project_name(name: str) -> bool:
        """Validate project name."""
        if not name:
            return False
        
        # Check for valid Python identifier
        if not name.isidentifier():
            return False
        
        # Check for reserved names
        reserved = ["aiflow", "test", "tests", "src", "lib"]
        if name.lower() in reserved:
            return False
        
        return True
    
    @staticmethod
    def get_template_content(template_name: str) -> Dict[str, str]:
        """Get template content for project scaffolding."""
        templates = {
            "basic_agent": '''"""
Basic AIFlow Agent

This is a template for a basic AIFlow agent.
"""

import jaygoga_orchestra

class {agent_name}(aiflow.Agent):
    def __init__(self):
        super().__init__(
            name="{agent_name}",
            description="A basic AIFlow agent",
            llm={{
                "model_provider": "openai",
                "model_name": "gpt-4o-mini"
            }}
        )
    
    async def process_task(self, task_description: str) -> str:
        """Process a task and return the result."""
        # Add your custom logic here
        return await self.generate_response(task_description)
''',
            
            "basic_task": '''"""
Basic AIFlow Task

This is a template for a basic AIFlow task.
"""

import jaygoga_orchestra

class {task_name}(aiflow.Task):
    def __init__(self, agent: aiflow.Agent):
        super().__init__(
            description="{task_description}",
            agent=agent,
            expected_output="Task completion result"
        )
    
    async def validate_result(self, result: str) -> bool:
        """Validate the task result."""
        # Add your validation logic here
        return len(result.strip()) > 0
''',
            
            "project_config": '''{
  "name": "{project_name}",
  "version": "1.0.1",
  "description": "AIFlow project: {project_description}",
  "aiflow_version": "1.0.1",
  "python_version": ">=3.8",
  "dependencies": [
    "aiflow>=1.0.0"
  ],
  "dev_dependencies": [
    "pytest>=6.0.0",
    "pytest-asyncio>=0.18.0"
  ],
  "agents": {{
    "default": {{
      "class": "agents.main.MainAgent",
      "config": {{
        "llm": {{
          "model_provider": "openai",
          "model_name": "gpt-4o-mini"
        }}
      }}
    }}
  }},
  "tasks": {{
    "default": {{
      "class": "tasks.main.MainTask",
      "agent": "default"
    }}
  }},
  "settings": {{
    "memory": {{
      "enabled": true,
      "backend": "sqlite",
      "max_entries": 1000
    }},
    "logging": {{
      "level": "INFO",
      "file": "logs/aiflow.log"
    }}
  }}
}''',
            
            "main_script": '''#!/usr/bin/env python3
"""
Main script for {project_name} AIFlow project.
"""

import asyncio
import jaygoga_orchestra
from agents.main import MainAgent
from tasks.main import MainTask

async def main():
    """Main execution function."""
    # Create agent
    agent = MainAgent()
    
    # Create task
    task = MainTask(agent)
    
    # Create team
    team = aiflow.Team(
        agents=[agent],
        tasks=[task],
        session_name="{project_name}_session"
    )
    
    # Execute
    results = await team.async_go(stream=True)
    
    if results["success"]:
        print("✓ Project executed successfully!")
        print(f"Execution time: {{results['execution_time']:.2f}}s")
    else:
        print("✗ Project execution failed!")
        if "error" in results:
            print(f"Error: {{results['error']}}")
    
    await team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
''',
            
            "requirements": '''# AIFlow project requirements
aiflow>=1.0.0

# Optional dependencies
# openai>=1.0.0  # For OpenAI models
# anthropic>=0.3.0  # For Anthropic models
# google-generativeai>=0.3.0  # For Google models

# Development dependencies
pytest>=6.0.0
pytest-asyncio>=0.18.0
black>=22.0.0
flake8>=4.0.0
''',
            
            "gitignore": '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# AIFlow specific
aiflow_memory.db
logs/
*.log

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Python
venv/
env/
.venv/
dist/
build/
*.egg-info/
''',
            
            "readme": '''# {project_name}

{project_description}

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

Run the main script:
```bash
python main.py
```

## Project Structure

- `agents/` - Agent implementations
- `tasks/` - Task definitions
- `tools/` - Custom tools
- `configs/` - Configuration files
- `data/` - Data files
- `logs/` - Log files
- `tests/` - Test files

## Configuration

Edit `aiflow.json` to configure:
- Agent settings
- Task definitions
- Memory configuration
- Logging settings

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black .
```

Lint code:
```bash
flake8 .
```

## License

This project is licensed under the MIT License.
'''
        }
        
        return templates
    
    @staticmethod
    def format_template(template: str, **kwargs) -> str:
        """Format template with provided variables."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return template
    
    @staticmethod
    def confirm_action(message: str, default: bool = False) -> bool:
        """Ask user for confirmation."""
        suffix = " [Y/n]" if default else " [y/N]"
        try:
            response = input(f"{message}{suffix}: ").strip().lower()
            if not response:
                return default
            return response in ['y', 'yes', 'true', '1']
        except (KeyboardInterrupt, EOFError):
            return False
