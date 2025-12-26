# Suggested Commands for MinerU

## Installation

```bash
# Install core dependencies (pipeline backend)
uv pip install -U "mineru[core]"

# Install with vLLM support (Linux)
uv pip install -U "mineru[core,vllm]"

# Install with LMDeploy support (Windows)
uv pip install -U "mineru[core,lmdeploy]"

# Install from source (editable mode)
git clone https://github.com/opendatalab/MinerU.git
cd MinerU
uv pip install -e .[core]
```

## Basic Usage (CLI)

```bash
# Parse a PDF file
mineru -p <input_file.pdf> -o <output_directory>

# Parse a directory of PDFs
mineru -p <input_directory> -o <output_directory>

# Specify backend (default: pipeline)
mineru -p input.pdf -o output -b vlm-vllm-engine

# Enable/Disable features
mineru -p input.pdf -o output --formula true --table true

# Specify language for OCR (improves accuracy)
mineru -p input.pdf -o output --lang en
mineru -p input.pdf -o output --lang ch  # Chinese (default)
```

## Model Management

```bash
# Download necessary models
mineru-models-download
```

## Development & Testing

```bash
# Run tests
pytest

# Run specific end-to-end test
pytest tests/unittest/test_e2e.py

# Format code (assuming standard python tools)
ruff check .
ruff format .
```

## API & WebUI

```bash
# Start FastAPI server
mineru-api

# Start Gradio WebUI
mineru-gradio
```
