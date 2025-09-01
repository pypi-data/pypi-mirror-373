"""
CI/CD Template Manager for Clyrdia
Provides unified interface for managing and generating CI/CD templates across all platforms.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .github_actions import GitHubActionsTemplate
from .gitlab_ci import GitLabCITemplate
from .jenkins import JenkinsTemplate
from .circleci import CircleCITemplate
from .azure_devops import AzureDevOpsTemplate
from ..auth.licensing import LicensingManager

@dataclass
class TemplateConfig:
    """Configuration for CI/CD template generation"""
    platform: str
    template_type: str
    workflow_name: str = "AI Benchmark"
    benchmark_file: str = "benchmark.yaml"
    python_version: str = "3.9"
    trigger_on: List[str] = None
    quality_gate: float = 0.8
    cost_threshold: float = 10.0
    model_registry: str = "mlflow"
    deployment_target: str = "kubernetes"
    
    def __post_init__(self):
        if self.trigger_on is None:
            self.trigger_on = ["push", "pull_request"]

@dataclass
class GeneratedTemplate:
    """Generated CI/CD template with metadata"""
    platform: str
    template_type: str
    content: str
    filename: str
    description: str

class CICDTemplateManager:
    """Manages CI/CD template generation with security enforcement"""
    
    def __init__(self):
        self.licensing = LicensingManager()
        self._validate_access()
        self.templates = {
            'github-actions': GitHubActionsTemplate(),
            'gitlab-ci': GitLabCITemplate(),
            'jenkins': JenkinsTemplate(),
            'circleci': CircleCITemplate(),
            'azure-devops': AzureDevOpsTemplate()
        }
        
        self.platform_info = {
            'github-actions': {
                'name': 'GitHub Actions',
                'description': 'GitHub-hosted CI/CD with YAML workflows',
                'file_extension': '.yml',
                'output_dir': '.github/workflows',
                'website': 'https://github.com/features/actions'
            },
            'gitlab-ci': {
                'name': 'GitLab CI/CD',
                'description': 'GitLab-hosted CI/CD with YAML pipelines',
                'file_extension': '.yml',
                'output_dir': '.gitlab-ci',
                'website': 'https://docs.gitlab.com/ee/ci/'
            },
            'jenkins': {
                'name': 'Jenkins',
                'description': 'Self-hosted CI/CD with Groovy pipelines',
                'file_extension': '',
                'output_dir': 'jenkins',
                'website': 'https://www.jenkins.io/'
            },
            'circleci': {
                'name': 'CircleCI',
                'description': 'Cloud-hosted CI/CD with YAML configs',
                'file_extension': '.yml',
                'output_dir': '.circleci',
                'website': 'https://circleci.com/'
            },
            'azure-devops': {
                'name': 'Azure DevOps',
                'description': 'Microsoft-hosted CI/CD with YAML pipelines',
                'file_extension': '.yml',
                'output_dir': 'azure-pipelines',
                'website': 'https://azure.microsoft.com/en-us/services/devops/'
            }
        }
        
        self.template_types = {
            'basic': {
                'name': 'Basic',
                'description': 'Simple CI/CD pipeline for basic AI benchmarking',
                'features': ['Basic benchmarking', 'Result collection', 'Artifact publishing']
            },
            'advanced': {
                'name': 'Advanced',
                'description': 'Advanced pipeline with quality gates and cost monitoring',
                'features': ['Quality gates', 'Cost thresholds', 'Advanced analysis', 'Scheduled runs']
            },
            'mlops': {
                'name': 'MLOps',
                'description': 'Full MLOps pipeline with model deployment',
                'features': ['Model versioning', 'MLflow integration', 'Staging/production deployment', 'Release management']
            }
        }
    
    def _validate_access(self):
        """Validate that user has access to CI/CD features"""
        try:
            # Check if user has CI/CD access
            if not self.licensing.has_feature_access('cicd_integration'):
                self.licensing.require_feature_access('cicd_integration')
        except Exception as e:
            raise Exception(f"Access denied: {str(e)}")
    
    def list_platforms(self) -> List[str]:
        """List available CI/CD platforms"""
        self._validate_access()
        return [
            "GitHub Actions",
            "GitLab CI",
            "Jenkins",
            "CircleCI", 
            "Azure DevOps"
        ]
    
    def list_template_types(self) -> List[str]:
        """List available template types"""
        self._validate_access()
        return [
            "basic",
            "advanced", 
            "mlops"
        ]
    
    def get_platform_info(self, platform: str) -> Optional[Dict[str, str]]:
        """Get information about a specific platform"""
        if platform in self.platform_info:
            return {
                'id': platform,
                **self.platform_info[platform]
            }
        return None
    
    def get_template_type_info(self, template_type: str) -> Optional[Dict[str, str]]:
        """Get information about a specific template type"""
        if template_type in self.template_types:
            return {
                'id': template_type,
                **self.template_types[template_type]
            }
        return None
    
    def generate_template(self, config: TemplateConfig) -> GeneratedTemplate:
        """Generate a CI/CD template based on configuration"""
        
        if config.platform not in self.templates:
            raise ValueError(f"Unsupported platform: {config.platform}")
        
        if config.template_type not in self.template_types:
            raise ValueError(f"Unsupported template type: {config.template_type}")
        
        template = self.templates[config.platform]
        
        # Generate template content
        if config.platform == 'github-actions':
            content = template.generate_workflow_file(
                template_type=config.template_type,
                workflow_name=config.workflow_name,
                benchmark_file=config.benchmark_file,
                python_version=config.python_version,
                quality_gate=config.quality_gate,
                cost_threshold=config.cost_threshold,
                trigger_on=config.trigger_on
            )
        elif config.platform == 'gitlab-ci':
            content = template.generate_pipeline_file(
                template_type=config.template_type,
                pipeline_name=config.workflow_name,
                benchmark_file=config.benchmark_file,
                python_version=config.python_version,
                quality_gate=config.quality_gate,
                cost_threshold=config.cost_threshold
            )
        elif config.platform == 'jenkins':
            content = template.generate_pipeline_file(
                template_type=config.template_type,
                pipeline_name=config.workflow_name,
                benchmark_file=config.benchmark_file,
                python_version=config.python_version,
                quality_gate=config.quality_gate,
                cost_threshold=config.cost_threshold
            )
        elif config.platform == 'circleci':
            content = template.generate_config_file(
                template_type=config.template_type,
                config_name=config.workflow_name,
                benchmark_file=config.benchmark_file,
                python_version=config.python_version,
                quality_gate=config.quality_gate,
                cost_threshold=config.cost_threshold
            )
        elif config.platform == 'azure-devops':
            content = template.generate_pipeline_file(
                template_type=config.template_type,
                pipeline_name=config.workflow_name,
                benchmark_file=config.benchmark_file,
                python_version=config.python_version,
                quality_gate=config.quality_gate,
                cost_threshold=config.cost_threshold
            )
        
        # Save template to file
        file_path = self._save_template(config, content)
        
        # Generate metadata
        metadata = {
            'generated_at': str(Path(file_path).stat().st_mtime),
            'platform': config.platform,
            'template_type': config.template_type,
            'file_size': str(Path(file_path).stat().st_size),
            'config_hash': str(hash(str(config))) # Changed to str(config) to avoid asdict
        }
        
        return GeneratedTemplate(
            platform=config.platform,
            template_type=config.template_type,
            content=content,
            filename=Path(file_path).name,
            description=f"{self.platform_info[config.platform]['name']} {self.template_types[config.template_type]['name']} template"
        )
    
    def _save_template(self, config: TemplateConfig, content: str) -> str:
        """Save template content to file"""
        
        platform_info = self.platform_info[config.platform]
        output_dir = Path(platform_info['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if config.platform == 'github-actions':
            if config.template_type == 'basic':
                filename = 'ai-benchmark.yml'
            elif config.template_type == 'advanced':
                filename = 'advanced-ai-benchmark.yml'
            elif config.template_type == 'mlops':
                filename = 'mlops-ai-benchmark.yml'
        elif config.platform == 'gitlab-ci':
            if config.template_type == 'basic':
                filename = '.gitlab-ci.yml'
            elif config.template_type == 'advanced':
                filename = 'advanced-gitlab-ci.yml'
            elif config.template_type == 'mlops':
                filename = 'mlops-gitlab-ci.yml'
        elif config.platform == 'jenkins':
            if config.template_type == 'basic':
                filename = 'Jenkinsfile'
            elif config.template_type == 'advanced':
                filename = 'Jenkinsfile.advanced'
            elif config.template_type == 'mlops':
                filename = 'Jenkinsfile.mlops'
        elif config.platform == 'circleci':
            if config.template_type == 'basic':
                filename = 'config.yml'
            elif config.template_type == 'advanced':
                filename = 'config.advanced.yml'
            elif config.template_type == 'mlops':
                filename = 'config.mlops.yml'
        elif config.platform == 'azure-devops':
            if config.template_type == 'basic':
                filename = 'azure-pipelines.yml'
            elif config.template_type == 'advanced':
                filename = 'azure-pipelines.advanced.yml'
            elif config.template_type == 'mlops':
                filename = 'azure-pipelines.mlops.yml'
        
        file_path = output_dir / filename
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return str(file_path)
    
    def generate_all_templates(self, 
                              benchmark_file: str = "benchmark.yaml",
                              output_base_dir: str = "cicd-templates") -> List[GeneratedTemplate]:
        """Generate all possible CI/CD templates"""
        
        results = []
        base_dir = Path(output_base_dir)
        base_dir.mkdir(exist_ok=True)
        
        for platform in self.platform_info.keys():
            for template_type in self.template_types.keys():
                config = TemplateConfig(
                    platform=platform,
                    template_type=template_type,
                    benchmark_file=benchmark_file
                )
                
                try:
                    result = self.generate_template(config)
                    results.append(result)
                except Exception as e:
                    print(f"Failed to generate {platform} {template_type}: {e}")
        
        return results
    
    def create_setup_guide(self, platform: str, template_type: str) -> str:
        """Create a setup guide for a specific platform and template type"""
        
        platform_info = self.get_platform_info(platform)
        template_info = self.get_template_type_info(template_type)
        
        if not platform_info or not template_info:
            return "Invalid platform or template type"
        
        guide = f"""# {platform_info['name']} Setup Guide for {template_info['name']} Template

## Overview
This guide will help you set up {platform_info['name']} CI/CD for AI benchmarking with Clyrdia using the {template_info['name']} template.

## Prerequisites
- A {platform_info['name']} account
- A repository with your AI models and benchmark configuration
- Clyrdia CLI installed and configured

## Step 1: Generate the Template
```bash
# Using Clyrdia CLI
clyrdia-cli cicd generate --platform {platform} --type {template_type}

# Or manually copy the generated file to your repository
```

## Step 2: Configure Secrets
Set the following secret in your {platform_info['name']} project:

- **CLYRIDIA_API_KEY**: Your Clyrdia API key for authentication

## Step 3: Customize the Template
Edit the generated template file to match your specific needs:

- Update the benchmark file path if different from `benchmark.yaml`
- Adjust Python version if needed
- Modify quality gates and cost thresholds
- Add custom environment variables

## Step 4: Commit and Push
```bash
git add {platform_info['output_dir']}/
git commit -m "Add {platform_info['name']} CI/CD configuration"
git push
```

## Step 5: Verify Setup
- Check that your pipeline is running
- Monitor benchmark results
- Verify quality gates and cost thresholds

## Features
{chr(10).join(f"- {feature}" for feature in template_info['features'])}

## Documentation
For more information, visit: {platform_info['website']}

## Support
If you encounter issues, check the Clyrdia documentation or contact support.
"""
        
        return guide
    
    def validate_config(self, config: TemplateConfig) -> List[str]:
        """Validate a template configuration and return any errors"""
        
        errors = []
        
        # Check platform
        if config.platform not in self.platform_info:
            errors.append(f"Unsupported platform: {config.platform}")
        
        # Check template type
        if config.template_type not in self.template_types:
            errors.append(f"Unsupported template type: {config.template_type}")
        
        # Check benchmark file
        if not config.benchmark_file:
            errors.append("Benchmark file is required")
        
        # Check Python version
        if not config.python_version:
            errors.append("Python version is required")
        
        # Check quality gate range
        if config.quality_gate < 0.0 or config.quality_gate > 1.0:
            errors.append("Quality gate must be between 0.0 and 1.0")
        
        # Check cost threshold
        if config.cost_threshold < 0.0:
            errors.append("Cost threshold must be positive")
        
        return errors
    
    def get_recommended_config(self, 
                              platform: str, 
                              template_type: str,
                              use_case: str = "general") -> TemplateConfig:
        """Get a recommended configuration for a specific use case"""
        
        # Base configuration
        config = TemplateConfig(
            platform=platform,
            template_type=template_type
        )
        
        # Customize based on use case
        if use_case == "startup":
            config.quality_gate = 0.7
            config.cost_threshold = 5.0
        elif use_case == "enterprise":
            config.quality_gate = 0.9
            config.cost_threshold = 50.0
        elif use_case == "research":
            config.quality_gate = 0.6
            config.cost_threshold = 2.0
        
        return config
    
    def export_templates(self, 
                        output_dir: str = "cicd-export",
                        include_guides: bool = True) -> str:
        """Export all templates with optional setup guides"""
        
        export_dir = Path(output_dir)
        export_dir.mkdir(exist_ok=True)
        
        # Create README
        readme_content = """# Clyrdia CI/CD Templates Export

This directory contains all available CI/CD templates for different platforms and use cases.

## Platforms Supported
"""
        
        for platform_id, info in self.platform_info.items():
            readme_content += f"- **{info['name']}** ({platform_id}): {info['description']}\n"
        
        readme_content += "\n## Template Types\n"
        
        for template_id, info in self.template_types.items():
            readme_content += f"- **{info['name']}** ({template_id}): {info['description']}\n"
        
        readme_content += """
## Quick Start
1. Choose your platform and template type
2. Copy the template file to your repository
3. Follow the setup guide for your platform
4. Configure your Clyrdia API key
5. Customize the template as needed

## Support
For help with setup or customization, refer to the Clyrdia documentation.
"""
        
        with open(export_dir / "README.md", 'w') as f:
            f.write(readme_content)
        
        # Export all templates
        templates = self.generate_all_templates()
        
        for template in templates:
            # Create platform directory
            platform_dir = export_dir / template.platform
            platform_dir.mkdir(exist_ok=True)
            
            # Copy template file
            template_path = Path(template.file_path)
            if template_path.exists():
                import shutil
                shutil.copy2(template_path, platform_dir / template_path.name)
            
            # Create setup guide if requested
            if include_guides:
                guide = self.create_setup_guide(template.platform, template.template_type)
                guide_file = platform_dir / f"setup-{template.template_type}.md"
                with open(guide_file, 'w') as f:
                    f.write(guide)
        
        return str(export_dir)
