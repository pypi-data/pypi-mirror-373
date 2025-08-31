# HTML Logger

A Python library for generating HTML logs with support for colors, file rotation, tagging, and JavaScript filters.

## Features

- ✅ Colored logs in HTML format
- ✅ Automatic file rotation
- ✅ Clean interface with integrated JavaScript filters
- ✅ Thread-safe and high performance
- ✅ Exception support with full traceback
- ✅ Flexible configuration for file size and quantity
- ✅ Tagging system for message categorization
- ✅ Advanced filtering by tags and text content

## Installation

```bash
pip install py-html-logger
```

## Basic Usage

```python
from htmllogger import log, error, report_exception

# Simple messages
log("Normal informative message")
log("Blue message", color="blue")

# Error messages
error("This is an error message")

# Log exceptions
try:
    # Your code here
    raise ValueError("Example error")
except Exception as e:
    report_exception(e)
```

## Enhanced Tagging System

The logger supports tagging messages for better organization and filtering:

```python
from htmllogger import log, info, debug, warning

# Simple tagged messages
log("User login", tag="auth")
info("Data processed", tag="processing")
debug("Variable value", tag="debug")
warning("Resource low", tag="system")

# Multiple tags
log("Security event", tag=["security", "monitoring"])
```

## Configuration

```python
from htmllogger import config

# Customize logger settings
config(
    max_files=15,           # Maximum number of log files
    max_size=5000000,       # Maximum size per file (5MB)
    main_filename="log.html", # Main file name
    log_dir="logs"          # Directory for logs
)
```

## File Structure

Logs are stored in the specified directory (default: `logs/`) with the following structure:

```
logs/
└── log.html (current file)
└── 2023-10-05_12-30-45_log.html (rotated file)
└── 2023-10-05_10-15-32_log.html (rotated file)
```

## Integrated JavaScript Filters

Generated HTML files include advanced filtering capabilities to facilitate analysis:

- Text filtering with AND/OR logic
- Tag-based filtering
- Time period filtering
- Real-time highlighting of matched terms
- Preserved original log view

## Complete Example

```python
from htmllogger import log, info, debug, warning, error, report_exception, config

# Configure logger
config(
    max_files=10,
    max_size=2000000,  # 2MB
    log_dir="my_logs"
)

# Log with different tags and levels
log("Application started", tag="system", color="green")
info("Loading configuration", tag="config")
debug("Initializing modules", tag="debug")

for i in range(100):
    if i % 10 == 0:
        log(f"Checkpoint {i}", tag="checkpoint")
    info(f"Processing item {i}", tag="processing")

try:
    # Code that might raise an error
    result = 10 / 0
except Exception as e:
    error("Division by zero detected")
    report_exception(e)

log("Application finished", tag="system", color="green")
```

## API Reference

### log(message, color="white", tag=None)
Logs a message with optional color and tag(s).

### info(message, color="white", tag=None)
Logs an informational message.

### debug(message, color="white", tag=None)
Logs a debug message.

### warning(message, color="gold", tag=None)
Logs a warning message.

### error(message)
Logs an error message (in red).

### report_exception(exc, timeout=None)
Logs an exception with its full traceback.

### config(**kwargs)
Configures logger options:
- `max_files`: Maximum number of files to maintain
- `max_size`: Maximum size in bytes per file
- `main_filename`: Main log file name
- `log_dir`: Directory where logs will be stored

### flush()
Processes all pending messages before termination.

## Development

To contribute to the project:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

If you encounter issues or have questions:

1. Check the [documentation](https://github.com/rphpires/py-html-logger)
2. Open an [issue](https://github.com/rphpires/py-html-logger/issues)
3. Contact: rphspires@gmail.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Developed by Raphael Pires
- Inspired by the need for better log visualization and analysis tools