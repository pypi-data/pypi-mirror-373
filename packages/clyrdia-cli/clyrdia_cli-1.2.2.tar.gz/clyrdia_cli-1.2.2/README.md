# Clyrdia CLI - Zero-Knowledge AI Benchmarking Platform

[![PyPI version](https://badge.fury.io/py/clyrdia-cli.svg)](https://badge.fury.io/py/clyrdia-cli)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

🚀 **The most advanced local-first AI model benchmarking tool** - Test, compare, and evaluate AI models with zero data exposure.

## ✨ Features

- **🔒 Zero-Knowledge**: Your data never leaves your system
- **📊 Comprehensive Benchmarking**: Test multiple AI models simultaneously
- **🎯 Production-Ready**: Includes customizable production benchmark suite
- **⚡ High Performance**: Async processing with intelligent caching
- **📈 Quality Evaluation**: Advanced metrics and scoring systems
- **🔄 Continuous Testing**: Canary and ratchet systems for ongoing validation
- **💾 Local Storage**: All results stored locally with optional cloud sync
- **👥 Team Collaboration**: Multi-user support with role-based access (Business tier)
- **🚀 CI/CD Integration**: Automated testing and quality gates (Business tier)

## 🚀 Quick Start

### Installation

```bash
pip install clyrdia-cli
```

### Basic Usage

```bash
# Run a benchmark with the included production configuration
clyrdia-cli run --config production_benchmark.yaml

# Run with custom configuration
clyrdia-cli run --config your_config.yaml

# View help and available commands
clyrdia-cli --help
```

## 📋 Prerequisites

- Python 3.8 or higher
- API keys for the AI models you want to test:
  - OpenAI API key for GPT models
  - Anthropic API key for Claude models

## 🔧 Configuration

### Environment Setup

Create a `.env` file in your project directory:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Custom configuration
CLYRIDIA_CONFIG_PATH=./config.yaml
```

### Benchmark Configuration

The package includes a production-ready benchmark configuration (`production_benchmark.yaml`) that tests:

- **Financial Risk Assessment** - Complex business analysis
- **Legal Contract Review** - Deep legal understanding
- **Marketing Strategy Development** - Creative and analytical thinking
- **System Architecture Design** - Technical complexity
- **Customer Success Strategy** - Business operations

### Custom Benchmark Configuration

Create your own benchmark configuration:

```yaml
name: "Custom Benchmark Suite"
description: "Your custom AI model testing scenarios"

models:
  - "claude-opus-4.1"
  - "gpt-5o"

tests:
  - name: "Your Test Case"
    prompt: |
      Your custom prompt here...
    expected_output: "Expected output description"
    max_tokens: 2000
    temperature: 0.3
    evaluation_criteria:
      - "accuracy"
      - "completeness"
      - "relevance"
```

## 💰 Pricing Tiers

### **Developer Tier (Free)**
- **Target**: All developers, everywhere
- **Goal**: Drive massive top-of-funnel adoption and create fans
- **Offer**: 100 credits/month, single user, no CI/CD

### **Pro Tier ($25/month)**
- **Target**: The serious individual professional or freelancer
- **Goal**: Monetize power users and provide a stepping stone
- **Offer**: 1,000 credits/month, single user, still no CI/CD

### **Business Tier ($500/month)**
- **Target**: Professional teams of 2-10 developers
- **Goal**: Be your primary revenue engine
- **Offer**: 25,000 credits/month, up to 10 users, and the killer CI/CD Integration feature

## 🎯 Available Commands

### `run` - Execute Benchmark
```bash
clyrdia-cli run --config production_benchmark.yaml
```

Options:
- `--config, -c`: Path to benchmark configuration file
- `--output, -o`: Output directory for results
- `--cache, --no-cache`: Enable/disable caching
- `--verbose, -v`: Verbose output

### `auth` - Authentication Management
```bash
clyrdia-cli auth --setup
clyrdia-cli auth --status
```

### `dashboard` - Launch Web Dashboard
```bash
clyrdia-cli dashboard
```

### `cache` - Cache Management
```bash
clyrdia-cli cache --clear
clyrdia-cli cache --status
```

### `plans` - View Subscription Plans
```bash
clyrdia-cli plans
```

### `status` - Account Status
```bash
clyrdia-cli status
```

### `team` - Team Management (Business Tier)
```bash
clyrdia-cli team
```

### `cicd` - CI/CD Integration (Business Tier)
```bash
clyrdia-cli cicd
```

### `upgrade` - Plan Upgrade Information
```bash
clyrdia-cli upgrade
```

## 📊 Output and Results

Benchmark results are saved in JSON format with comprehensive metrics:

- **Performance Metrics**: Response time, token usage, cost analysis
- **Quality Scores**: Accuracy, completeness, business relevance
- **Comparative Analysis**: Model-to-model performance comparison
- **Detailed Logs**: Full conversation history and evaluation details

## 🔍 Advanced Features

### Caching System
- Smart caching for repeated requests
- Configurable TTL and storage limits
- Cost optimization for development and testing

### Quality Evaluation
- Multi-dimensional scoring system
- Business relevance assessment
- Execution feasibility analysis

### Continuous Testing
- Canary system for ongoing validation
- Ratchet system for quality gates
- Automated regression detection

## 🏗️ Architecture

```
clyrdia/
├── cli_modular.py      # Main CLI application
├── benchmarking/        # Core benchmarking engine
├── models/             # Data models and configurations
├── caching/            # Intelligent caching system
├── auth/               # Authentication and licensing
├── database/           # Local data storage
├── core/               # Core utilities and decorators
└── utils/              # Helper functions
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=clyrdia tests/
```

## 📦 Package Development

### Building the Package

```bash
# Build source distribution
python -m build --sdist

# Build wheel
python -m build --wheel

# Build both
python -m build
```

### Publishing to Test PyPI

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ clyrdia-cli
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is proprietary software. See [LICENSE](LICENSE) for details.

## 🆘 Support

- **Documentation**: [https://docs.clyrdia.com](https://docs.clyrdia.com)
- **Issues**: [GitHub Issues](https://github.com/clyrdia/clyrdia-cli/issues)
- **Email**: team@clyrdia.com

## 🗺️ Roadmap

- [ ] Cloud synchronization
- [ ] Advanced analytics dashboard
- [ ] Model fine-tuning integration
- [ ] Enterprise SSO support
- [ ] Multi-language support
- [ ] API rate limiting optimization

---

**Built with ❤️ by the Clyrdia Team**

