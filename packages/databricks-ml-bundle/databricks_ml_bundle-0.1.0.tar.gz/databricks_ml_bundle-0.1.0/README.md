# Databricks ML Bundle CLI

A CLI tool to generate Databricks ML platform project structures with governance and best practices.

## Installation

```bash
pip install databricks-ml-bundle
```

## Usage

Generate a new ML project:

```bash
databricks-ml-init --name my-ml-project --workspace-host https://your-workspace.cloud.databricks.com --model-type segmentation --use-gpu
```

Or use the short command:

```bash
dml-init -n my-ml-project -w https://your-workspace.cloud.databricks.com -m classification
```

### Options

- `--name, -n`: Project name (required)
- `--output-dir, -o`: Output directory (default: current directory)
- `--workspace-host, -w`: Databricks workspace URL (required)
- `--model-type, -m`: Model type - classification, regression, segmentation, nlp, custom (default: custom)
- `--use-gpu`: Enable GPU configuration for training

## Generated Structure

The CLI generates a complete ML platform project with:

- **Multi-environment support** (dev/stg/prod)
- **Unity Catalog integration**
- **MLflow experiment tracking**
- **Quality gates and approvals**
- **CI/CD pipeline with GitHub Actions**
- **Cluster policies and security**
- **Modular Python package structure**

## Example

```bash
# Generate a computer vision project
databricks-ml-init \
  --name vista-segmentation \
  --workspace-host https://my-workspace.cloud.databricks.com \
  --model-type segmentation \
  --use-gpu

# Navigate to project
cd vista-segmentation

# Install dependencies
pip install -r requirements.txt

# Deploy to Databricks
databricks bundle validate --target dev
databricks bundle deploy --target dev
```

## Features

- ✅ **Governance-first**: Built-in security, permissions, and audit trails
- ✅ **Multi-environment**: Separate dev/staging/production environments
- ✅ **Model-specific**: Templates optimized for different ML use cases
- ✅ **Production-ready**: Includes serving endpoints, monitoring, and CI/CD
- ✅ **Unity Catalog**: Full integration with Databricks governance platform

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/databricks-ml-bundle-cli
cd databricks-ml-bundle-cli

# Install with Poetry
poetry install

# Run locally
poetry run databricks-ml-init --help
```

## Publishing to PyPI

```bash
# Build package
poetry build

# Publish to PyPI
poetry publish
```

## License

MIT License
