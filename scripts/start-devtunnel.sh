#!/bin/bash

set -e

# Configuration
PORT="${DEVTUNNEL_PORT:-8080}"
TUNNEL_ID="${DEVTUNNEL_ID:-}"
ALLOW_ANONYMOUS="${DEVTUNNEL_ALLOW_ANONYMOUS:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚇 Microsoft DevTunnel Setup Script${NC}"
echo ""

# Function to check if devtunnel is installed
check_devtunnel_installed() {
    if command -v devtunnel &> /dev/null; then
        echo -e "${GREEN}✓${NC} devtunnel is installed"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} devtunnel is not installed"
        return 1
    fi
}

# Function to install devtunnel
install_devtunnel() {
    echo -e "${BLUE}📦 Installing devtunnel...${NC}"
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Installing for Linux..."
        curl -sL https://aka.ms/DevTunnelCliInstall | bash
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing for macOS..."
        brew install --cask devtunnel
    else
        echo -e "${RED}✗${NC} Unsupported operating system: $OSTYPE"
        echo "Please install devtunnel manually from: https://aka.ms/devtunnels/download"
        exit 1
    fi
    
    # Verify installation
    if command -v devtunnel &> /dev/null; then
        echo -e "${GREEN}✓${NC} devtunnel installed successfully"
    else
        echo -e "${RED}✗${NC} Installation failed. Please install manually."
        exit 1
    fi
}

# Function to check if user is logged in
check_login() {
    if devtunnel user show &> /dev/null; then
        USER_INFO=$(devtunnel user show 2>&1)
        echo -e "${GREEN}✓${NC} Already logged in to devtunnel"
        echo "$USER_INFO"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Not logged in to devtunnel"
        return 1
    fi
}

# Function to login to devtunnel
login_devtunnel() {
    echo -e "${BLUE}🔐 Logging in to devtunnel...${NC}"
    echo "This will open a browser window for authentication."
    echo ""
    
    if devtunnel user login; then
        echo -e "${GREEN}✓${NC} Login successful"
        devtunnel user show
    else
        echo -e "${RED}✗${NC} Login failed"
        exit 1
    fi
}

# Function to create or use existing tunnel
setup_tunnel() {
    echo ""
    echo -e "${BLUE}🔧 Setting up tunnel...${NC}"
    
    if [ -n "$TUNNEL_ID" ]; then
        echo "Using existing tunnel ID: $TUNNEL_ID"
        TUNNEL="$TUNNEL_ID"
    else
        echo "Creating a new tunnel..."
        # Create a new temporary tunnel
        TUNNEL_OUTPUT=$(devtunnel create -a 2>&1)
        TUNNEL=$(echo "$TUNNEL_OUTPUT" | grep "Tunnel ID" | awk '{print $4}')
        echo -e "${GREEN}✓${NC} Created tunnel: $TUNNEL"
    fi
    
    # Add port
    echo "Configuring port $PORT..."
    if devtunnel port create "$TUNNEL" -p "$PORT" &> /dev/null; then
        echo -e "${GREEN}✓${NC} Port $PORT configured"
    else
        # Port might already exist, continue anyway
        echo -e "${YELLOW}⚠${NC} Port $PORT already configured or couldn't be added"
    fi
    
    # Set anonymous access if requested
    if [ "$ALLOW_ANONYMOUS" = "true" ]; then
        echo "Enabling anonymous access..."
        devtunnel access create "$TUNNEL" -a &> /dev/null || true
        echo -e "${GREEN}✓${NC} Anonymous access enabled"
    fi
    
    echo ""
    echo -e "${GREEN}✓${NC} Tunnel setup complete"
    echo ""
}

# Function to start the tunnel
start_tunnel() {
    echo -e "${BLUE}🚀 Starting tunnel on port $PORT...${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the tunnel${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Host the tunnel (port is already configured during setup)
    devtunnel host "$TUNNEL" --allow-anonymous
}

# Main execution
main() {
    # Check if devtunnel is installed
    if ! check_devtunnel_installed; then
        read -p "Would you like to install devtunnel? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_devtunnel
        else
            echo -e "${RED}✗${NC} devtunnel is required. Exiting."
            exit 1
        fi
    fi
    
    echo ""
    
    # Check if logged in
    if ! check_login; then
        echo ""
        read -p "Would you like to login now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            login_devtunnel
        else
            echo -e "${RED}✗${NC} Login is required. Exiting."
            exit 1
        fi
    fi
    
    # Setup and start tunnel
    setup_tunnel
    start_tunnel
}

# Run main function
main
