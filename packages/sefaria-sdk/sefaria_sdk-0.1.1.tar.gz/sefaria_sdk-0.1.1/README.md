# Unofficial Sefaria Python SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, modernized Python SDK for interacting with the [Sefaria API](https://www.sefaria.org/developers), featuring robust client architecture, extensive examples, and full compatibility with current API endpoints.

## ✨ Features

### 🚀 Modern API Support
- **Search**: POST `/search-wrapper` endpoint with advanced query capabilities
- **Texts**: v3 API with comprehensive parameter support and language options
- **Related Content**: `/related/{tref}` endpoint for content relationships
- **Languages**: `/texts/translations` for available translations discovery

### 💪 Robust Client Architecture
- Connection pooling with `requests.Session()`
- Exponential backoff retry strategy for reliability
- Configurable timeouts and headers
- Comprehensive error handling and logging

### ⚡ Async Support
- High-performance async client for bulk operations
- Concurrent text fetching capabilities
- Proper session management and resource cleanup

### 📊 Data Export Tools
- **JSON**: Full text structure preservation
- **CSV**: Verse-by-verse data export
- **PDF**: Clean English text generation
- **HTML**: Tag removal and formatting

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/rbrtjns90/unofficial_sefaria_python_sdk.git
cd unofficial_sefaria_python_sdk

# Install the SDK
pip install -e .

# Install example dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

```python
from sefaria_sdk import SefariaClient

# Initialize client
client = SefariaClient()

# Search for texts
results = client.search("charity", limit=5)
print(f"Found {results['hits']['total']} results")

# Get text with specific version
text = client.get_text("Genesis 1:1", lang="en")
print(text['versions'][0]['text'])

# Get related content
related = client.get_related("Genesis 1:1")
print(f"Found {len(related['links'])} related texts")

# Get available languages
languages = client.get_languages()
print(f"Available languages: {list(languages.keys())}")
```

## 📚 Examples

All examples are **tested and working** with the current Sefaria API:

### Command Line Interface
```bash
# Search for texts
python examples/04_cli/sefaria_cli.py search "charity" -n 5

# Get specific text
python examples/04_cli/sefaria_cli.py get-text "Psalms 23:1"

# View today's calendar
python examples/04_cli/sefaria_cli.py today
```

### Web Application
```bash
# Run Flask Torah portion viewer
python examples/02_web_app/flask_torah_app.py
# Visit http://localhost:5000
```

### Async Text Processing
```python
# Fetch multiple texts concurrently
python examples/05_async/async_text_fetcher_fixed.py
```

### Data Export
```python
# Export texts to multiple formats
python examples/06_data_export/text_exporter.py
# Generates JSON, CSV, and PDF files
```

## 🔧 API Methods

### Core Methods
- `get_text(tref, **kwargs)` - Retrieve text with full v3 API support
- `search(query, **kwargs)` - Advanced search with highlighting
- `get_related(tref)` - Find related texts and commentaries
- `get_languages()` - Available translation languages
- `get_calendar()` - Jewish calendar information

### Advanced Features
- Automatic retry with exponential backoff
- Session-based connection pooling
- Configurable timeouts and headers
- Comprehensive error handling

## 📁 Project Structure

```
unofficial_sefaria_python_sdk/
├── sefaria_sdk/
│   ├── client.py          # Main SDK client
│   ├── text_processing.py # Text utilities
│   └── __init__.py
├── examples/
│   ├── 01_basic_usage/    # Basic API usage
│   ├── 02_web_app/        # Flask web application
│   ├── 03_research/       # Text analysis tools
│   ├── 04_cli/            # Command line interface
│   ├── 05_async/          # Async text fetching
│   ├── 06_data_export/    # Multi-format export
│   └── 06_improved_api/   # Modern API showcase
├── requirements.txt
├── setup.py
└── README.md
```

## 🔄 Recent Updates

### API Compatibility (August 2024)
- ✅ Updated search to use POST `/search-wrapper`
- ✅ Fixed text retrieval for current API response structure
- ✅ Corrected language parameter handling
- ✅ Enhanced error handling and retries

### Example Fixes
- ✅ **CLI Search**: Now displays actual results instead of "N/A"
- ✅ **Async Fetcher**: Retrieves real English text content
- ✅ **Text Exporter**: Proper API response parsing for all formats
- ✅ **Modern Demo**: Working search and related content features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Format code
black sefaria_sdk/ examples/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This is an unofficial SDK and is not affiliated with or endorsed by Sefaria. Please respect Sefaria's API usage guidelines and terms of service.

## 🔗 Links

- [Sefaria Website](https://www.sefaria.org)
- [Sefaria API Documentation](https://www.sefaria.org/developers)
- [Report Issues](https://github.com/yourusername/unofficial_sefaria_python_sdk/issues)

---

**Made with ❤️ for the Jewish learning community**
