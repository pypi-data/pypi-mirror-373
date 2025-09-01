"""CLI interface for Databricks ML Bundle generator."""

import os
import click
from pathlib import Path
from .generator import ProjectGenerator


@click.command()
@click.option(
    "--name",
    "-n",
    prompt="Project name",
    help="Name of the ML project (e.g., vista-2d-segmentation)"
)
@click.option(
    "--output-dir",
    "-o",
    default=".",
    help="Output directory for the project (default: current directory)"
)
@click.option(
    "--workspace-host",
    "-w",
    prompt="Databricks workspace host",
    help="Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)"
)
@click.option(
    "--model-type",
    "-m",
    type=click.Choice(["classification", "regression", "segmentation", "nlp", "custom"]),
    default="custom",
    help="Type of ML model (default: custom)"
)
@click.option(
    "--use-gpu",
    is_flag=True,
    default=False,
    help="Configure for GPU-based training"
)
def main(name, output_dir, workspace_host, model_type, use_gpu):
    """Generate a Databricks ML platform project with governance and best practices."""
    
    click.echo(f"🚀 Creating Databricks ML project: {name}")
    
    # Create project directory
    project_path = Path(output_dir) / name
    if project_path.exists():
        if not click.confirm(f"Directory {project_path} already exists. Continue?"):
            click.echo("❌ Aborted.")
            return
    
    try:
        generator = ProjectGenerator(
            project_name=name,
            workspace_host=workspace_host,
            model_type=model_type,
            use_gpu=use_gpu
        )
        
        generator.generate(project_path)
        
        click.echo(f"✅ Successfully created project at: {project_path}")
        click.echo("\n📋 Next steps:")
        click.echo(f"1. cd {name}")
        click.echo("2. pip install -r requirements.txt")
        click.echo("3. databricks bundle validate --target dev")
        click.echo("4. databricks bundle deploy --target dev")
        
    except Exception as e:
        click.echo(f"❌ Error creating project: {e}")
        raise


if __name__ == "__main__":
    main()
