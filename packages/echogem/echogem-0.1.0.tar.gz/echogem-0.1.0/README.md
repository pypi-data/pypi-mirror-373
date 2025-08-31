# EchoGem

Intelligent Transcript Processing and Question Answering Library

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/echogem.svg)](https://badge.fury.io/py/echogem)

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install echogem

# Install from source
git clone https://github.com/yourusername/echogem.git
cd echogem
pip install -e .
```

### Basic Usage

```python
from echogem import Processor

# Initialize the processor
processor = Processor()

# Process a transcript
response = processor.process_transcript("path/to/transcript.txt")

# Ask questions
result = processor.query("What is this transcript about?")
print(result.answer)
```

### Command Line Interface

```bash
# Process a transcript
echogem process transcript.txt

# Ask questions
echogem query "What is this about?"

# Visualize information flow
echogem graph

# Get usage statistics
echogem stats
```

## 📚 Features

- **Intelligent Chunking**: LLM-based semantic transcript segmentation
- **Vector Storage**: Pinecone integration for efficient retrieval
- **Question Answering**: Google Gemini-powered responses with context
- **Graph Visualization**: Interactive GUI showing information flow
- **Usage Tracking**: Monitor chunk and response utilization
- **Batch Processing**: Handle multiple documents efficiently

## 🏗️ Package Structure

```
echogem/
├── echogem/                 # Main package directory
│   ├── __init__.py         # Package initialization
│   ├── chunker.py          # Transcript chunking
│   ├── vector_store.py     # Vector database operations
│   ├── prompt_answer_store.py # Q&A pair storage
│   ├── usage_cache.py      # Usage tracking
│   ├── processor.py        # Main orchestrator
│   ├── models.py           # Data models
│   ├── cli.py              # Command-line interface
│   └── graphe.py           # Graph visualization
├── examples/                # Usage examples
├── demos/                   # Comprehensive demonstrations
├── legacy/                  # Development history
├── tests/                   # Test suite
├── setup.py                 # Package setup
├── pyproject.toml          # Project configuration
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🔧 Configuration

Set your API keys as environment variables:

```bash
export GOOGLE_API_KEY="your_gemini_api_key"
export PINECONE_API_KEY="your_pinecone_api_key"
```

## 📖 Documentation

- [Installation Guide](echogem/INSTALL.md)
- [Graph Visualization Guide](echogem/GRAPH_GUIDE.md)
- [Examples](echogem/examples/)
- [Demos](echogem/demos/)

## 🧪 Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black echogem/

# Lint code
flake8 echogem/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you have any questions or need help, please open an issue on GitHub.
