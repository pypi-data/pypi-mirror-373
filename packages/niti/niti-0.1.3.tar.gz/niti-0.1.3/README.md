<div align="center">

# Niti by Vajra 


[![Documentation](https://img.shields.io/badge/📖_Documentation-blue?style=for-the-badge)](https://project-vajra.github.io/niti/)
[![Discord](https://img.shields.io/badge/💬_Discord-7289da?style=for-the-badge)](https://discord.gg/wjaSvGgsNN)
[![PyPI](https://img.shields.io/pypi/v/niti?style=for-the-badge&color=green)](https://pypi.org/project/niti/)


Fast, Modern, Lean Linter for C++ code for Vajra. Easy to configure no frills supercharged C++ linter with plugin support for custom rules.

</div>

## Setup

### Installation

```bash
pip install rekha
```

## Usage

### Basic Linting

```bash
# Lint a single file
niti path/to/file.cpp

# Lint a directory (recursively finds all C++ files)
niti path/to/project/

# Lint current directory
niti .

# Show help and available options
niti --help

# List all available rules
niti --list-rules

# List rules with descriptions
niti --list-rules --verbose
```

### Discovering Available Rules

Before disabling rules, you can discover what rules are available and which ones are triggering:

```bash
# See all available rules and their categories
niti --list-rules

# Run linter to see which rules are being triggered
niti --check your_project/

# Get detailed information about specific rule violations
niti --check --verbose your_file.cpp
```

### Configuration File (.nitirc or niti.yaml)

Create a `.nitirc` or `niti.yaml` file in your project root to customize linting behavior:

```yaml
# Basic configuration
documentation_style: doxygen  # Options: doxygen, javadoc, plain
copyright_holders:
  - "Your Organization"
  - "Your Team"

# File organization
header_extensions: [".h", ".hpp", ".hxx"]
source_extensions: [".cpp", ".cc", ".cxx"] 
excluded_paths: ["/kernels/", "/test/", "/build/"]

# Disable specific rules globally  
disabled_rules:
  - type-forbidden-int
  - modern-missing-noexcept
  - doc-function-missing

# Enable specific rules (overrides defaults)
enabled_rules:
  - modern-nodiscard-missing
  - doc-function-param-desc-quality

# Override rule severities
rule_severities:
  naming-function-case: error
  safety-raw-pointer-param: warning
  doc-class-missing: info
```

### Disabling Rules

Niti supports multiple approaches for rule suppression:

**Configuration-based (global):**
```yaml
# .nitirc or niti.yaml
rules:
  type-forbidden-int:
    enabled: false
  naming-variable-case:
    severity: warning
```

**Comment-based (NOLINT):**
```cpp
int value = 42;  // NOLINT
int badName = 10;  // NOLINT naming-variable-case
int multiple = 99;  // NOLINT type-forbidden-int,naming-variable-case

// NOLINTNEXTLINE type-forbidden-int
int nextLine = 24;
```

**File-level disable:**
```cpp
// niti-lint-disable naming-variable-case
// niti-lint-disable type-forbidden-int
```

📚 **[Complete Rule Suppression Guide →](docs/source/index.md#rule-suppression-and-configuration)**


## Development

### Prerequisites

- Python 3.8 or higher

### Setting Up Development Environment

We recommend using a virtual environment to isolate dependencies. You can use either `uv` or `conda`:

#### Option 1: Using uv (Recommended)
```bash
# Clone the repository
git clone https://github.com/project-vajra/niti.git
cd niti

# Create and activate virtual environment with uv
uv venv
source .venv/bin/activate 

# Install dependencies
# For development:
uv pip install -r requirements-dev.txt
# Install Niti
uv pip install -e .

# Or install directly with optional dependencies:
uv pip install -e .[dev]
```

#### Option 2: Using conda/mamba
```bash
# Clone the repository
git clone https://github.com/project-vajra/niti.git
cd niti

# Create conda environment from file
conda env create -f environment.yml
conda activate niti

# Install the package in editable mode
pip install -e .

# Or use the Makefile for convenience
make install-dev
```

### Installing Dependencies

The project has the following main dependencies:
- `pyyaml`: For configuration file parsing
- `tree-sitter` & `tree-sitter-cpp`: For C++ code parsing

Development dependencies include:
- `pytest`: Testing framework
- `black`, `isort` & `autoflake`: Code formatting and cleanup
- `flake8` & `mypy`: Linting and type checking
- `pytest-cov`: Coverage reporting

**Note**: Niti is not yet available on PyPI. For now, please install from source as shown above.

### Development Workflow

#### Running Tests using PyTests

Niti has a comprehensive test suite organized into unit and integration tests:

```bash
# Run all tests
pytest

# Run all tests with coverage report
pytest --cov=niti --cov-report=html

# Run only unit tests (fast, isolated)
pytest -m unit

# Run only integration tests (slower, end-to-end)
pytest -m integration

# Run tests for specific rule categories
pytest test/unit/naming/           # Naming convention rules
pytest test/unit/safety/           # Safety rules
pytest test/unit/modern_cpp/       # Modern C++ rules
pytest test/unit/documentation/    # Documentation rules

# Run tests with verbose output
pytest -v

# Run a specific test file
pytest test/unit/types/test_type_rules.py

# Run a specific test method
pytest test/unit/naming/test_naming_rules.py::TestNamingFunctionCase::test_detects_snake_case_functions
```

##### Using the Custom Test Runner

The project includes a custom test runner for convenience:

```bash
# Run unit tests
python test/run_tests.py unit

# Run integration tests
python test/run_tests.py integration

# Run all tests
python test/run_tests.py all

# Run with verbose output and coverage
python test/run_tests.py unit -v -c
```

##### Test Structure

The test suite is organized as follows:
- **`test/unit/`**: Fast, isolated unit tests organized by rule category
- **`test/integration/`**: End-to-end integration tests
- **`test/fixtures/`**: Reusable C++ code samples for testing
- **`test/test_utils.py`**: Base classes and testing utilities

Each rule category has comprehensive positive (should pass) and negative (should fail) test cases using real C++ code examples.

#### Code Quality Checks

You can use individual commands or the convenient Makefile targets:

##### Using Makefile (Recommended)
```bash
# Format code (autoflake + black + isort)
make format

# Run linting (flake8 + mypy)
make lint

# Run tests
make test

# Run tests with coverage
make test-cov

# Show all available commands
make help
```

#### Project Structure
```
niti/
├── niti/                   # Main package
│   ├── cli.py             # Command-line interface
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration handling
│   │   ├── engine.py      # Linting engine
│   │   ├── issue.py       # Issue representation
│   │   └── severity.py    # Severity levels
│   └── rules/             # Linting rules (54+ rules across categories)
│       ├── base.py        # Base rule classes
│       ├── naming.py      # Naming convention rules
│       ├── safety.py      # Safety-related rules
│       ├── modern_cpp.py  # Modern C++ best practices
│       ├── documentation.py # Documentation requirements
│       ├── types.py       # Type system rules
│       └── ...            # Other rule categories
├── test/                  # Comprehensive test suite
│   ├── unit/              # Unit tests by rule category
│   │   ├── naming/        # Tests for naming rules
│   │   ├── safety/        # Tests for safety rules
│   │   ├── modern_cpp/    # Tests for modern C++ rules
│   │   ├── documentation/ # Tests for documentation rules
│   │   ├── types/         # Tests for type system rules
│   │   └── ...            # Other rule category tests
│   ├── integration/       # End-to-end integration tests
│   ├── fixtures/          # Reusable C++ code samples
│   ├── test_utils.py      # Testing base classes and utilities
│   └── run_tests.py       # Custom test runner
├── pyproject.toml         # Project configuration
├── Makefile              # Development workflow commands
├── CLAUDE.md             # Claude Code assistant guidance or for other Agentic tools
└── README.md             # This file
```

## Examples

Full sample on using the Linter in a large-scale C++ project in the Vajra project will be out soon. We're building [Vajra](https://github.com/project-vajra/vajra) the second-generation LLM serving engine in C++. Watch out this space for more details soon.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.