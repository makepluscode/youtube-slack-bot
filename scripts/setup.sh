#!/bin/bash
#
# Setup script for YouTube Download Agent
# This script installs all dependencies and configures the environment
#

set -e  # Exit on error

echo "================================================"
echo "YouTube Download Agent - Setup"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Project directory: $PROJECT_DIR"
echo ""

# Check if Homebrew is installed
echo "Checking Homebrew..."
if ! command -v brew &> /dev/null; then
    echo -e "${RED}❌ Homebrew is not installed${NC}"
    echo "Install Homebrew from: https://brew.sh"
    exit 1
fi
echo -e "${GREEN}✅ Homebrew found${NC}"

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo -e "${RED}❌ Python 3.11+ is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Install uv if not installed
echo ""
echo "Checking uv package manager..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    brew install uv
fi
echo -e "${GREEN}✅ uv found${NC}"

# Install yt-dlp if not installed
echo ""
echo "Checking yt-dlp..."
if ! command -v yt-dlp &> /dev/null; then
    echo "Installing yt-dlp..."
    brew install yt-dlp
fi
echo -e "${GREEN}✅ yt-dlp found${NC}"

# Install Ollama if not installed
echo ""
echo "Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    brew install ollama
    
    echo -e "${YELLOW}⚠️  Starting Ollama service...${NC}"
    brew services start ollama
    sleep 5
fi
echo -e "${GREEN}✅ Ollama found${NC}"

# Check if gemma3:4b model is available
echo ""
echo "Checking Ollama model (gemma3:4b)..."
if ! ollama list | grep -q "gemma3:4b"; then
    echo "Pulling gemma3:4b model (this may take a while)..."
    ollama pull gemma3:4b
fi
echo -e "${GREEN}✅ gemma3:4b model available${NC}"

# Install Python dependencies with uv
echo ""
echo "Installing Python dependencies with uv..."
cd "$PROJECT_DIR"
uv sync

echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Create .env file if it doesn't exist
echo ""
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Creating .env file from template..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo -e "${YELLOW}⚠️  Please edit .env file and add your Slack tokens:${NC}"
    echo "   - SLACK_BOT_TOKEN"
    echo "   - SLACK_APP_TOKEN"
    echo ""
    echo "   Run: nano $PROJECT_DIR/.env"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create download directory
echo ""
echo "Creating download directory..."
DOWNLOAD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Youtube"
mkdir -p "$DOWNLOAD_DIR"
echo -e "${GREEN}✅ Download directory: $DOWNLOAD_DIR${NC}"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

echo ""
echo "================================================"
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Slack tokens:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. Test the bot:"
echo "   cd $PROJECT_DIR"
echo "   uv run youtube-agent"
echo ""
echo "3. Install as background service:"
echo "   ./scripts/install_service.sh"
echo ""

