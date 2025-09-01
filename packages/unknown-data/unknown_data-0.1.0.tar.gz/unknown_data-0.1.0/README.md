# Unknown Data - Digital Forensics Data Processing Library

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/unknown-data.svg)](https://badge.fury.io/py/unknown-data)

A comprehensive Python library for parsing and processing digital forensics data artifacts. This library provides standardized interfaces for handling various types of forensic data including browser artifacts, deleted files, link files, messenger data, prefetch files, and USB device information.

## Features

- **Multi-format Support**: Handle browser data, deleted files, link files, messenger data, prefetch files, and USB artifacts
- **Standardized Processing**: Consistent interface for all data types
- **Flexible Data Sources**: Support for local files and cloud storage (S3)
- **DataFrame Output**: All processed data is converted to pandas DataFrames for easy analysis
- **Comprehensive Logging**: Built-in logging for debugging and monitoring
- **Type Safety**: Full type hints support for better development experience

## Installation

```bash
pip install unknown-data
```

## Quick Start

### Local File Processing

```python
from unknown_data import Category, Encoder, DataLoader, DataSaver

# Load data from local file
loader = DataLoader()
data = loader.local_data_load(Category.BROWSER, "./data/browser_results.json")

# Process the data
encoder = Encoder()
browser_encoder = encoder.convert_data(data, Category.BROWSER)

# Get processed results
results = browser_encoder.get_result_dfs()

# Save results to CSV files
saver = DataSaver("./output/path")
saver.save_all(results)
```

### AWS S3 Integration

```python
from unknown_data import Category, DataLoader

# Configure S3 access with task_id structure
s3_config = {
    'bucket': 'your-forensic-data-bucket',
    'task_id': '550e8400-e29b-41d4-a716-446655440000',  # UUID format
    'region': 'us-west-2',  # optional
    'profile': 'forensics'  # optional AWS profile
}

# Load data from S3
# S3 path will be: {bucket}/{task_id}/browser_data.json
loader = DataLoader()
browser_data = loader.s3_data_load(Category.BROWSER, s3_config)

# The data is automatically loaded and ready for processing
print(f"Loaded {len(browser_data.get('browser_data', []))} browser records")

# Load different types of data from the same task
deleted_data = loader.s3_data_load(Category.DELETED, s3_config)
usb_data = loader.s3_data_load(Category.USB, s3_config)
```

## Supported Data Types

### Browser Artifacts
- History (URLs, visits, downloads)
- Cookies
- Login data
- Web data

### Deleted Files
- MFT deleted files
- Recycle bin files
- Collection metadata

### Other Artifacts
- Link (LNK) files
- Messenger data
- Prefetch files
- USB device information

## Data Structure

The library expects JSON data in specific formats for each category. Here's an example for browser data:

```python
browser_data = {
    "collected_files": [...],
    "collection_time": "2023-01-01T10:00:00",
    "detailed_files": [...],
    "discovered_profiles": [...],
    "statistics": {...},
    "temp_directory": "/tmp/extraction"
}
```

## Advanced Usage

### Custom Data Processing

```python
from unknown_data import BrowserDataEncoder

# Create specific encoder
encoder = BrowserDataEncoder()

# Process data
encoder.convert_data(your_data)

# Access specific results
chrome_data = encoder.chrome_data
edge_data = encoder.edge_data
```

### Cloud Storage Support

```python
# Load from S3 (requires boto3 configuration)
s3_config = {
    "bucket": "your-bucket",
    "key": "path/to/data.json"
}
data = loader.s3_data_load(Category.BROWSER, s3_config)
```

## Requirements

- Python 3.8+
- pandas >= 1.3.0
- numpy
- jsonschema
- boto3 (for S3 support)

## AWS S3 Configuration

### Setting up AWS Credentials

Before using S3 features, configure your AWS credentials using one of these methods:

#### 1. AWS CLI Configuration
```bash
aws configure
```

#### 2. Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

#### 3. AWS Profile
```python
s3_config = {
    'bucket': 'your-bucket',
    'key': 'path/to/file.json',
    'profile': 'your-aws-profile'
}
```

### S3 Data Structure

Your S3 bucket should organize forensic data using the task_id structure:

```
your-forensic-bucket/
├── 550e8400-e29b-41d4-a716-446655440000/  # task_id (UUID)
│   ├── browser_data.json
│   ├── deleted_data.json
│   ├── usb_data.json
│   ├── messenger_data.json
│   ├── prefetch_data.json
│   └── lnk_data.json
├── 6ba7b810-9dad-11d1-80b4-00c04fd430c8/  # another task_id
│   ├── browser_data.json
│   └── ...
└── ...
```

Each `{category.value}_data.json` file contains the forensic data for that specific category. The library automatically constructs the S3 key as `{task_id}/{category.value}_data.json`.
│   ├── case001/
│   │   ├── browser_data.json
│   │   ├── deleted_data.json
│   │   └── usb_data.json
│   └── case002/
│       └── messenger_data.json
└── archive/
    └── old_cases/
```

### Error Handling

The library provides comprehensive error handling for S3 operations:

```python
from unknown_data import DataLoader, Category
from botocore.exceptions import NoCredentialsError, ClientError

try:
    loader = DataLoader()
    data = loader.s3_data_load(Category.BROWSER, s3_config)
except NoCredentialsError:
    print("AWS credentials not found. Please configure your credentials.")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ClientError as e:
    print(f"AWS error: {e}")
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/daehan00/unknown_parsing_module.git
cd unknown_parsing_module

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black mypy
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=parsing_module

# Run specific test file
pytest tests/test_integration.py -v
```

## Changelog

### Version 0.1.0
- Initial release
- Support for browser artifacts processing
- Support for deleted files analysis
- Basic encoder framework
- Local and S3 data loading
- Comprehensive test coverage

## Contact

- GitHub: [@daehan00](https://github.com/daehan00)
- Repository: [unknown_parsing_module](https://github.com/daehan00/unknown_parsing_module)

