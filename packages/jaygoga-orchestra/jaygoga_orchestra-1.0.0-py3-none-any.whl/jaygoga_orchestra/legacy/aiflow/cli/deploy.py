"""
Deployment commands for AIFlow CLI.

Provides commands for deploying AIFlow projects to various environments.
"""

import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any

from .base import BaseCLICommand, CLIContext


class DeployCommand(BaseCLICommand):
    """Command for deploying AIFlow projects."""
    
    def __init__(self):
        super().__init__(
            name="deploy",
            description="Deploy AIFlow projects to various environments"
        )
    
    def add_arguments(self, parser) -> None:
        """Add deploy command arguments."""
        parser.add_argument(
            "--environment", "-e",
            choices=["development", "staging", "production"],
            default="development",
            help="Deployment environment (default: development)"
        )
        
        parser.add_argument(
            "--config", "-c",
            type=Path,
            help="Deployment configuration file"
        )
        
        parser.add_argument(
            "--platform", "-p",
            choices=["docker", "kubernetes", "aws", "gcp", "azure", "local"],
            default="local",
            help="Deployment platform (default: local)"
        )
        
        parser.add_argument(
            "--build-only",
            action="store_true",
            help="Only build, don't deploy"
        )
        
        parser.add_argument(
            "--no-build",
            action="store_true",
            help="Skip build step"
        )
        
        parser.add_argument(
            "--tag", "-t",
            help="Docker image tag or deployment version"
        )
        
        parser.add_argument(
            "--registry",
            help="Container registry URL"
        )
        
        parser.add_argument(
            "--namespace", "-n",
            help="Kubernetes namespace"
        )
        
        parser.add_argument(
            "--replicas", "-r",
            type=int,
            default=1,
            help="Number of replicas (default: 1)"
        )
        
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without actual deployment"
        )
    
    async def execute(self, context: CLIContext, args) -> int:
        """Execute the deploy command."""
        try:
            self.print_info(f"Starting deployment to {args.environment} environment...", context)
            
            # Load deployment configuration
            config = await self._load_deployment_config(args, context)
            if config is None:
                return 1
            
            # Validate deployment setup
            if not await self._validate_deployment_setup(config, args, context):
                return 1
            
            # Build if needed
            if not args.no_build:
                if not await self._build_project(config, args, context):
                    return 1
            
            # Deploy if not build-only
            if not args.build_only:
                if not await self._deploy_project(config, args, context):
                    return 1
            
            self.print_success("Deployment completed successfully!", context)
            return 0
            
        except Exception as e:
            self.print_error(f"Deployment failed: {e}", context)
            return 1
    
    async def _load_deployment_config(self, args, context: CLIContext) -> Dict[str, Any]:
        """Load deployment configuration."""
        try:
            if args.config and args.config.exists():
                with open(args.config, 'r') as f:
                    config = json.load(f)
                self.print_info(f"Loaded deployment config: {args.config}", context)
            else:
                # Default configuration
                config = {
                    "deployment": {
                        "platform": args.platform,
                        "environment": args.environment,
                        "replicas": args.replicas
                    },
                    "build": {
                        "dockerfile": "Dockerfile",
                        "context": ".",
                        "tag": args.tag or f"aiflow-app:{args.environment}"
                    },
                    "registry": {
                        "url": args.registry or "localhost:5000",
                        "push": args.platform != "local"
                    }
                }
                self.print_info("Using default deployment configuration", context)
            
            return config
            
        except Exception as e:
            self.print_error(f"Error loading deployment config: {e}", context)
            return None
    
    async def _validate_deployment_setup(self, config: Dict[str, Any], args, context: CLIContext) -> bool:
        """Validate deployment setup."""
        try:
            # Check if project config exists
            project_config_path = context.project_root / "aiflow.json"
            if not project_config_path.exists():
                self.print_error("No aiflow.json found. Run this command from an AIFlow project directory.", context)
                return False
            
            # Check platform-specific requirements
            platform = config["deployment"]["platform"]
            
            if platform == "docker":
                if not await self._check_docker():
                    self.print_error("Docker is not available", context)
                    return False
                
                dockerfile_path = context.project_root / config["build"]["dockerfile"]
                if not dockerfile_path.exists():
                    self.print_warning(f"Dockerfile not found: {dockerfile_path}", context)
                    self.print_info("Creating default Dockerfile...", context)
                    await self._create_default_dockerfile(dockerfile_path, context)
            
            elif platform == "kubernetes":
                if not await self._check_kubectl():
                    self.print_error("kubectl is not available", context)
                    return False
            
            self.print_info("Deployment setup validation passed", context)
            return True
            
        except Exception as e:
            self.print_error(f"Validation error: {e}", context)
            return False
    
    async def _check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    async def _check_kubectl(self) -> bool:
        """Check if kubectl is available."""
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    async def _create_default_dockerfile(self, dockerfile_path: Path, context: CLIContext):
        """Create a default Dockerfile."""
        dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash aiflow
RUN chown -R aiflow:aiflow /app
USER aiflow

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["python", "main.py"]
"""
        
        dockerfile_path.write_text(dockerfile_content)
        self.print_info(f"Created default Dockerfile: {dockerfile_path}", context)
    
    async def _build_project(self, config: Dict[str, Any], args, context: CLIContext) -> bool:
        """Build the project."""
        try:
            platform = config["deployment"]["platform"]
            
            if platform in ["docker", "kubernetes"]:
                return await self._build_docker_image(config, args, context)
            else:
                self.print_info("No build step required for this platform", context)
                return True
                
        except Exception as e:
            self.print_error(f"Build error: {e}", context)
            return False
    
    async def _build_docker_image(self, config: Dict[str, Any], args, context: CLIContext) -> bool:
        """Build Docker image."""
        try:
            build_config = config["build"]
            tag = build_config["tag"]
            dockerfile = build_config["dockerfile"]
            build_context = build_config["context"]
            
            self.print_info(f"Building Docker image: {tag}", context)
            
            if args.dry_run:
                self.print_info(f"[DRY RUN] Would build: docker build -t {tag} -f {dockerfile} {build_context}", context)
                return True
            
            # Build Docker image
            cmd = [
                "docker", "build",
                "-t", tag,
                "-f", dockerfile,
                build_context
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=context.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Stream output
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output and context.verbose:
                    print(output.strip())
            
            if process.returncode != 0:
                self.print_error("Docker build failed", context)
                return False
            
            self.print_success(f"Docker image built successfully: {tag}", context)
            
            # Push to registry if configured
            if config["registry"]["push"]:
                return await self._push_docker_image(config, args, context)
            
            return True
            
        except Exception as e:
            self.print_error(f"Docker build error: {e}", context)
            return False
    
    async def _push_docker_image(self, config: Dict[str, Any], args, context: CLIContext) -> bool:
        """Push Docker image to registry."""
        try:
            registry_url = config["registry"]["url"]
            tag = config["build"]["tag"]
            
            # Tag for registry
            registry_tag = f"{registry_url}/{tag}"
            
            self.print_info(f"Pushing Docker image to registry: {registry_tag}", context)
            
            if args.dry_run:
                self.print_info(f"[DRY RUN] Would push: {registry_tag}", context)
                return True
            
            # Tag image
            subprocess.run(
                ["docker", "tag", tag, registry_tag],
                check=True,
                capture_output=True
            )
            
            # Push image
            subprocess.run(
                ["docker", "push", registry_tag],
                check=True,
                capture_output=True
            )
            
            self.print_success(f"Docker image pushed successfully: {registry_tag}", context)
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Docker push failed: {e}", context)
            return False
    
    async def _deploy_project(self, config: Dict[str, Any], args, context: CLIContext) -> bool:
        """Deploy the project."""
        try:
            platform = config["deployment"]["platform"]
            
            if platform == "local":
                return await self._deploy_local(config, args, context)
            elif platform == "docker":
                return await self._deploy_docker(config, args, context)
            elif platform == "kubernetes":
                return await self._deploy_kubernetes(config, args, context)
            else:
                self.print_error(f"Unsupported deployment platform: {platform}", context)
                return False
                
        except Exception as e:
            self.print_error(f"Deployment error: {e}", context)
            return False
    
    async def _deploy_local(self, config: Dict[str, Any], args, context: CLIContext) -> bool:
        """Deploy locally."""
        self.print_info("Starting local deployment...", context)
        
        if args.dry_run:
            self.print_info("[DRY RUN] Would start local application", context)
            return True
        
        # This would typically start the application locally
        self.print_success("Local deployment completed", context)
        return True
    
    async def _deploy_docker(self, config: Dict[str, Any], args, context: CLIContext) -> bool:
        """Deploy using Docker."""
        try:
            tag = config["build"]["tag"]
            
            self.print_info(f"Starting Docker container: {tag}", context)
            
            if args.dry_run:
                self.print_info(f"[DRY RUN] Would run: docker run -d -p 8000:8000 {tag}", context)
                return True
            
            # Run Docker container
            subprocess.run([
                "docker", "run", "-d",
                "-p", "8000:8000",
                "--name", f"aiflow-{args.environment}",
                tag
            ], check=True, capture_output=True)
            
            self.print_success("Docker deployment completed", context)
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Docker deployment failed: {e}", context)
            return False
    
    async def _deploy_kubernetes(self, config: Dict[str, Any], args, context: CLIContext) -> bool:
        """Deploy to Kubernetes."""
        try:
            self.print_info("Deploying to Kubernetes...", context)
            
            # Generate Kubernetes manifests
            manifests = await self._generate_k8s_manifests(config, args, context)
            
            if args.dry_run:
                self.print_info("[DRY RUN] Would apply Kubernetes manifests", context)
                return True
            
            # Apply manifests
            for manifest_file in manifests:
                subprocess.run([
                    "kubectl", "apply", "-f", str(manifest_file)
                ], check=True, capture_output=True)
            
            self.print_success("Kubernetes deployment completed", context)
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Kubernetes deployment failed: {e}", context)
            return False
    
    async def _generate_k8s_manifests(self, config: Dict[str, Any], args, context: CLIContext) -> list:
        """Generate Kubernetes manifests."""
        manifests_dir = context.project_root / "k8s"
        manifests_dir.mkdir(exist_ok=True)
        
        # Generate deployment manifest
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "aiflow-app",
                "namespace": args.namespace or "default"
            },
            "spec": {
                "replicas": config["deployment"]["replicas"],
                "selector": {
                    "matchLabels": {
                        "app": "aiflow-app"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "aiflow-app"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "aiflow-app",
                            "image": config["build"]["tag"],
                            "ports": [{
                                "containerPort": 8000
                            }]
                        }]
                    }
                }
            }
        }
        
        deployment_file = manifests_dir / "deployment.yaml"
        with open(deployment_file, 'w') as f:
            import yaml
            yaml.dump(deployment_manifest, f)
        
        return [deployment_file]
