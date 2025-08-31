"""
Project creation and scaffolding commands for AIFlow CLI.

Provides commands for creating new AIFlow projects with templates and boilerplate.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any

from .base import BaseCLICommand, CLIContext, CLIUtils


class CreateCommand(BaseCLICommand):
    """Command for creating new AIFlow projects."""
    
    def __init__(self):
        super().__init__(
            name="create",
            description="Create a new AIFlow project with templates and boilerplate"
        )
    
    def add_arguments(self, parser) -> None:
        """Add create command arguments."""
        parser.add_argument(
            "project_name",
            help="Name of the project to create"
        )
        
        parser.add_argument(
            "--template", "-t",
            choices=["basic", "advanced", "minimal", "enterprise"],
            default="basic",
            help="Project template to use (default: basic)"
        )
        
        parser.add_argument(
            "--description", "-d",
            default="",
            help="Project description"
        )
        
        parser.add_argument(
            "--author",
            default="",
            help="Project author"
        )
        
        parser.add_argument(
            "--license",
            choices=["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "None"],
            default="MIT",
            help="Project license (default: MIT)"
        )
        
        parser.add_argument(
            "--python-version",
            default="3.8",
            help="Minimum Python version (default: 3.8)"
        )
        
        parser.add_argument(
            "--force", "-f",
            action="store_true",
            help="Overwrite existing directory"
        )
        
        parser.add_argument(
            "--no-git",
            action="store_true",
            help="Don't initialize git repository"
        )
        
        parser.add_argument(
            "--no-venv",
            action="store_true",
            help="Don't create virtual environment"
        )
        
        parser.add_argument(
            "--install-deps",
            action="store_true",
            help="Install dependencies after creation"
        )
    
    def validate_args(self, args) -> bool:
        """Validate create command arguments."""
        if not CLIUtils.validate_project_name(args.project_name):
            print(f"Invalid project name: {args.project_name}")
            print("Project name must be a valid Python identifier and not a reserved word.")
            return False
        
        project_path = Path.cwd() / args.project_name
        if project_path.exists() and not args.force:
            print(f"Directory '{args.project_name}' already exists. Use --force to overwrite.")
            return False
        
        return True
    
    async def execute(self, context: CLIContext, args) -> int:
        """Execute the create command."""
        project_path = Path.cwd() / args.project_name
        
        try:
            # Create project directory
            if project_path.exists() and args.force:
                self.print_info(f"Removing existing directory: {project_path}", context)
                shutil.rmtree(project_path)
            
            project_path.mkdir(parents=True, exist_ok=True)
            self.print_info(f"Creating project: {args.project_name}", context)
            
            # Create project structure
            if not CLIUtils.create_project_structure(project_path):
                self.print_error("Failed to create project structure", context)
                return 1
            
            # Generate project files based on template
            if not await self._generate_project_files(project_path, args, context):
                self.print_error("Failed to generate project files", context)
                return 1
            
            # Initialize git repository
            if not args.no_git:
                await self._initialize_git(project_path, context)
            
            # Create virtual environment
            if not args.no_venv:
                await self._create_virtual_environment(project_path, context)
            
            # Install dependencies
            if args.install_deps:
                await self._install_dependencies(project_path, context)
            
            self.print_success(f"Project '{args.project_name}' created successfully!", context)
            self._print_next_steps(args.project_name, context)
            
            return 0
            
        except Exception as e:
            self.print_error(f"Failed to create project: {e}", context)
            return 1
    
    async def _generate_project_files(self, project_path: Path, args, context: CLIContext) -> bool:
        """Generate project files based on template."""
        try:
            templates = CLIUtils.get_template_content("")
            
            # Template variables
            template_vars = {
                "project_name": args.project_name,
                "project_description": args.description or f"AIFlow project: {args.project_name}",
                "author": args.author or "AIFlow Developer",
                "license": args.license,
                "python_version": args.python_version,
                "agent_name": f"{args.project_name.title()}Agent",
                "task_name": f"{args.project_name.title()}Task",
                "task_description": f"Main task for {args.project_name}"
            }
            
            # Generate main agent file
            agent_content = CLIUtils.format_template(
                templates["basic_agent"],
                **template_vars
            )
            agent_file = project_path / "agents" / "main.py"
            agent_file.write_text(agent_content)
            
            # Generate main task file
            task_content = CLIUtils.format_template(
                templates["basic_task"],
                **template_vars
            )
            task_file = project_path / "tasks" / "main.py"
            task_file.write_text(task_content)
            
            # Generate project configuration
            config_content = CLIUtils.format_template(
                templates["project_config"],
                **template_vars
            )
            config_file = project_path / "aiflow.json"
            config_file.write_text(config_content)
            
            # Generate main script
            main_content = CLIUtils.format_template(
                templates["main_script"],
                **template_vars
            )
            main_file = project_path / "main.py"
            main_file.write_text(main_content)
            
            # Generate requirements.txt
            requirements_file = project_path / "requirements.txt"
            requirements_file.write_text(templates["requirements"])
            
            # Generate .gitignore
            gitignore_file = project_path / ".gitignore"
            gitignore_file.write_text(templates["gitignore"])
            
            # Generate README.md
            readme_content = CLIUtils.format_template(
                templates["readme"],
                **template_vars
            )
            readme_file = project_path / "README.md"
            readme_file.write_text(readme_content)
            
            # Generate additional files based on template
            if args.template == "advanced":
                await self._generate_advanced_template_files(project_path, template_vars)
            elif args.template == "enterprise":
                await self._generate_enterprise_template_files(project_path, template_vars)
            
            self.print_info("Generated project files", context)
            return True
            
        except Exception as e:
            self.print_error(f"Error generating project files: {e}", context)
            return False
    
    async def _generate_advanced_template_files(self, project_path: Path, template_vars: Dict[str, Any]):
        """Generate additional files for advanced template."""
        # Create additional directories
        (project_path / "configs" / "agents").mkdir(parents=True, exist_ok=True)
        (project_path / "configs" / "tasks").mkdir(parents=True, exist_ok=True)
        (project_path / "tools" / "custom").mkdir(parents=True, exist_ok=True)
        
        # Generate agent config
        agent_config = {
            "name": template_vars["agent_name"],
            "description": f"Advanced agent for {template_vars['project_name']}",
            "llm": {
                "model_provider": "openai",
                "model_name": "gpt-4o"
            },
            "memory": {
                "enabled": True,
                "max_entries": 1000
            },
            "tools": ["web_search", "file_operations"]
        }
        
        import json
        config_file = project_path / "configs" / "agents" / "main.json"
        config_file.write_text(json.dumps(agent_config, indent=2))
        
        # Generate custom tool template
        tool_template = '''"""
Custom tool for {project_name}.
"""

from jaygoga_orchestra.tools.base_tool import BaseTool

class Custom{project_name}Tool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_{project_name_lower}_tool",
            description="Custom tool for {project_name}"
        )
    
    async def execute(self, **kwargs):
        """Execute the custom tool."""
        # Add your custom tool logic here
        return {{"result": "Custom tool executed successfully"}}
'''.format(
            project_name=template_vars["project_name"],
            project_name_lower=template_vars["project_name"].lower()
        )
        
        tool_file = project_path / "tools" / "custom" / "main.py"
        tool_file.write_text(tool_template)
    
    async def _generate_enterprise_template_files(self, project_path: Path, template_vars: Dict[str, Any]):
        """Generate additional files for enterprise template."""
        # Create enterprise directories
        (project_path / "deployment").mkdir(parents=True, exist_ok=True)
        (project_path / "monitoring").mkdir(parents=True, exist_ok=True)
        (project_path / "security").mkdir(parents=True, exist_ok=True)
        
        # Generate Docker files
        dockerfile_content = f'''FROM python:3.{template_vars["python_version"]}-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
'''
        dockerfile = project_path / "Dockerfile"
        dockerfile.write_text(dockerfile_content)
        
        # Generate docker-compose.yml
        compose_content = f'''version: '3.8'

services:
  {template_vars["project_name"].lower()}:
    build: .
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: aiflow
      POSTGRES_USER: aiflow
      POSTGRES_PASSWORD: aiflow_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
'''
        compose_file = project_path / "docker-compose.yml"
        compose_file.write_text(compose_content)
    
    async def _initialize_git(self, project_path: Path, context: CLIContext):
        """Initialize git repository."""
        try:
            import subprocess
            
            # Initialize git repo
            subprocess.run(
                ["git", "init"],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            # Add initial commit
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            self.print_info("Initialized git repository", context)
            
        except subprocess.CalledProcessError:
            self.print_warning("Failed to initialize git repository", context)
        except FileNotFoundError:
            self.print_warning("Git not found, skipping repository initialization", context)
    
    async def _create_virtual_environment(self, project_path: Path, context: CLIContext):
        """Create virtual environment."""
        try:
            import subprocess
            
            subprocess.run(
                ["python", "-m", "venv", "venv"],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            self.print_info("Created virtual environment", context)
            
        except subprocess.CalledProcessError as e:
            self.print_warning(f"Failed to create virtual environment: {e}", context)
    
    async def _install_dependencies(self, project_path: Path, context: CLIContext):
        """Install project dependencies."""
        try:
            import subprocess
            
            # Determine pip path
            if os.name == 'nt':  # Windows
                pip_path = project_path / "venv" / "Scripts" / "pip"
            else:  # Unix-like
                pip_path = project_path / "venv" / "bin" / "pip"
            
            if pip_path.exists():
                subprocess.run(
                    [str(pip_path), "install", "-r", "requirements.txt"],
                    cwd=project_path,
                    check=True,
                    capture_output=True
                )
                self.print_info("Installed dependencies", context)
            else:
                # Fallback to system pip
                subprocess.run(
                    ["pip", "install", "-r", "requirements.txt"],
                    cwd=project_path,
                    check=True,
                    capture_output=True
                )
                self.print_info("Installed dependencies (system pip)", context)
                
        except subprocess.CalledProcessError as e:
            self.print_warning(f"Failed to install dependencies: {e}", context)
    
    def _print_next_steps(self, project_name: str, context: CLIContext):
        """Print next steps for the user."""
        if context.output_format == "json":
            return
        
        steps = f"""
Next steps:
  1. cd {project_name}
  2. Activate virtual environment:
     - Windows: venv\\Scripts\\activate
     - Unix/Mac: source venv/bin/activate
  3. Install dependencies: pip install -r requirements.txt
  4. Configure your API keys in .env file
  5. Run the project: python main.py

For more information, see README.md
"""
        print(steps)
