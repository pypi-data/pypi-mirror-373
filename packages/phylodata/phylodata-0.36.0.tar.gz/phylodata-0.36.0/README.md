# 🧬 PhyloData CLI

## 📥 Installation

### Using pip

```bash
pip install phylodata
```

## 📖 Usage

```bash
# Process an experiment before uploading it to PhyloData
# (starts an interactive process in a web browser)
phylodata process

# Validate if a given JSON file contains valid PhyloData metadata
phylodata validate path/to/metadata.json

# Print the JSON schema for valid PhyloData metadata files
# (Use this to debug the JSON file, e.g. using https://www.jsonschemavalidator.net/)
phylodata schema
```


## For Developers

## 🔧 Tech Stack

- **Python**: Requires Python 3.10+
- **Streamlit**: Web interface for data processing
- **UV**: Modern Python package manager and installer (no venv required)
- **Just**: Command runner used for development workflows

### 📋 Prerequisites

- Python 3.10+
- [UV](https://github.com/astral-sh/uv) for dependency management
- [Just](https://github.com/casey/just) for running commands

### 🛠️ Development Commands

Run these commands with `just`:

```bash
just test    # Run pytest tests with UV
just check   # Run ruff linter with auto-fix
just format  # Format code with ruff
```

In order to run a script using the dependencies, just preface it with `uv python`:

```bash
uv python my_script.py
```
