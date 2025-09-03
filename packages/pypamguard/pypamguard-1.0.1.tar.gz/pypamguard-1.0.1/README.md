![PyPI - Version](https://img.shields.io/pypi/v/pypamguard?label=pypi)
![PyPI - Status](https://img.shields.io/pypi/status/pypamguard)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pypamguard)
![GitHub contributors](https://img.shields.io/github/contributors/PAMGuard/pypamguard)
![GitHub License](https://img.shields.io/github/license/PAMGuard/pypamguard)
![GitHub last commit](https://img.shields.io/github/last-commit/PAMGuard/pypamguard)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/PAMGuard/pypamguard/tests.yml?label=tests)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/PAMGuard/pypamguard/documentation.yml?label=docs)
![GitHub Tag](https://img.shields.io/github/v/tag/PAMGuard/pypamguard?label="github-version")
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16789563.svg)](https://doi.org/10.5281/zenodo.16789563)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pypamguard)

pypamguard is a package for processing PAMGuard binary file outputs in Python.

* **PyPI**: https://pypi.org/project/pypamguard/
* **GitHub**: https://github.com/PAMGuard/pypamguard
* **Documentation**: https://www.pamguard.org/pypamguard/
* **Website**: https://www.pamguard.org/
* **Zenodo**: https://doi.org/10.5281/zenodo.16789563

## Installation

```bash
pip install pypamguard
```

## Getting Started

Example of loading in a simple PAMGuard data file into Python.

```python
import pypamguard
df = pypamguard.load_pamguard_binary_file('path/to/data/file.pgdf')
```

Then, for example, you can print out the file header like so.

```python
print(df.file_info.file_header) # File header
print(df.file_info.file_header.version) # File version
```

Modules also have a `file_info.module_header`, `file_info.module_footer`, `file_info.file_footer`, and most importantly `data` and `background`. 

```python
print("File length", len(df.data)) # Number of module data chunks
first_obj = df.data[0] # First module data chunk
for chunk in df.data: # Looping through the data
    print(chunk.identifier)
```

For more information, see the [documentation](https://www.pamguard.org/pypamguard/).

## Bugs/Requests

Please use the [Github issue tracker](https://github.com/PAMGuard/pypamguard/issues) to submit bugs or feature requests.

## License

This software is distributed under the terms of the MIT license. pypamguard is free and open source. 

If you use this code, please cite it as listed on Zenodo: https://doi.org/10.5281/zenodo.16789563
e.g. James Sullivan. (2025). PAMGuard/pypamguard: Version 1.0.0 (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.16789564

## Contributing

Check [CONTRIBUTING.md](CONTRIBUTING.md) to get started.
