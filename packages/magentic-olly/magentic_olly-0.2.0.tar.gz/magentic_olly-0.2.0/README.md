# Magentic Instrumentation

A package for magentic ai observability systems.

## Installation

```bash
pip install magentic-olly
```

## Usage

```python
import magentic_olly
export_params = magentic_olly.HttpExportParams(
    endpoint='https://{DOMAIN}/v1/traces',
    token='{TOKEN}'  
)
magentic_olly.set_http_export_params(export_params)
```

