#!/bin/bash

# Reasoning Kernel One-Line Installation Script
# Supports macOS, Linux (Ubuntu/Debian/CentOS/Fedora)

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            echo "ubuntu"
        elif command -v yum &> /dev/null; then
            echo "centos"
        elif command -v dnf &> /dev/null; then
            echo "fedora"
        else
            echo "linux"
        fi
    else
        echo "unsupported"
    fi
}

# Check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Install Python 3.12 if not available
install_python() {
    local os_type=$1
    log "Checking Python installation..."
    
    if command_exists python3.12; then
        PYTHON_CMD="python3.12"
        success "Python 3.12 already installed"
    elif command_exists python3 && [[ $(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2) == "3.12" ]]; then
        PYTHON_CMD="python3"
        success "Python 3.12 already installed"
    else
        log "Installing Python 3.12..."
        case $os_type in
            "macos")
                if command_exists brew; then
                    brew install python@3.12
                    PYTHON_CMD="python3.12"
                else
                    error "Homebrew not found. Please install Homebrew first: https://brew.sh/"
                    exit 1
                fi
                ;;
            "ubuntu")
                sudo apt-get update
                sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
                PYTHON_CMD="python3.12"
                ;;
            "centos")
                sudo yum install -y python3.12 python3.12-devel
                PYTHON_CMD="python3.12"
                ;;
            "fedora")
                sudo dnf install -y python3.12 python3.12-devel
                PYTHON_CMD="python3.12"
                ;;
            *)
                error "Unsupported OS for automatic Python installation"
                exit 1
                ;;
        esac
        success "Python 3.12 installed"
    fi
}

# Install uv package manager
install_uv() {
    log "Installing uv package manager..."
    if command_exists uv; then
        success "uv already installed"
    else
        # Use the official installation method
        if command_exists curl; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
        elif command_exists wget; then
            wget -O - https://astral.sh/uv/install.sh | sh
        else
            error "Neither curl nor wget found. Please install one of them first."
            exit 1
        fi
        # Add uv to PATH for the current session
        export PATH="$HOME/.local/bin:$PATH"
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            export PATH="$HOME/.local/bin:$PATH"
        fi
        success "uv installed"
    fi
}

# Create virtual environment
create_venv() {
    log "Creating virtual environment..."
    if [ ! -d ".msa-venv" ]; then
        $PYTHON_CMD -m venv .msa-venv
        success "Virtual environment created"
    else
        warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .msa-venv/bin/activate
    success "Virtual environment activated"
}

# Install Reasoning Kernel
install_reasoning_kernel() {
    log "Installing Reasoning Kernel..."
    
    # Check if we're in a git repository
    if [ -d ".git" ]; then
        log "Installing in development mode (editable install)..."
        if command_exists uv; then
            uv pip install -e ".[all]"
        else
            pip install -e ".[all]"
        fi
    else
        log "Installing from PyPI..."
        if command_exists uv; then
            uv pip install "reasoning-kernel[all]"
        else
            pip install "reasoning-kernel[all]"
        fi
    fi
    
    success "Reasoning Kernel installed"
}

# Configure Daytona API key
configure_daytona() {
    log "Configuring Daytona API key..."
    echo "To configure Daytona, please set the following environment variables:"
    echo "  export DAYTONA_API_KEY=your_api_key_here"
    echo "  export DAYTONA_API_URL=https://app.daytona.io"
    echo ""
    echo "You can get your Daytona API key from: https://www.daytona.io/"
    echo ""
    read -p "Would you like to configure Daytona now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Daytona API key (or press Enter to skip): " daytona_api_key
        if [ ! -z "$daytona_api_key" ]; then
            echo "export DAYTONA_API_KEY=$daytona_api_key" >> ~/.msa_config
            echo "export DAYTONA_API_URL=https://app.daytona.io" >> ~/.msa_config
            success "Daytona API key configured"
            echo "To use the configuration in future sessions, add the following to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
            echo " source ~/.msa_config"
        fi
    fi
}

# Verify installation
verify_installation() {
    log "Verifying installation..."
    if command -v reasoning-kernel &> /dev/null; then
        reasoning-kernel --help > /dev/null
        success "Reasoning Kernel CLI verified"
    else
        error "Installation verification failed"
        exit 1
    fi
}

# Main installation function
main() {
    echo "========================================"
    echo "  Reasoning Kernel Installer"
    echo "========================================"
    echo
    
    # Check if we're running on a supported platform
    OS_TYPE=$(detect_os)
    if [[ $OS_TYPE == "unsupported" ]]; then
        error "Unsupported operating system. This script supports macOS and Linux (Ubuntu/Debian/CentOS/Fedora)."
        exit 1
    fi
    
    log "Detected OS: $OS_TYPE"
    
    # Install Python if needed
    install_python $OS_TYPE
    
    # Install uv package manager
    install_uv
    
    # Create virtual environment
    create_venv
    
    # Install Reasoning Kernel
    install_msa_kernel
    
    # Configure Daytona
    configure_daytona
    
    # Verify installation
    verify_installation
    
    echo
    echo "========================================"
    success "Reasoning Kernel installed successfully!"
    echo "========================================"
    echo
    echo "To use the Reasoning Kernel:"
    echo "1. Activate the virtual environment: source .msa-venv/bin/activate"
    echo "2. Run the CLI: reasoning-kernel --help"
    echo
    echo "To configure Daytona in future sessions, add to your shell profile:"
    echo "  source ~/.msa_config"
    echo
}

# Run main function
main "$@"