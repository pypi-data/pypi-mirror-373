#!/bin/bash
# Script to build documentation and start a preview server
# Supports both static and live-reloading preview modes

set -e  # Exit on error

# Directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default options
LIVE_RELOAD=true
PORT=8000
BUILD_ARGS=""

# Source directories from Makefile
SOURCEDIR="source"
BUILDDIR="build"
CONFDIR="$SCRIPT_DIR"

# Function to display usage information
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -l, --live BOOL        Enable live reloading: 'true' (default) or 'false'"
    echo "  -p, --port PORT        Port to use for the preview server (default: 8000)"
    echo "  -b, --build-args ARGS  Additional arguments to pass to the build script"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Live preview on port 8000"
    echo "  $0 -l false            # Static preview on port 8000"
    echo "  $0 -p 8080             # Live preview on port 8080"
    echo "  $0 -b \"-m hatch\"      # Live preview with hatch build method"
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--live)
            LIVE_RELOAD="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -b|--build-args)
            BUILD_ARGS="$2"
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
if [[ "$LIVE_RELOAD" != "true" && "$LIVE_RELOAD" != "false" ]]; then
    echo "Error: Invalid live reload option '$LIVE_RELOAD'. Use 'true' or 'false'."
    exit 1
fi

# Clean previous build
echo "Cleaning previous build..."
make clean

# If live reload is enabled, use sphinx-autobuild
if [[ "$LIVE_RELOAD" == "true" ]]; then
    # Check if sphinx-autobuild is available
    if ! command -v sphinx-autobuild &> /dev/null; then
        echo "sphinx-autobuild not found. Installing..."
        pip install sphinx-autobuild
    fi
    
    echo "Starting live preview server with sphinx-autobuild..."
    echo "Open http://localhost:$PORT/ in your browser to view the documentation."
    echo "The page will automatically reload when you make changes to the source files."
    echo "Press Ctrl+C to stop the server."
    echo ""
    
    # Start the live-reloading server using the same format as in Makefile
    sphinx-autobuild "$SOURCEDIR" "$BUILDDIR/html" -c "$CONFDIR" --port $PORT --open-browser
else
    # Build the documentation first
    echo "Building documentation..."
    ./build.sh $BUILD_ARGS
    
    # Check if python is available
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not available. Cannot start preview server."
        exit 1
    fi
    
    # Start a local server to preview the documentation
    echo ""
    echo "Starting local preview server..."
    echo "Open http://localhost:$PORT/ in your browser to view the documentation."
    echo "Press Ctrl+C to stop the server."
    echo ""
    
    # Change to the build directory and start the server
    cd "$BUILDDIR/html"
    python -m http.server $PORT
fi 