# 🎯 Results Parser Agent

A powerful, intelligent agent for extracting metrics from benchmark result files using LangGraph and AI-powered parsing. The agent automatically analyzes unstructured result files and extracts specific metrics into structured JSON output with high accuracy.

## 🚀 Features

- **🤖 AI-Powered Parsing**: Uses advanced LLMs (OpenAI GPT-4, GROQ, Anthropic, Google Gemini, Ollama) for intelligent metric extraction
- **📁 Flexible Input**: Process single files or entire directories of result files
- **🎯 Workload-Specific Tools**: Dedicated extraction scripts for different benchmark types (FIO, Redis, Nginx, MariaDB/MySQL TPC-H & TPC-C)
- **⚙️ MongoDB Integration**: External API-backed workload registry for scalable management
- **📊 Structured Output**: Direct output in Pydantic schemas for easy integration
- **🛠️ Professional CLI**: Comprehensive Typer-based command-line interface with subcommands
- **🔧 Python API**: Easy integration into existing Python applications
- **🔄 Error Recovery**: Robust error handling and retry mechanisms
- **📦 Git-based Scripts**: Secure, efficient script distribution and caching system
- **🔒 Enterprise Security**: SSH authentication, environment variables, and secure defaults

## 📦 Installation

### Quick Install (Recommended)

```bash
pip install result-parser-agent
```

### Development Install

```bash
# Clone the repository
git clone https://github.com/Infobellit-Solutions-Pvt-Ltd/result-parser-agent.git
cd result-parser-agent

# Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv pip install -e .

# Or install with pip
pip install -e .
```

## 📋 Configuration

### Environment Variables

Create a `.env` file in your project directory:

```bash
# API Keys - Set only the one you need
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# MongoDB Registry API
REGISTRY_API_BASE_URL=http://your-mongodb-api.com/api/v1
REGISTRY_API_KEY=your_api_key_here

# Script Management
SCRIPTS_BASE_URL=git@github.com:your-org/parser-scripts.git
SCRIPTS_CACHE_DIR=~/.cache/result-parser/scripts
SCRIPTS_CACHE_TTL=3600

# Optional: Override default LLM settings
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
```

## 🎯 Quick Start

### 1. Set up your API key

```bash
# For OpenAI (default - recommended)
export OPENAI_API_KEY="your-openai-api-key-here"

# For GROQ
export GROQ_API_KEY="your-groq-api-key-here"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# For Google Gemini
export GOOGLE_API_KEY="your-google-api-key-here"
```

### 2. Use the CLI

The CLI now supports multiple subcommands for different operations:

#### Parse Results
```bash
# Parse all files in a directory with workload-specific tools
result-parser parse ./benchmark_results --workload fio

# Parse with specific metrics
result-parser parse ./benchmark_results --workload redis --metrics "SET(requests/sec),GET(requests/sec)"

# Parse a single file
result-parser parse ./results.txt --workload nginx --metrics "Requests/sec,Transfer/sec"

# Custom output file
result-parser parse ./results/ --workload mariadb_tpch --output my_results.json

# Verbose output
result-parser parse ./results/ --workload mysql_tpcc --verbose
```

#### Manage Registry
```bash
# Show registry information and script cache status
result-parser registry

# Add new workload
result-parser add-workload fio --metrics "random_read_iops,random_write_iops" --description "Storage performance benchmark"

# Update existing workload
result-parser update-workload redis --metrics "SET(requests/sec),GET(requests/sec),DEL(requests/sec)"

# Show workload details
result-parser show-workload nginx
```

#### Manage Script Cache
```bash
# Show cache information
result-parser cache info

# Clear specific workload cache
result-parser cache clear fio

# Clear all caches
result-parser cache clear-all
```

### 3. Use the Python API

```python
from result_parser_agent import ResultsParserAgent, settings
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Get default configuration
config = settings

# Initialize agent
agent = ResultsParserAgent(config)

# Parse results with workload-specific tools
results = await agent.parse_results(
    input_path="./benchmark_results",
    workload="fio",
    metrics=["random_read_iops", "random_write_iops"]
)

# Output structured data
print(results.json(indent=2))
```

## 🔧 Supported Workloads

The agent supports various benchmark workloads with dedicated extraction scripts:

| Workload | Description | Example Metrics |
|----------|-------------|-----------------|
| **FIO** | Storage performance benchmark | `random_read_iops`, `random_write_iops`, `sequential_read_mbps` |
| **Redis** | In-memory database benchmark | `SET(requests/sec)`, `GET(requests/sec)` |
| **Nginx** | Web server performance | `Requests/sec`, `Transfer/sec` |
| **MariaDB TPC-H** | Database TPC-H benchmark | `Power@Size`, `Throughput@Size`, `QphH@Size` |
| **MySQL TPC-H** | Database TPC-H benchmark | `Power@Size`, `Throughput@Size`, `QphH@Size` |
| **MariaDB TPC-C** | Database TPC-C benchmark | `tpmC`, `tpmTOTAL` |
| **MySQL TPC-C** | Database TPC-C benchmark | `tpmC`, `tpmTOTAL` |

## 🏗️ Architecture

The agent uses a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Parser Agent    │    │  Tool Registry  │
│  (Typer CLI)    │◄──►│  (LangGraph)     │◄──►│  (Workloads)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Configuration  │    │   LLM Provider   │    │ Script Download │
│  (Pydantic)     │    │  (OpenAI/GROQ)   │    │   (Git SSH)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ MongoDB Registry│    │  Result Output   │    │  Script Cache   │
│     API         │    │   (JSON)         │    │   (Local)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ CLI Commands Reference

### `parse` - Parse Benchmark Results
```bash
result-parser parse <input_path> [OPTIONS]

Arguments:
  input_path              Path to results file or directory

Options:
  --workload TEXT         Workload type (fio, redis, nginx, mariadb_tpch, etc.)
  --metrics TEXT          Comma-separated list of metrics to extract
  --output TEXT           Output file path [default: results.json]
  --verbose               Enable verbose logging
  --help                  Show this message and exit
```

### `registry` - Show Registry Information
```bash
result-parser registry

Shows:
- Registry source (API + Git Scripts)
- Available workloads
- Script cache status
- Cache directory information
```

### `cache` - Manage Script Cache
```bash
result-parser cache <action> [workload]

Actions:
  info                    Show cache information
  clear [workload]        Clear specific or all caches
  clear-all               Clear all caches
```

### `add-workload` - Add New Workload
```bash
result-parser add-workload <name> [OPTIONS]

Arguments:
  name                    Workload name

Options:
  --metrics TEXT          Comma-separated list of metrics [required]
  --script TEXT           Script filename [default: extractor.sh]
  --description TEXT      Workload description
  --status TEXT           Workload status (active/inactive) [default: active]
```

### `update-workload` - Update Existing Workload
```bash
result-parser update-workload <name> [OPTIONS]

Arguments:
  name                    Workload name

Options:
  --metrics TEXT          Comma-separated list of metrics
  --script TEXT           Script filename
  --description TEXT      Workload description
  --status TEXT           Workload status (active/inactive)
```

### `show-workload` - Show Workload Details
```bash
result-parser show-workload <name>

Arguments:
  name                    Workload name to display
```

## 🔒 Security Features

- **SSH Authentication**: Secure access to private Git repositories
- **Environment Variables**: No hardcoded secrets or API keys
- **Input Validation**: Comprehensive validation of all user inputs
- **Secure Defaults**: Principle of least privilege in configuration
- **Script Isolation**: Scripts run in controlled environment

## 🚀 Performance Features

- **Script Caching**: Local cache with TTL-based invalidation
- **Sparse Git Operations**: Efficient individual script retrieval
- **Lazy Loading**: Scripts downloaded only when needed
- **Optimized API Calls**: Efficient MongoDB API interactions

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/result_parser_agent

# Run specific test file
uv run pytest tests/test_cli.py
```

## 📚 Development

### Code Quality
```bash
# Format code
uv run black .

# Sort imports
uv run isort .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks
pre-commit run --all-files
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/Infobellit-Solutions-Pvt-Ltd/result-parser-agent/wiki)
- **Issues**: [GitHub Issues](https://github.com/Infobellit-Solutions-Pvt-Ltd/result-parser-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Infobellit-Solutions-Pvt-Ltd/result-parser-agent/discussions)

## 🏆 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- Powered by [Typer](https://typer.tiangolo.com/) for CLI development
- Enhanced with [Pydantic](https://pydantic.dev/) for data validation
- Script management powered by Git and SSH