# Opencloudtool Python Library

A tool to hide the complexity of the cloud, now available as a Python library.
This library allows you to deploy services directly from your Python scripts.The core of this library is written in Rust
for high performance and reliability.

## Installation

You can install the library from PyPI using `pip`

```bash
pip install opencloudtool

```

## Basic Usage

To use the library, you need an `oct.toml` configuration file in your project directory.
The library provides `deploy` and `destroy` functions to manage your stack.

Example `deploy.py`

```python
import opencloudtool as oct

# The path to the project directory containing oct.toml
project_path = "./my-app"

oct.deploy(path=project_path)
```

To destroy infrastructure:

```python
oct.destroy(path=project_path)
```

Main repo [opencloudtool](https://github.com/opencloudtool/opencloudtool)
