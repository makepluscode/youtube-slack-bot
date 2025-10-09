#!/bin/bash
#
# Install script for YouTube Download Agent launchd service
# This script configures and installs the bot as a background service on macOS
#

set -e  # Exit on error

echo "================================================"
echo "YouTube Download Agent - Service Installation"
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

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create .env file first:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Please run setup.sh first:"
    echo "   ./scripts/setup.sh"
    exit 1
fi

# Paths
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
PLIST_TEMPLATE="$PROJECT_DIR/services/com.makepluscode.youtube-downloader.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.makepluscode.youtube-downloader.plist"

# Check if template exists
if [ ! -f "$PLIST_TEMPLATE" ]; then
    echo -e "${RED}❌ plist template not found: $PLIST_TEMPLATE${NC}"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Replace placeholders in plist file
echo "Creating plist configuration..."
sed -e "s|PLACEHOLDER_VENV_PATH|$PROJECT_DIR/.venv|g" \
    -e "s|PLACEHOLDER_PROJECT_PATH|$PROJECT_DIR|g" \
    -e "s|PLACEHOLDER_HOME|$HOME|g" \
    "$PLIST_TEMPLATE" > "$PLIST_DEST"

echo -e "${GREEN}✅ Created plist file: $PLIST_DEST${NC}"

# Unload existing service if running
if launchctl list | grep -q "com.makepluscode.youtube-downloader"; then
    echo "Stopping existing service..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# Load the service
echo "Loading service..."
launchctl load "$PLIST_DEST"

# Give it a moment to start
sleep 2

# Check if service is running
if launchctl list | grep -q "com.makepluscode.youtube-downloader"; then
    echo -e "${GREEN}✅ Service installed and running!${NC}"
else
    echo -e "${YELLOW}⚠️  Service installed but may not be running${NC}"
    echo "Check logs for errors:"
    echo "   tail -f $PROJECT_DIR/logs/stderr.log"
fi

echo ""
echo "================================================"
echo "Service Management Commands"
echo "================================================"
echo ""
echo "Check status:"
echo "  launchctl list | grep youtube-downloader"
echo ""
echo "View logs:"
echo "  tail -f $PROJECT_DIR/logs/app.log"
echo "  tail -f $PROJECT_DIR/logs/stderr.log"
echo ""
echo "Stop service:"
echo "  launchctl unload $PLIST_DEST"
echo ""
echo "Start service:"
echo "  launchctl load $PLIST_DEST"
echo ""
echo "Restart service:"
echo "  launchctl unload $PLIST_DEST && launchctl load $PLIST_DEST"
echo ""

