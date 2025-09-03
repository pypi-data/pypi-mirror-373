# Rebuilding Aider with Jac

**Autonomous Code Editor Powered by Jac Object-Spatial Programming**

*Developed by Team ByteBrains*

## 🎥 Live Demonstration

**Watch the system in action:**

- **🤖 Agent Mode Demo:** [Autonomous Agentic AI Operations](https://youtu.be/2h2Y8VzGq8g)
- **⚙️ Standard Mode Demo:** [Standard Code Editing Features](https://youtu.be/qP_V97Zia7s)

See real-time autonomous code editing, multi-file coordination, and spatial programming capabilities demonstrated on production codebases.

---

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Agentic AI](https://img.shields.io/badge/Agentic-AI-purple.svg)](https://openrouter.ai/)
[![OSP Technology](https://img.shields.io/badge/OSP-Spatial%20Programming-green.svg)](https://github.com/ThiruvarankanM/Rebuilding-Aider-with-Jac-OSP)
[![Jac Language](https://img.shields.io/badge/Jac-Language-orange.svg)](https://docs.jac-lang.org/)
[![Multi-LLM](https://img.shields.io/badge/Multi--LLM-Support-red.svg)](https://openrouter.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

An autonomous code editing system that demonstrates Agentic AI capabilities through intelligent task planning, multi-file coordination, and spatial code analysis. Built with Python-Jac integration for professional development workflows.

**Key Achievements:**
- 25.8% token cost reduction on production codebases
- Multi-file autonomous editing with coordinated changes
- Spatial code analysis using Object-Spatial Programming algorithms
- Professional CLI interface with comprehensive operation tracking
- Multi-LLM provider support including cost-effective models

## Installation

### Option 1: PyPI Package (Recommended)
```bash
pip install aider-jac-osp
```

### Option 2: Docker Container
```bash
# Build and run with Docker
docker build -t aider-jac-osp .
docker run -it -v $(pwd):/workspace aider-jac-osp

# Or use docker-compose
docker-compose up aider-jac-osp
```

### Option 3: Development Setup
```bash
git clone https://github.com/ThiruvarankanM/Rebuilding-Aider-with-Jac-OSP.git
cd Rebuilding-Aider-with-Jac-OSP
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Set up the system:
```bash
aider-genius setup
```

Configure API settings in `~/.aider-genius/config.json`:
```json
{
  "llm_provider": "openrouter",
  "model": "google/gemma-2-9b-it:free",
  "api_key": "your-openrouter-key",
  "max_tokens": 4000,
  "temperature": 0.2
}
```

## Usage

### Quick Start
```bash
# Install the package
pip install aider-jac-osp

# Basic usage
aider --help                            # Standard aider interface
aider-genius --help                     # Advanced genius mode
```

### Project Analysis
```bash
aider-genius analyze                    # Analyze entire project structure
aider-genius analyze --dir src/         # Directory-specific analysis
aider-genius analyze --files main.py utils.py --verbose
```

### Cost Optimization
```bash
aider-genius optimize main.py          # Single file optimization
aider-genius optimize --files *.py     # Batch optimization
```

### Autonomous Editing
```bash
aider-genius edit "add error handling"
aider-genius edit "improve logging" --files app.py utils.py
aider-genius edit "optimize performance" --dry-run
```

## Architecture

### Core System Components

The system implements autonomous intelligence through:

- **Task Planning**: Independent decomposition of high-level objectives
- **Spatial Analysis**: Multi-dimensional code relationship understanding
- **Coordinated Execution**: Synchronized multi-file modification strategies
- **Adaptive Learning**: Pattern recognition for improved decision making

### Technology Stack
- **Python**: Core system implementation and LLM integration
- **Jac**: Object-Spatial Programming for advanced code analysis
- **Rich**: Professional terminal interface with visual formatting
- **Multi-LLM**: OpenAI, Anthropic, OpenRouter provider support

### Project Structure
```
aider/
├── cli.py                     # Command-line interface
├── integration/
│   ├── jac_bridge.py         # Python-Jac integration layer
│   ├── file_editor.py        # Autonomous editing engine
│   ├── llm_client.py         # Multi-provider LLM client
│   └── osp_interface.py      # Spatial programming interface
└── jac/                      # Spatial programming modules
    ├── repomap_osp.jac       # File ranking algorithms
    ├── token_optimizer.jac   # Cost optimization
    ├── planning_walker.jac   # Task decomposition
    └── context_gatherer.jac  # Context optimization
```

## Key Features

### Autonomous Code Understanding
- Real-time analysis of project structure and dependencies
- Intelligent file relevance scoring using spatial algorithms
- Cross-component relationship mapping for coordinated changes
- Pattern recognition for consistent code style maintenance

### Professional Development Integration
- Comprehensive backup system with version control
- Dry-run mode for safe change preview
- Git integration for collaborative workflows
- Enterprise-grade error handling and logging

### Cost-Effective Operation
- Proven 25.8% token reduction on large codebases
- Support for free-tier LLM models
- Intelligent prompt optimization for minimal API usage
- Configurable resource limits and usage tracking

## Performance Metrics

| Feature | Result | Impact |
|---------|--------|---------|
| Token Optimization | 25.8% reduction | Significant cost savings |
| File Analysis | 23+ files processed | Comprehensive coverage |
| Multi-file Coordination | Multiple simultaneous edits | Synchronized changes |
| Processing Speed | Sub-3 second response | Real-time workflow |

## Object-Spatial Programming Integration

Aider-Genius utilizes Object-Spatial Programming (OSP) for advanced code analysis:

- Spatial code graphs for relationship visualization
- Multi-dimensional dependency analysis
- Context-aware code selection and modification
- Predictive impact assessment across file boundaries

## Supported LLM Providers

- **OpenAI**: Complete GPT model support
- **Anthropic**: Claude integration
- **OpenRouter**: Multi-model access with free tiers
- **Custom**: Extensible provider system

## Command Reference

| Command | Description |
|---------|-------------|
| `aider-genius setup` | Initialize system configuration |
| `aider-genius analyze` | Perform spatial code analysis |
| `aider-genius optimize` | Optimize token usage and costs |
| `aider-genius edit <task>` | Execute autonomous editing tasks |
| `aider-genius --help` | Display comprehensive help |

## Testing

```bash
# Install and verify package
pip install aider-jac-osp
pip show aider-jac-osp

# Test functionality
aider --version
aider-genius analyze --dry-run
python -c "import aider; print('Import successful')"

# Development testing
python system_test.py

# Test autonomous capabilities
aider-genius edit "comprehensive code improvement" --dry-run
```

## Contributing

1. Fork the repository
2. Create feature branches for enhancements
3. Submit pull requests with comprehensive testing
4. Follow established code quality standards

## Future Enhancements

- Advanced LLM integration (GPT-4, Claude-3)
- Web-based interface for visual spatial programming
- IDE plugins for native development environment integration
- Enhanced pattern recognition with AST-based analysis
- Team collaboration features with multi-developer coordination

## License

MIT License - Open source autonomous AI innovation

---

**Professional autonomous coding solution powered by Agentic AI and Object-Spatial Programming | Team ByteBrains**
