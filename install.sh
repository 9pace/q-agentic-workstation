#!/bin/bash
#
# Q Agentic Workstation Installation Script
#
# This script installs qaw and its dependencies.

set -e

echo "=================================="
echo "Q Agentic Workstation Installer"
echo "=================================="
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}✗ Python version $PYTHON_VERSION is too old${NC}"
    echo "Python 3.8 or later is required"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check Q CLI
echo "Checking Amazon Q CLI..."
if ! command -v q &> /dev/null; then
    echo -e "${YELLOW}⚠ Amazon Q CLI not found${NC}"
    echo "Please install Q CLI first: https://docs.aws.amazon.com/amazonq/latest/aws-builder-use-ug/command-line.html"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    Q_VERSION=$(q --version 2>&1 || echo "unknown")
    echo -e "${GREEN}✓ Amazon Q CLI installed${NC}"
fi

# Check pip
echo "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip3 not found${NC}"
    echo "Installing pip..."
    python3 -m ensurepip --upgrade || {
        echo -e "${RED}Failed to install pip${NC}"
        exit 1
    }
fi
echo -e "${GREEN}✓ pip3 available${NC}"

# Install package
echo
echo "Installing Q Agentic Workstation..."
echo

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install in development mode
cd "$SCRIPT_DIR"
pip3 install -e . || {
    echo -e "${RED}✗ Installation failed${NC}"
    exit 1
}

echo
echo -e "${GREEN}✓ Installation complete!${NC}"
echo

# Verify installation
if command -v qaw &> /dev/null; then
    echo -e "${GREEN}✓ qaw command is available${NC}"
    QAW_VERSION=$(qaw --version 2>&1)
    echo "  Version: $QAW_VERSION"
else
    echo -e "${YELLOW}⚠ qaw command not found in PATH${NC}"
    echo "You may need to add ~/.local/bin to your PATH"
    echo "Add this to your ~/.zshrc or ~/.bashrc:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
fi

# Copy agent configs
echo
echo "Installing agent configurations..."
AGENT_DIR="$HOME/.aws/amazonq/cli-agents"
if [ -d "$AGENT_DIR" ]; then
    cp -v agents/*.json "$AGENT_DIR/" 2>/dev/null && \
        echo -e "${GREEN}✓ Agent configs installed${NC}" || \
        echo -e "${YELLOW}⚠ Could not copy agent configs${NC}"
else
    echo -e "${YELLOW}⚠ Q CLI agent directory not found: $AGENT_DIR${NC}"
    echo "Agent configs were not installed. You may need to copy them manually."
fi

echo
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo
echo "Quick Start:"
echo "  1. Navigate to your project directory"
echo "  2. Initialize workspace: qaw init"
echo "  3. Submit a task: qaw submit \"Create a React component\""
echo "  4. Check status: qaw status"
echo
echo "For more information, see: docs/GETTING_STARTED.md"
echo
