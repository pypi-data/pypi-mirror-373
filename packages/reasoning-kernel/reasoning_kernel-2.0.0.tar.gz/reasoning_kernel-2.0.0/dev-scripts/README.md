# Development Scripts

This directory contains development and testing utilities used during the enhancement and debugging of the Reasoning Kernel system.

## Testing Scripts

### Quick Test (`quick_test.py`)

Basic import and functionality test for MSA plugins.

**Purpose:** Verify that MSA plugins can be imported and basic functions work.

**Usage:**

```bash
cd dev-scripts
python quick_test.py
```

**Output Example:**

```
🧪 Testing MSA Plugin Imports
========================================
✅ MSAReasoningPlugin imported successfully
✅ Basic analysis function available
✅ Plugin initialization successful
```

### Simple Test (`simple_test.py`)

Step-by-step Semantic Kernel import validation.

**Purpose:** Debug Semantic Kernel import issues and verify SDK availability.

**Usage:**

```bash
cd dev-scripts
python simple_test.py
```

**Output Example:**

```
Testing SK imports step by step...
1. Testing basic SK import...
   ✅ Kernel import OK
2. Testing Azure AI import...
   ✅ AzureChatCompletion import OK
3. Testing plugin decorators...
   ✅ Function decorators OK
```

### MSA Plugin Test (`test_msa_plugins.py`)

Comprehensive MSA plugin testing without CLI dependencies.

**Purpose:** Validate MSA plugins work correctly in isolation.

**Usage:**

```bash
cd dev-scripts
python test_msa_plugins.py
```

**Features Tested:**

- Plugin instantiation
- Function execution
- Error handling
- Performance metrics

### Enhanced CLI Test (`test_enhanced_cli.py`)

CLI functionality testing and validation.

**Purpose:** Test CLI commands and argument parsing.

**Usage:**

```bash
cd dev-scripts
python test_enhanced_cli.py
```

### SK Integration Tests

#### SK Imports Test (`test_sk_imports.py`)

Tests Semantic Kernel import patterns and compatibility.

**Purpose:** Verify SK integration works with current version.

#### SK Native Test (`test_sk_native.py`)

Tests SK-native function patterns and plugin architecture.

**Purpose:** Validate SK-native plugin implementations.

## Validation Scripts

### Super Simple Validation (`super_simple_validation.py`)

Minimal validation of core functionality.

**Purpose:** Quick smoke test to verify basic system functionality.

**Usage:**

```bash
cd dev-scripts
python super_simple_validation.py
```

### Quick Validation (`quick_validation.py`)

Fast validation of key components.

**Purpose:** Rapid health check for development iterations.

### MSA Enhancement Validation (`validate_msa_enhancements.py`)

Validates all MSA enhancement implementations.

**Purpose:** Comprehensive validation of MSA system improvements.

**Usage:**

```bash
cd dev-scripts
python validate_msa_enhancements.py
```

**Validation Areas:**

- Plugin architecture
- Service integration
- API functionality
- CLI commands
- Error handling

### Plugin Test (`test_plugins.py`)

Direct plugin testing and validation.

**Purpose:** Test plugin loading, registration, and execution.

## Development Workflow

### Quick Development Check

For rapid development iterations:

```bash
# 1. Quick import test
python dev-scripts/simple_test.py

# 2. Plugin validation
python dev-scripts/test_msa_plugins.py

# 3. Basic functionality check
python dev-scripts/super_simple_validation.py
```

### Comprehensive Validation

Before committing changes:

```bash
# 1. Full SK integration test
python dev-scripts/test_sk_native.py

# 2. Complete MSA validation
python dev-scripts/validate_msa_enhancements.py

# 3. CLI functionality test
python dev-scripts/test_enhanced_cli.py
```

### Debug Workflow

When troubleshooting issues:

```bash
# 1. Basic imports
python dev-scripts/simple_test.py

# 2. Detailed plugin test
python dev-scripts/test_msa_plugins.py --verbose

# 3. Component isolation
python dev-scripts/quick_test.py
```

## Script Organization

### Import Testing

- `simple_test.py` - Basic SK imports
- `test_sk_imports.py` - Detailed import validation
- `quick_test.py` - Plugin import testing

### Functionality Testing

- `test_msa_plugins.py` - MSA plugin functionality
- `test_sk_native.py` - SK-native patterns
- `test_plugins.py` - General plugin testing

### System Validation

- `super_simple_validation.py` - Minimal validation
- `quick_validation.py` - Fast validation
- `validate_msa_enhancements.py` - Comprehensive validation

### CLI Testing

- `test_enhanced_cli.py` - CLI functionality testing

## Usage Guidelines

### Development Phase

During active development, use these scripts for:

1. **Rapid feedback**: Quick tests for immediate validation
2. **Component isolation**: Test individual components
3. **Integration verification**: Ensure components work together
4. **Performance monitoring**: Track performance impacts

### Pre-Commit Validation

Before committing code changes:

1. Run comprehensive validation scripts
2. Verify all import tests pass
3. Ensure plugin functionality is maintained
4. Test CLI command compatibility

### Troubleshooting

When encountering issues:

1. Start with simple import tests
2. Isolate the problematic component
3. Use verbose output modes
4. Check error logs and stack traces

## Environment Setup

### Prerequisites

```bash
# Ensure development environment is activated
source .venv/bin/activate  # or your environment activation

# Install development dependencies
uv install --dev
```

### Configuration

```bash
# Copy environment template if not exists
cp .env.example .env

# Set development-specific variables
export REASONING_KERNEL_ENVIRONMENT=development
export REASONING_KERNEL_LOG_LEVEL=DEBUG
```

## Script Maintenance

### Adding New Scripts

When creating new development scripts:

1. **Follow naming convention**: `test_*.py` for tests, `validate_*.py` for validation
2. **Include docstrings**: Clear description of purpose and usage
3. **Handle errors gracefully**: Provide helpful error messages
4. **Use consistent output format**: Match existing script patterns

### Script Template

```python
#!/usr/bin/env python3
"""
Script Name
===========
Brief description of what this script does and when to use it.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Main script function"""
    print("🔧 Development Script: Script Name")
    print("=" * 40)
    
    try:
        # Script logic here
        print("✅ Script completed successfully")
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Integration with Main Testing

These development scripts complement the main testing framework in `tests/`:

- **Dev scripts**: Quick validation during development
- **Main tests**: Comprehensive testing for CI/CD
- **Integration**: Dev scripts can be used for rapid feedback before running full test suite

## Debugging Tips

### Common Issues

1. **Import Errors**: Use `simple_test.py` to isolate import problems
2. **Plugin Issues**: Use `test_msa_plugins.py` for detailed plugin debugging  
3. **Configuration Problems**: Check environment variables and settings
4. **Performance Issues**: Use validation scripts to identify bottlenecks

### Debug Output

Enable verbose output in scripts:

```bash
python dev-scripts/test_msa_plugins.py --verbose --debug
```

Set debug environment:

```bash
export REASONING_KERNEL_LOG_LEVEL=DEBUG
export PYTHONPATH=$(pwd):$PYTHONPATH
```

These development scripts provide essential tools for maintaining code quality and rapid development iteration during the enhancement process.
