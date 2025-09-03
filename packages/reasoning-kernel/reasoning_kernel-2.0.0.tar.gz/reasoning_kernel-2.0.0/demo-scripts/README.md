# Demo Scripts

This directory contains demonstration scripts that showcase the capabilities of the Reasoning Kernel system.

## Available Demos

### CLI Demo (`cli_demo.py`)

Demonstrates the enhanced CLI functionality with all available commands.

**Usage:**

```bash
cd demo-scripts
python cli_demo.py msa-analyze --query "What is artificial intelligence?" --plugin simple
```

**Features Demonstrated:**

- MSA analysis with both simple and enhanced plugins
- Multiple output formats (text and JSON)
- Domain-specific analysis
- Rich console output with colors and formatting

### Interactive MSA Demo (`interactive_msa_demo.py`)

Interactive demonstration of MSA capabilities with user input.

**Usage:**

```bash
cd demo-scripts  
python interactive_msa_demo.py
```

**Features Demonstrated:**

- Interactive query input
- Plugin selection
- Real-time analysis results
- Step-by-step reasoning display

### Complete MSA Demo (`demo_msa_complete.py`)

Comprehensive demonstration of the complete MSA pipeline.

**Usage:**

```bash
cd demo-scripts
python demo_msa_complete.py
```

**Features Demonstrated:**

- Full MSA workflow
- Plugin comparison
- Performance metrics
- Error handling examples

### Simple MSA Demo (`simple_msa_demo.py`)

Basic demonstration of MSA functionality for quick testing.

**Usage:**

```bash
cd demo-scripts
python simple_msa_demo.py
```

**Features Demonstrated:**

- Basic MSA analysis
- Simple plugin usage
- Minimal setup requirements

## Launcher Scripts

### API Server Launcher (`launch_api_server.py`)

Launches the FastAPI server with proper configuration.

**Usage:**

```bash
cd demo-scripts
python launch_api_server.py
```

**Features:**

- FastAPI server startup
- Automatic port detection
- Environment configuration
- Health check endpoints

### REPL Launcher (`repl_launcher.py`)

Launches an interactive Python REPL with Reasoning Kernel pre-loaded.

**Usage:**

```bash
cd demo-scripts
python repl_launcher.py
```

**Features:**

- Pre-configured environment
- Imported Reasoning Kernel modules
- Interactive exploration
- Helper functions available

## Running the Demos

### Prerequisites

Ensure you have the Reasoning Kernel installed and configured:

1. **Installation:**

   ```bash
   # From project root
   uv install -e .
   ```

2. **Configuration:**

   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

### Demo Execution

1. **Navigate to demo directory:**

   ```bash
   cd demo-scripts
   ```

2. **Run specific demo:**

   ```bash
   # CLI demo
   python cli_demo.py --help
   
   # Interactive demo
   python interactive_msa_demo.py
   
   # Complete demo
   python demo_msa_complete.py
   ```

3. **API server demo:**

   ```bash
   python launch_api_server.py
   # Then visit http://localhost:8000/docs
   ```

## Demo Scenarios

### Business Analysis Demo

```bash
python cli_demo.py msa-analyze \
  --query "Market trends for renewable energy in 2024" \
  --plugin enhanced \
  --domain business \
  --output json
```

### Technical Analysis Demo

```bash
python cli_demo.py msa-analyze \
  --query "Benefits of microservices architecture" \
  --plugin enhanced \
  --domain technical \
  --output text
```

### Scientific Analysis Demo

```bash
python cli_demo.py msa-analyze \
  --query "Impact of quantum computing on cryptography" \
  --plugin enhanced \
  --domain scientific \
  --output json
```

## Integration Examples

### Python Integration

```python
# Example of using demos in other Python code
import sys
from pathlib import Path

# Add demo scripts to path
demo_path = Path(__file__).parent / "demo-scripts"
sys.path.insert(0, str(demo_path))

# Import demo functionality
from cli_demo import demonstrate_msa_analysis

# Use in your code
result = demonstrate_msa_analysis(
    query="Your analysis query",
    plugin="enhanced",
    domain="technical"
)
```

### Shell Script Integration

```bash
#!/bin/bash
# batch_demo.sh - Run multiple demos

cd demo-scripts

echo "Running CLI demo..."
python cli_demo.py msa-analyze --query "AI trends" --plugin simple

echo "Running interactive demo..."
echo -e "What is machine learning?\nenhanced\ngeneral\nq" | python interactive_msa_demo.py

echo "Running complete demo..."
python demo_msa_complete.py
```

## Troubleshooting

### Common Issues

1. **Module Import Errors:**

   ```bash
   # Ensure Reasoning Kernel is installed
   uv install -e .
   ```

2. **Configuration Errors:**

   ```bash
   # Check environment configuration
   cat .env
   # Ensure all required variables are set
   ```

3. **API Server Issues:**

   ```bash
   # Check port availability
   lsof -i :8000
   # Use different port if needed
   python launch_api_server.py --port 8001
   ```

### Debug Mode

Run demos with debug information:

```bash
export REASONING_KERNEL_LOG_LEVEL=DEBUG
python cli_demo.py msa-analyze --query "test" --verbose
```

## Contributing New Demos

### Demo Structure

```python
#!/usr/bin/env python3
"""
Demo Name
=========
Brief description of what this demo shows.
"""

import asyncio
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def main():
    """Main demo function"""
    # Demo implementation here
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

### Demo Guidelines

1. **Clear Documentation:** Include docstrings explaining the demo purpose
2. **Error Handling:** Provide helpful error messages
3. **User Interaction:** Make demos interactive where appropriate
4. **Resource Cleanup:** Properly clean up resources
5. **Example Output:** Show expected output in comments

This collection of demo scripts provides comprehensive examples of how to use all aspects of the Reasoning Kernel system, from basic CLI usage to advanced API integration.
