# ss-utils-logging

A Python logging utility package with orjson serialization and advanced configuration features.

## Features

- **ORJSON Serialization**: High-performance JSON logging with orjson
- **YAML Configuration**: Easy logging setup using YAML configuration files
- **Merging Logger Adapter**: Advanced adapter that properly merges extra fields (fixes Python <3.13 limitation)
- **Console & JSON Formatters**: Flexible formatting options for different output needs
- **Config File Generation**: Automatically generate example configuration files

## Installation

```bash
uv add ss-utils-logging
```

## Quick Start

```bash
# [one-time] Generate example configuration files in `config/` folder
# This creates example YAML configuration files (logging.yaml and logging.prod.yaml) that you can customize for your needs.
uv run ss-utils-logging config --no-overwrite
```

```python
from ss_utils_logging import configure_logging, get_logger, generate_config_files

# Configure logging with YAML file
configure_logging("config/logging.yaml")

# Set up a logger with extra context
logger = get_logger(__name__, extra={"service": "my-app", "version": "1.0.0"})

# Log with additional context (optional)
logger.info("Processing request", user_id=123, action="login")
```

## Key Components

### MergingLoggerAdapter
Fixes the Python <3.13 limitation where LoggerAdapter doesn't properly merge extra fields from both the adapter and individual log calls.

### Formatters
- `ConsoleFormatter`: Human-readable console output
- `ORJSONFormatter`: High-performance JSON output using orjson

### Configuration Management
- `configure_logging()`: Set up logging from YAML configuration
- `generate_config_files()`: Create example configuration files
- `get_logger()`: Get logger instances with optional extra context


## Test notes

- Tested only on macos
