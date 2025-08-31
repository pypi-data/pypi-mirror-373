# TBuddy - Terminal Assistant Powered by On-Device LLM

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-managed-orange.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)](LICENSE)

TBuddy is an intelligent terminal assistant that converts natural language queries into bash commands using on-device (<1B params) Large Language Models (LLMs). It provides both a command-line interface and a daemon service for seamless terminal command generation.

## 🚀 Features

- **Natural Language to Bash Commands**: Convert plain English descriptions into executable bash commands
- **On-Device LLM Integration**: Uses Ollama with extremely small sub 1Billion parameter local models for balancing privacy, speed, memory usage and accuracy
- **Semantic Example Selection**: Leverages vector embeddings to find relevant command examples from a pre-curated list
- **Dual Operation Modes**: 
  - One-off command generation
  - Background daemon service for persistent, faster availability
- **Rich Example Database**: Comprehensive collection of text-to-command examples (available per request)
- **Safe Command Generation**: Focuses on standard, secure and safe bash commands

## 🏗️ Architecture

### Core Components

```
terminal-buddy/
├── src/terminal_buddy/
│   ├── main.py              # CLI interface and server logic
│   └── utils/
│       ├── llm_functions.py     # LLM integration with Ollama
│       ├── config.py            # Configuration management
│       ├── prompts.py           # System prompts and templates
│       ├── example_selection.py # Vector-based example retrieval
│       └── examples.json        # Command examples database
├── data/examples/
│   └── text_2_command_examples.json  # Training examples (not included in the repo, but this is where you'd place your own)
└── tests/                    # Test suite
```

### Key Technologies

- **Ollama**: Local LLM inference engine
- **LangChain**: Vector embeddings and example selection
- **ChromaDB**: Vector database for semantic search
- **Typer**: Modern CLI framework
- **Pydantic**: Configuration and data validation

## 📋 Prerequisites

- Python 3.12 or higher
- [Ollama](https://ollama.ai/) installed and running
- Required Ollama models:
  - `qwen3:0.6b` (for command generation)
  - `nomic-embed-text` (for embeddings)

## 🛠️ Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd terminal-buddy

# Install dependencies
poetry install

# Install the package
poetry install --with dev
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd terminal-buddy

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Setup Ollama Models

```bash
# Pull required models
ollama pull qwen3:0.6b
ollama pull nomic-embed-text
```

## 🚀 Usage

### Command Line Interface

TBuddy provides a simple CLI for generating commands:

```bash
# Basic usage
tb "list all files in current directory"

# Using the full command
tb query "show me disk usage"

# Start background service
tb serve
```

### Examples

```bash
# File operations
tb "create a new directory called projects"
# Output: mkdir projects

tb "list all hidden files"
# Output: ls -a

# System information
tb "check disk space"
# Output: df -h

tb "show running processes"
# Output: ps aux

# Text processing
tb "find all .txt files"
# Output: find . -name "*.txt"

tb "search for 'error' in log files"
# Output: grep -r "error" *.log
```

### Daemon Mode

For persistent availability, run TBuddy as a background service:

```bash
# Start the daemon
tb serve

# In another terminal, send queries
tb "check memory usage"
```

The daemon runs on `127.0.0.1:65432` and automatically handles multiple concurrent requests.

## ⚙️ Configuration

Configuration is managed through the `Config` class in `src/terminal_buddy/utils/config.py`:

```python
class Config(BaseModel):
    OLLAMA_MODEL_NAME: str = Field(default="qwen3:0.6b")
    OLLAMA_EMBEDDINGS_MODEL_NAME: str = Field(default="nomic-embed-text")
    EXAMPLES_JSON_PATH: str = Field(default="path/to/examples.json")
```

## 🔧 Development

### Project Structure

- **`main.py`**: Entry point with CLI commands and server logic
- **`utils/llm_functions.py`**: Core LLM integration using Ollama
- **`utils/example_selection.py`**: Vector-based example retrieval using LangChain
- **`utils/prompts.py`**: System prompts for command generation
- **`data/examples/`**: Training data with text-to-command mappings

### Adding New Examples

To improve command generation, add new examples to `data/examples/text_2_command_examples.json`:

```json
{
    "user_query": "Your natural language description",
    "command": "corresponding bash command"
}
```

### Running Tests

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=terminal_buddy
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Use type hints for all functions

## 📊 Performance

- **Response Time**: ~1-3 seconds for command generation
- **Memory Usage**: ~2-4GB RAM (depending on model size)
- **Accuracy**: High accuracy for common terminal operations
- **Safety**: Focuses on standard, safe bash commands

## 🔒 Security

- **Local Processing**: All LLM operations run locally via Ollama
- **No Data Transmission**: No queries or responses are sent to external services
- **Safe Commands**: System prompts emphasize safe, standard bash commands
- **Input Validation**: All inputs are validated before processing

## 📝 License

This project is licensed under the GNU General Public License v3 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [LangChain](https://langchain.com/) for vector operations and example selection
- [Typer](https://typer.tiangolo.com/) for the CLI framework
- [Pydantic](https://pydantic.dev/) for data validation

## 📞 Support

For questions, issues, or contributions:

- Open an issue on GitHub
- Check the [documentation](docs/)
- Review existing examples in `data/examples/`

---

**Made with ❤️ for the terminal community**
