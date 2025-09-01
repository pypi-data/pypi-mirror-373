# EchoGem 🎯

**Intelligent Transcript Processing and Question Answering Library**

EchoGem is a powerful Python library that transforms transcripts into intelligent, searchable knowledge bases. Using advanced AI techniques, it chunks transcripts semantically, stores them in vector databases, and provides accurate answers to questions through retrieval-augmented generation.

## ✨ Features

- **🧠 Intelligent Chunking**: Uses LLM-based semantic analysis to create meaningful transcript segments
- **🔍 Vector Search**: Pinecone-powered similarity search with intelligent scoring (similarity + entropy + recency)
- **🤖 AI-Powered Q&A**: Gemini-powered question answering grounded in retrieved chunks
- **📊 Usage Analytics**: Tracks chunk usage patterns for continuous improvement
- **💾 Persistent Storage**: Stores both chunks and Q&A pairs for future reference
- **🛠️ Easy CLI**: Simple command-line interface for quick transcript processing and questioning
- **⚙️ Configurable**: Customizable scoring weights, chunk sizes, and model parameters

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install echogem

# Or install from source
git clone https://github.com/yourusername/echogem.git
cd echogem
pip install -e .

# For graph visualization (optional)
pip install pygame
```

### Setup

1. **Get API Keys**:
   - [Google AI API Key](https://makersuite.google.com/app/apikey) for Gemini
   - [Pinecone API Key](https://app.pinecone.io/) for vector database

2. **Set Environment Variables**:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   export PINECONE_API_KEY="your-pinecone-api-key"
   ```

3. **Install Optional Dependencies**:
   ```bash
   # For better NLP analysis
   python -m spacy download en_core_web_sm
   ```

### Basic Usage

#### Process a Transcript

```bash
# Process a transcript file
py -m echogem.cli process transcript.txt

# Process and show chunk details
py -m echogem.cli process transcript.txt --show-chunks
```

#### Ask Questions

```bash
# Ask a single question
echogem ask "What is the main topic discussed?"

# Ask with detailed chunk information
echogem ask "What is the main topic discussed?" --show-chunks --show-metadata
```

#### Interactive Mode

```bash
# Start interactive questioning session
echogem interactive

#### Graph Visualization

```bash
# Launch interactive graph visualization
echogem graph

# Customize display
echogem graph --width 1600 --height 1000

# Export graph data to JSON
echogem graph --export graph_data.json
```

**Features:**
- **Interactive Nodes**: Click and drag nodes to explore
- **Multiple Layouts**: Force-directed, circular, and hierarchical layouts
- **Relationship Visualization**: Edges show similarity and relevance between chunks
- **Usage Analytics**: Color-coded nodes based on usage frequency
- **Real-time Updates**: Dynamic layout adjustments
- **Export Capability**: Save graph data for external analysis

**Controls:**
- `Space`: Cycle through layout modes
- `L`: Toggle node labels
- `E`: Toggle edge display
- `U`: Toggle usage statistics
- `Mouse`: Drag nodes, click to select
- `ESC`: Exit visualization
```

## 📚 Python API

### Basic Workflow

```python
from echogem import Processor

# Initialize processor
processor = Processor()

# Process transcript
processor.chunk_and_process("transcript.txt", output_chunks=True)

# Ask questions
result = processor.answer_question(
    "What is the main topic discussed?",
    show_chunks=True
)

print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")
print(f"Chunks used: {len(result.chunks_used)}")
```

### Advanced Usage

```python
from echogem import Processor, ChunkingOptions, QueryOptions

# Custom configuration
processor = Processor(
    chunk_index_name="my-chunks",
    pa_index_name="my-qa-pairs"
)

# Process with custom options
processor.chunk_and_process("transcript.txt")

# Query with custom parameters
chunks = processor.pick_chunks(
    "What are the key points?",
    k=10,
    entropy_weight=0.3,
    recency_weight=0.2
)

# Get similar Q&A pairs
similar_qa = processor.get_similar_qa_pairs(
    "What is the main topic?",
    k=5,
    sim_weight=0.7,
    entropy_weight=0.2,
    recency_weight=0.1
)
```

## 🏗️ Architecture

### Core Components

1. **Chunker**: LLM-based semantic transcript segmentation
2. **Vector Store**: Pinecone-powered chunk storage and retrieval
3. **Usage Cache**: CSV-based usage tracking and analytics
4. **Prompt-Answer Store**: Vector storage for Q&A pairs
5. **Processor**: Main orchestrator class

### Data Flow

```
Transcript → Chunker → Chunks → Vector Store
                                    ↓
User Question → Vector Search → Relevant Chunks → LLM → Answer
                                    ↓
                              Usage Cache ← Prompt-Answer Store
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI API key for Gemini | Yes |
| `PINECONE_API_KEY` | Pinecone API key for vector DB | Yes |

### Customization Options

- **Chunking**: Adjust `max_tokens`, `similarity_threshold`, `coherence_threshold`
- **Scoring**: Customize `entropy_weight`, `recency_weight`, `similarity_weight`
- **Retrieval**: Set `k` (number of chunks), `overfetch` multiplier
- **Index Names**: Customize Pinecone index names for different projects

## 📊 CLI Commands

| Command | Description | Options |
|---------|-------------|---------|
| `process <file>` | Process transcript file | `--show-chunks` |
| `ask <question>` | Ask a single question | `--show-chunks`, `--show-metadata` |
| `interactive` | Start interactive mode | None |
| `stats` | Show system statistics | None |
| `clear` | Clear all stored data | None |

### Interactive Mode Commands

- `help` - Show available commands
- `stats` - Display system statistics
- `clear` - Clear all data
- `chunks <k>` - Show top k chunks for a question
- `quit` / `exit` - Exit interactive mode

## 🔧 Development

### Installation for Development

```bash
git clone https://github.com/yourusername/echogem.git
cd echogem
pip install -e .[dev]
```

### Running Tests

```bash
pytest
pytest --cov=echogem
```

### Code Quality

```bash
# Format code
black echogem/
isort echogem/

# Lint code
flake8 echogem/
mypy echogem/
```

## 📁 Project Structure

```
echogem/
├── echogem/
│   ├── __init__.py          # Package exports
│   ├── models.py            # Data models
│   ├── chunker.py           # Transcript chunking
│   ├── vector_store.py      # Vector database operations
│   ├── usage_cache.py       # Usage tracking
│   ├── prompt_answer_store.py # Q&A storage
│   ├── processor.py         # Main orchestrator
│   └── cli.py              # Command-line interface
├── setup.py                 # Package configuration
├── requirements.txt         # Dependencies
├── README.md               # This file
└── examples/               # Usage examples
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for powerful language models
- [Pinecone](https://www.pinecone.io/) for vector database infrastructure
- [LangChain](https://langchain.com/) for LLM integration framework
- [Sentence Transformers](https://www.sbert.net/) for text embeddings

## 📞 Support

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/echogem/issues)
- 📖 Documentation: [GitHub Wiki](https://github.com/yourusername/echogem/wiki)

---

**Made with ❤️ for the AI community**
