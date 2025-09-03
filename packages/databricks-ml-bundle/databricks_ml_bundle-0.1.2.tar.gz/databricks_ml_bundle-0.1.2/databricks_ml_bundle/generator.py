"""Project generator for Databricks ML Bundle."""

import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from typing import Dict, Any


class ProjectGenerator:
    """Generates Databricks ML platform project structure."""
    
    def __init__(self, project_name: str, workspace_host: str, model_type: str, use_gpu: bool):
        self.project_name = project_name
        self.workspace_host = workspace_host
        self.model_type = model_type
        self.use_gpu = use_gpu
        self.template_dir = Path(__file__).parent / "templates"
        
    def get_template_vars(self) -> Dict[str, Any]:
        """Get template variables for rendering."""
        return {
            "project_name": self.project_name,
            "project_name_underscore": self.project_name.replace("-", "_"),
            "workspace_host": self.workspace_host,
            "model_type": self.model_type,
            "use_gpu": self.use_gpu,
            "spark_version": "14.3.x-gpu-ml-scala2.12" if self.use_gpu else "14.3.x-scala2.12",
            "node_type": "g4dn.xlarge" if self.use_gpu else "i3.xlarge",
            "gpu_libraries": ["torch>=2.0.0", "torchvision>=0.15.0"] if self.use_gpu else [],
            "model_specific_deps": self._get_model_dependencies()
        }
    
    def _get_model_dependencies(self) -> list:
        """Get model-specific dependencies."""
        deps = {
            "segmentation": ["monai>=1.3.0", "cellpose==3.0.6", "segment-anything-py"],
            "nlp": ["transformers>=4.20.0", "datasets>=2.0.0", "tokenizers>=0.13.0"],
            "classification": ["scikit-learn>=1.3.2", "xgboost>=1.7.0"],
            "regression": ["scikit-learn>=1.3.2", "statsmodels>=0.14.0"],
            "custom": []
        }
        return deps.get(self.model_type, [])
    
    def generate(self, output_path: Path):
        """Generate the complete project structure."""
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create directory structure
        self._create_directories(output_path)
        
        # Generate files from templates
        self._generate_files(output_path)
        
    def _create_directories(self, output_path: Path):
        """Create the directory structure."""
        directories = [
            "src/ds/utils",
            "notebooks",
            "jobs", 
            "policies",
            "ci",
            "docs"
        ]
        
        for directory in directories:
            (output_path / directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_files(self, output_path: Path):
        """Generate all project files from templates."""
        template_vars = self.get_template_vars()
        
        # File templates to generate
        files_to_generate = [
            ("databricks.yaml.j2", "databricks.yaml"),
            ("requirements.txt.j2", "requirements.txt"),
            ("requirements-lock.txt.j2", "requirements-lock.txt"),
            ("README.md.j2", "README.md"),
            (".gitignore.j2", ".gitignore"),
            ("src/ds/__init__.py.j2", "src/ds/__init__.py"),
            ("src/ds/preprocess.py.j2", "src/ds/preprocess.py"),
            ("src/ds/train.py.j2", "src/ds/train.py"),
            ("src/ds/register.py.j2", "src/ds/register.py"),
            ("src/ds/deploy_serving.py.j2", "src/ds/deploy_serving.py"),
            ("src/ds/utils/__init__.py.j2", "src/ds/utils/__init__.py"),
            ("src/ds/utils/io.py.j2", "src/ds/utils/io.py"),
            ("src/ds/utils/mlflow_utils.py.j2", "src/ds/utils/mlflow_utils.py"),
            ("notebooks/01_preprocess.py.j2", "notebooks/01_preprocess.py"),
            ("notebooks/02_train.py.j2", "notebooks/02_train.py"),
            ("notebooks/03_register_and_validate.py.j2", "notebooks/03_register_and_validate.py"),
            ("jobs/job_preprocess.yml.j2", "jobs/job_preprocess.yml"),
            ("jobs/job_train.yml.j2", "jobs/job_train.yml"),
            ("jobs/job_register.yml.j2", "jobs/job_register.yml"),
            ("jobs/job_deploy_serving.yml.j2", "jobs/job_deploy_serving.yml"),
            ("jobs/job_batch_inference.yml.j2", "jobs/job_batch_inference.yml"),
            ("policies/cluster_policy_restricted.json.j2", "policies/cluster_policy_restricted.json"),
            ("policies/serving_policy_serverless.json.j2", "policies/serving_policy_serverless.json"),
            ("policies/email_notifications.json.j2", "policies/email_notifications.json"),
            ("policies/mlflow_policy.json.j2", "policies/mlflow_policy.json"),
            ("ci/github-actions.yml.j2", "ci/github-actions.yml"),
            ("docs/GOVERNANCE.md.j2", "docs/GOVERNANCE.md")
        ]
        
        env = Environment(loader=FileSystemLoader(self.template_dir))
        
        for template_file, output_file in files_to_generate:
            try:
                template = env.get_template(template_file)
                content = template.render(**template_vars)
                
                output_file_path = output_path / output_file
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file_path, 'w') as f:
                    f.write(content)
                    
            except Exception as e:
                print(f"Warning: Could not generate {output_file}: {e}")
                # Create a basic version if template fails
                self._create_basic_file(output_path / output_file, template_vars)
    
    def _create_basic_file(self, file_path: Path, template_vars: Dict[str, Any]):
        """Create a basic file when template generation fails."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.name.endswith('.py'):
            content = f'# {template_vars["project_name"]} - Generated file\n# TODO: Implement functionality\n'
        elif file_path.name.endswith('.yml') or file_path.name.endswith('.yaml'):
            content = f'# {template_vars["project_name"]} - Generated YAML\n# TODO: Configure properly\n'
        elif file_path.name.endswith('.json'):
            content = '{\n  "TODO": "Configure properly"\n}\n'
        elif file_path.name.endswith('.md'):
            content = f'# {template_vars["project_name"]}\n\nTODO: Add documentation\n'
        else:
            content = f'# {template_vars["project_name"]} - Generated file\n'
        
        with open(file_path, 'w') as f:
            f.write(content)
