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
- **Rich Example Database**: Comprehensive collection of text-to-command examples (available with repo)
- **Safe Command Generation**: Focuses on standard, secure and safe bash commands

## 🏗️ Architecture

### Core Components

```
terminal-buddy/
├── src/terminal_buddy/
│ ├── main.py # CLI interface and server logic
│ └── utils/
│ ├── llm_functions.py # LLM integration with Ollama
│ ├── config.py # Configuration management
│ ├── prompts.py # System prompts and templates
│ └── example_selection.py # Vector-based Example Selection
├── data/examples/
│ └── text_2_command_examples.json # Training examples (included in the repo)
└── tests/ # Test suite
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

### Step 1 - Install Package

#### Using pip installer (Recommended)

```bash
pip install terminal-buddy
```

#### Using Poetry (Build Yourself)

```bash
# Clone the repository
git clone <repository-url>
cd terminal-buddy

# Install dependencies
poetry install

# Install the package
poetry install --with dev
```

### Step 2 - Setup Ollama Models
```bash
# Pull required models
ollama pull qwen3:0.6b
ollama pull nomic-embed-text
```

## 🚀 Usage

TBuddy provides a CLI with multiple commands grouped under query, server, and config.

### Query Commands
##### Generate a command directly

`tb query "list all files in current directory"`

### Server Management

```bash
# Start the server in background mode (default)
tb server up

# Start the server in foreground mode
tb server up --no-daemonize

# Stop the server
tb server down

# Check server status
tb server status
```
### Configuration Management
```
# Show current configuration
tb config show

# Update LLM model
tb config set-llm-model qwen3:0.6b

# Update embeddings model
tb config set-embeddings-model nomic-embed-text

# Update examples file path
tb config set-examples-path ./data/examples/text_2_command_examples.json
```