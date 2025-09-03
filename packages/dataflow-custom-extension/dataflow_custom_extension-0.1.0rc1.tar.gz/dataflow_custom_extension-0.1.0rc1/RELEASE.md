# Making package of dataflow-custom-extension

### Python package

This extension can be distributed as Python packages. All of the Python
packaging instructions are in the `pyproject.toml` file to wrap your extension in a
Python package. Before generating a package, you first need to install some tools:

```
dependencies for the package:
  - python >=3.10,<3.11.0a0
  - jupyterlab >=4.0.0,<5
  - nodejs >=18,<19
  - pip
  - wheel
```

```bash
pip install build hatch
```

To create a Python source package (`.tar.gz`) and the binary package (`.whl`) in the `dist/` directory, do:

```bash
python -m build
```