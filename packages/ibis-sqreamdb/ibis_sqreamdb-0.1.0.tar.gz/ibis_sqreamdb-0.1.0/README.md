# Ibis SQreamDB Backend

This package provides a backend for the [Ibis framework](https://ibis-project.org/) that connects to [SQreamDB](https://sqream.com/).

## Installation

From within the `ibis-framework-sqream` directory, run:
```bash
# It's recommended to uninstall any previous versions first
pip uninstall -y ibis-sqreamdb

# Install in editable mode
pip install -e .
```

## Usage

```python
import ibis

# Example connection
con = ibis.sqream.connect(
    host="127.0.0.1",
    port=5000,
    database="master",
    user="sqream",
    password="sqream",
)

version = con.version
print(f"Connected to SQreamDB version: {version}")
```
