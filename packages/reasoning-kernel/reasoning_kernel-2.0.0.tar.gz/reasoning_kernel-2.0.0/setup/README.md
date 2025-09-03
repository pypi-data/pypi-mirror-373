# Reasoning Kernel Installation

This directory contains installation scripts for the Reasoning Kernel with Semantic Kernel integration on different platforms.

## One-Line Installation

For macOS and Linux, you can install the Reasoning Kernel with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/Qredence/Reasoning-Kernel/main/setup/install.sh | bash
```

For Windows, download and run the `install.bat` script:

```cmd
curl -fsSL https://raw.githubusercontent.com/Qredence/Reasoning-Kernel/main/setup/install.bat -o install.bat
install.bat
```

## Platform-Specific Installation

### macOS and Linux

Run the installation script directly:

```bash
./setup/install.sh
```

The script will:

1. Detect your operating system
2. Install Python 3.12 if not already installed
3. Install the uv package manager
4. Create a virtual environment
5. Install the Reasoning Kernel
6. Configure Daytona API key (optional)
7. Verify the installation

### Windows

Run the batch script:

```cmd
setup\install.bat
```

The script will:

1. Check for Python 3.12 and install if needed (requires Chocolatey)
2. Install the uv package manager
3. Create a virtual environment
4. Install the Reasoning Kernel
5. Configure Daytona API key (optional)
6. Verify the installation

## Manual Installation

If you prefer to install manually, follow these steps:

1. Ensure you have Python 3.12 installed
2. Install the uv package manager:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Create a virtual environment:

   ```bash
   python3.12 -m venv .msa-venv
   source .msa-venv/bin/activate  # On Windows: .msa-venv\Scripts\activate
   ```

4. Install the Reasoning Kernel:

   ```bash
   # zsh note: quote extras to avoid globbing
   uv pip install "reasoning-kernel[all]"
   ```

5. Verify the installation:

   ```bash
   reasoning-kernel --help
   ```

## Configuration

After installation, you can configure the Daytona API key:

```bash
export DAYTONA_API_KEY=your_api_key_here
export DAYTONA_API_URL=https://app.daytona.io
```

Add these lines to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) to make them persistent.

## Usage

After installation, activate the virtual environment and use the CLI:

```bash
source .msa-venv/bin/activate  # On Windows: .msa-venv\Scripts\activate
reasoning-kernel --help
```

### Daytona sandbox quick start

Execute a small NumPyro example in the Daytona sandbox. Create a file `example_ppl.py`:

```python
from numpyro import sample, distributions as dist

def main():
    mu = sample("mu", dist.Normal(0, 1))
    return {"mu": float(mu)}
```

Run it via the CLI:

```bash
reasoning-kernel sandbox execute --file example_ppl.py --framework numpyro --entry-point main
```

Tip for zsh users: when passing inline code, quote the argument to prevent bracket/brace expansion.
