#!/bin/bash
# Unified script to build the package documentation
# Supports both direct Sphinx and Hatch-based builds

set -e  # Exit on error

# Directory of this script and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default options
BUILD_METHOD="sphinx"  # Options: sphinx, hatch
RUN_TESTS="none"       # Options: none, script, hatch

# Function to display usage information
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -m, --method           Build method: 'sphinx' (default) or 'hatch'"
    echo "  -t, --testing          Test approach: 'none' (default), 'script', or 'hatch'"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Build with Sphinx, no tests"
    echo "  $0 -m hatch            # Build with Hatch, no tests"
    echo "  $0 -m sphinx -t script # Build with Sphinx, run script tests"
    echo "  $0 -m hatch -t hatch   # Build with Hatch, run Hatch tests"
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--method)
            BUILD_METHOD="$2"
            shift 2
            ;;
        -t|--test)
            RUN_TESTS="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate options
if [[ "$BUILD_METHOD" != "sphinx" && "$BUILD_METHOD" != "hatch" ]]; then
    echo "Error: Invalid build method '$BUILD_METHOD'. Use 'sphinx' or 'hatch'."
    exit 1
fi

if [[ "$RUN_TESTS" != "none" && "$RUN_TESTS" != "script" && "$RUN_TESTS" != "hatch" ]]; then
    echo "Error: Invalid test approach '$RUN_TESTS'. Use 'none', 'script', or 'hatch'."
    exit 1
fi

# Check if Hatch is installed when needed
if [[ "$BUILD_METHOD" == "hatch" || "$RUN_TESTS" == "hatch" ]]; then
    if ! command -v hatch &> /dev/null; then
        echo "Error: Hatch is not installed."
        echo "To install Hatch, run: pip install hatch"
        exit 1
    fi
    
    # Create environments if needed
    echo "Setting up Hatch environments..."
    cd "$PROJECT_ROOT"
    hatch env create
fi

# Run tests if requested
if [[ "$RUN_TESTS" == "script" ]]; then
    echo "Running script-based tests..."
    # Add your script-based test commands here
    # For example: python tests/test_docs.py
elif [[ "$RUN_TESTS" == "hatch" ]]; then
    echo "Running Hatch-based tests..."
    cd "$PROJECT_ROOT"
    echo "Testing package installation..."
    hatch run test:python tests/test_installation.py
    echo "Testing documentation build..."
    hatch run test:python tests/test_docs_build.py
fi

# Build documentation
if [[ "$BUILD_METHOD" == "sphinx" ]]; then
    echo "Building documentation with Sphinx..."
    cd "$SCRIPT_DIR"
    
    # Clean previous build
    echo "Cleaning previous build..."
    make clean
    
    # Build the documentation
    echo "Building documentation..."
    make html
    
    echo "Documentation built successfully."
    echo "Open $SCRIPT_DIR/build/html/index.html to view the documentation."
elif [[ "$BUILD_METHOD" == "hatch" ]]; then
    echo "Building documentation with Hatch..."
    cd "$PROJECT_ROOT"
    hatch run docs:build
    
    echo "Documentation built successfully."
    echo "Open $SCRIPT_DIR/build/html/index.html to view the documentation."
fi 