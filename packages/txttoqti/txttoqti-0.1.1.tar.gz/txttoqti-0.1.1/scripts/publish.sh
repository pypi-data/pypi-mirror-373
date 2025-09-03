#!/bin/bash
# Secure publishing script using .env file

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 txttoqti Publishing Script${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo -e "${YELLOW}💡 Create .env file from .env.template:${NC}"
    echo "   cp .env.template .env"
    echo "   # Then edit .env with your API tokens"
    exit 1
fi

# Load environment variables from .env file
set -a  # Automatically export all variables
source .env
set +a

# Validate tokens are set
if [ -z "$TESTPYPI_TOKEN" ] || [ "$TESTPYPI_TOKEN" = "pypi-your-test-token-here" ]; then
    echo -e "${RED}❌ Error: TESTPYPI_TOKEN not set in .env file${NC}"
    exit 1
fi

if [ -z "$PYPI_TOKEN" ] || [ "$PYPI_TOKEN" = "pypi-your-production-token-here" ]; then
    echo -e "${YELLOW}⚠️  Warning: PYPI_TOKEN not set in .env file${NC}"
    echo -e "${YELLOW}   You can still publish to TestPyPI${NC}"
fi

# Build the package
echo -e "${BLUE}🔨 Building package...${NC}"
python3 -m build

# Check the package
echo -e "${BLUE}🔍 Checking package...${NC}"
python3 -m twine check dist/*

# Function to publish to TestPyPI
publish_test() {
    echo -e "${BLUE}📤 Publishing to TestPyPI...${NC}"
    export TWINE_USERNAME=__token__
    export TWINE_PASSWORD="$TESTPYPI_TOKEN"
    python3 -m twine upload --repository testpypi dist/*
    echo -e "${GREEN}✅ Published to TestPyPI successfully!${NC}"
    echo -e "${YELLOW}🔗 View at: https://test.pypi.org/project/txttoqti/${NC}"
}

# Function to publish to production PyPI
publish_prod() {
    if [ -z "$PYPI_TOKEN" ] || [ "$PYPI_TOKEN" = "pypi-your-production-token-here" ]; then
        echo -e "${RED}❌ Error: PYPI_TOKEN not set properly in .env file${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}⚠️  WARNING: This will publish to PRODUCTION PyPI!${NC}"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}📤 Publishing to Production PyPI...${NC}"
        export TWINE_USERNAME=__token__
        export TWINE_PASSWORD="$PYPI_TOKEN"
        python3 -m twine upload dist/*
        echo -e "${GREEN}✅ Published to Production PyPI successfully!${NC}"
        echo -e "${YELLOW}🔗 View at: https://pypi.org/project/txttoqti/${NC}"
    else
        echo -e "${YELLOW}📝 Publication cancelled${NC}"
    fi
}

# Parse command line arguments
case "${1:-}" in
    "test")
        publish_test
        ;;
    "prod")
        publish_prod
        ;;
    *)
        echo -e "${YELLOW}📋 Usage:${NC}"
        echo "  $0 test  - Publish to TestPyPI"
        echo "  $0 prod  - Publish to Production PyPI"
        echo ""
        echo -e "${YELLOW}🔧 Setup:${NC}"
        echo "  1. Copy .env.template to .env"
        echo "  2. Add your API tokens to .env"
        echo "  3. Run: $0 test"
        ;;
esac