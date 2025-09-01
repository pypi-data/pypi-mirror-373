# Sushi Train

Like a sushi train, you can grab a utility if you want it or leave it if you don't.

Sushi Train is a small Python utility library geared towards data engineering tasks. It's designed to be easy to use, minimal, and ready for publishing to PyPI as a community-friendly package. In short, these are a collection of utility functions that I tend to use frequently in my own data workflows. 

## Goals

- Provide pragmatic, well-tested helper functions for everyday data engineering workflows.
- Favor clear, composable utilities over heavy frameworks.
- Pythonic function naming conventions for clear, intuitive usage at the expense of brevity.

## Features

- Duckdb (in-memory currently) & Ducklake connection and attachment functions
- Query Param helper for constructing dynamic URLs from .env base URLs
- Updating Ducklake Catalog from MinIO bucket files

## Installation

Install from PyPI:

```bash
pip install sushi-train
```

## Example

Import the package and use the small focused utilities. The library exposes short, composable functions so you can grab them off the sushi train and into data pipelines:

```python
from sushi_train import add_query_params_to_url

url = "https://example.com/api"
params = {"roll": "spicy-tuna",
          "edamame": "true"}
full_url = add_query_params_to_url(url, params)
```

## Contributing

Contributions, issues, and suggestions are welcome. This is my first open-source project, so I appreciate any feedback or contributions.

This is intended to be a community-first package — friendly, minimal, and re-useable. It is not intended to be a comprehensive solution for all data engineering tasks. 

## License

This project is available under the terms of the MIT License — see the `LICENSE` file.

## Contact

Author: Michael Galo — contributions and feedback welcome via GitHub issues.


