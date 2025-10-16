#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

# Check if repository URL argument is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}✗${NC} Error: Repository URL is required"
    echo ""
    echo "Usage: $0 <github-repo-url>"
    echo ""
    echo "Examples:"
    echo "  $0 https://github.com/owner/repo"
    echo "  $0 git@github.com:owner/repo.git"
    echo "  $0 owner/repo"
    echo ""
    exit 1
fi

REPO_URL="$1"

# Extract owner and repo from URL
# Supports formats: https://github.com/owner/repo, git@github.com:owner/repo.git, owner/repo
if [[ "$REPO_URL" =~ github\.com[:/]([^/]+)/([^/\.]+) ]]; then
    REPO_OWNER="${BASH_REMATCH[1]}"
    REPO_NAME="${BASH_REMATCH[2]}"
    REPO_FULL_NAME="$REPO_OWNER/$REPO_NAME"
elif [[ "$REPO_URL" =~ ^([^/]+)/([^/]+)$ ]]; then
    REPO_FULL_NAME="$REPO_URL"
    REPO_OWNER="${BASH_REMATCH[1]}"
    REPO_NAME="${BASH_REMATCH[2]}"
else
    echo -e "${RED}✗${NC} Error: Invalid repository URL format"
    echo ""
    echo "Supported formats:"
    echo "  - https://github.com/owner/repo"
    echo "  - git@github.com:owner/repo.git"
    echo "  - owner/repo"
    echo ""
    exit 1
fi

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}GitHub Webhook Development Setup${NC}                      ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Repository:${NC} $REPO_FULL_NAME"
echo ""

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠${NC} .env file not found. Creating from .env.sample..."
    if [ -f "$PROJECT_ROOT/.env.sample" ]; then
        cp "$PROJECT_ROOT/.env.sample" "$ENV_FILE"
        echo -e "${GREEN}✓${NC} Created .env file"
        echo ""
        echo -e "${YELLOW}⚠${NC} Please edit .env and add your GITHUB_WEBHOOK_SECRET"
        echo "   Generate one with: ${CYAN}openssl rand -hex 32${NC}"
        echo ""
        exit 1
    else
        echo -e "${RED}✗${NC} .env.sample not found"
        exit 1
    fi
fi

# Source the .env file to check webhook secret
source "$ENV_FILE"

if [ -z "$GITHUB_WEBHOOK_SECRET" ] || [ "$GITHUB_WEBHOOK_SECRET" = "your_webhook_secret_here" ]; then
    echo -e "${RED}✗${NC} GITHUB_WEBHOOK_SECRET not set in .env"
    echo "   Generate one with: ${CYAN}openssl rand -hex 32${NC}"
    echo "   Then add it to $ENV_FILE"
    echo ""
    exit 1
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}✗${NC} GitHub CLI (gh) is not installed"
    echo "   Install it from: https://cli.github.com/"
    echo ""
    exit 1
fi

# Check if gh CLI is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}✗${NC} GitHub CLI is not authenticated"
    echo "   Run: ${CYAN}gh auth login${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} Environment configured"
echo ""

# Create a temporary file to store the devtunnel URL
DEVTUNNEL_LOG_FILE=$(mktemp)
trap "rm -f $DEVTUNNEL_LOG_FILE" EXIT

# Start devtunnel in background and capture its URL
echo -e "${BLUE}Step 1:${NC} Starting DevTunnel..."
echo ""

# Start devtunnel in background
"$SCRIPT_DIR/start-devtunnel.sh" > "$DEVTUNNEL_LOG_FILE" 2>&1 &
DEVTUNNEL_PID=$!

# Give it time to initialize and display the URL
sleep 5

# Extract the HTTPS URL from the devtunnel output
DEVTUNNEL_URL=""
for i in {1..20}; do
    if [ -f "$DEVTUNNEL_LOG_FILE" ]; then
        # Look for the Connect via browser line with the URL without port
        DEVTUNNEL_URL=$(grep -oP 'https://[a-z0-9-]+\.use\d\.devtunnels\.ms(?=,|$)' "$DEVTUNNEL_LOG_FILE" | head -1)
        if [ -n "$DEVTUNNEL_URL" ]; then
            break
        fi
    fi
    sleep 1
done

if [ -z "$DEVTUNNEL_URL" ]; then
    echo -e "${RED}✗${NC} Failed to extract DevTunnel URL"
    echo "   Check the DevTunnel output:"
    cat "$DEVTUNNEL_LOG_FILE"
    kill $DEVTUNNEL_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓${NC} DevTunnel started: ${CYAN}$DEVTUNNEL_URL${NC}"
echo ""

# Configure GitHub webhook
echo -e "${BLUE}Step 2:${NC} Configuring GitHub webhook..."
echo ""

WEBHOOK_URL="${DEVTUNNEL_URL}/webhook"

# Check if webhook already exists
EXISTING_WEBHOOKS=$(gh api "repos/$REPO_FULL_NAME/hooks" --jq '.[].config.url' 2>/dev/null || echo "")

if echo "$EXISTING_WEBHOOKS" | grep -q "$WEBHOOK_URL"; then
    echo -e "${YELLOW}⚠${NC} Webhook already exists for this URL"
else
    # Create the webhook
    gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        "repos/$REPO_FULL_NAME/hooks" \
        -f name='web' \
        -f "config[url]=$WEBHOOK_URL" \
        -f config[content_type]='json' \
        -f "config[secret]=$GITHUB_WEBHOOK_SECRET" \
        -f config[insecure_ssl]='0' \
        -f events[]='issues' \
        -F active=true \
        > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Webhook created successfully"
    else
        echo -e "${YELLOW}⚠${NC} Failed to create webhook (may need manual setup)"
        echo "   You can create it manually at:"
        echo "   https://github.com/$REPO_FULL_NAME/settings/hooks"
    fi
fi

echo -e "  ${CYAN}URL:${NC} $WEBHOOK_URL"
echo -e "  ${CYAN}Events:${NC} issues"
echo ""

# Start the webhook server
echo -e "${BLUE}Step 3:${NC} Starting webhook server..."
echo ""

cd "$PROJECT_ROOT"
uv run src/webhook.py &
WEBHOOK_PID=$!

# Wait a moment for the server to start
sleep 3

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  ${GREEN}✓${NC} Development environment is ready!                     ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Repository:${NC}      $REPO_FULL_NAME"
echo -e "${CYAN}Webhook URL:${NC}     $WEBHOOK_URL"
echo -e "${CYAN}Events:${NC}          issues"
echo ""
echo -e "${YELLOW}Test by creating an issue in your repository!${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both DevTunnel and webhook server${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${BLUE}Shutting down...${NC}"
    kill $WEBHOOK_PID 2>/dev/null || true
    kill $DEVTUNNEL_PID 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $WEBHOOK_PID $DEVTUNNEL_PID
