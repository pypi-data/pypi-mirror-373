#!/bin/bash
# Script to test GitHub Actions workflows locally using act

# Directory of this script and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "Error: 'act' is not installed."
    echo "To install act, run:"
    echo "  brew install act (macOS)"
    echo "  or visit https://github.com/nektos/act for other platforms"
    exit 1
fi

# Default values
WORKFLOW=""
EVENT=""
DRY_RUN=false  # Now defaults to actually running the workflow
SHOW_HELP=false
LIST_ONLY=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --workflow|-w)
            WORKFLOW="$2"
            shift 2
            ;;
        --event|-e)
            EVENT="$2"
            shift 2
            ;;
        --dry-run|-d)
            DRY_RUN=true
            shift
            ;;
        --list|-l)
            LIST_ONLY=true
            shift
            ;;
        --help|-h)
            SHOW_HELP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            SHOW_HELP=true
            shift
            ;;
    esac
done

# Show help text
if [ "$SHOW_HELP" = true ] || ([ -z "$WORKFLOW" ] && [ "$LIST_ONLY" = false ]); then
    echo "Usage: $0 [--list] [--workflow WORKFLOW_FILE] [--event EVENT_FILE] [--dry-run]"
    echo ""
    echo "Options:"
    echo "  --list, -l                     List all available workflows and jobs"
    echo "  --workflow, -w WORKFLOW_FILE   Workflow file to test (e.g. publish.yml)"
    echo "  --event, -e EVENT_FILE         Event file to use (without .json extension)"
    echo "  --dry-run, -d                  Show what would be executed without running it"
    echo "  --help, -h                     Show this help text"
    echo ""
    echo "Available workflows:"
    ls -1 .github/workflows/*.yml | sed 's|\.github/workflows/||'
    echo ""
    echo "Available event files:"
    ls -1 .github/workflows/test-events/*.json 2>/dev/null | sed 's|\.github/workflows/test-events/||' | sed 's|\.json$||' || echo "  No event files found"
    exit 0
fi

# Check if we're on an M-series Mac
IS_M_SERIES_MAC=false
if [[ "$(uname)" == "Darwin" && "$(uname -m)" == "arm"* ]]; then
    IS_M_SERIES_MAC=true
fi

# Build base command with common options
BASE_CMD=("act")

# Add architecture flag for M-series Macs
if [ "$IS_M_SERIES_MAC" = true ]; then
    BASE_CMD+=("--container-architecture" "linux/amd64")
    echo "Detected M-series Mac: Adding container architecture flag"
fi

# List mode - show all workflows and jobs
if [ "$LIST_ONLY" = true ]; then
    echo "Listing all workflows and jobs:"
    LIST_CMD=("${BASE_CMD[@]}" "--list" "-q")
    "${LIST_CMD[@]}" | grep -v "time=" | grep -v "level=" | column -t
    exit 0
fi

# Build workflow execution command
CMD=("${BASE_CMD[@]}" "--workflows" ".github/workflows/$WORKFLOW" "-q")

# Add event file if provided
if [ -n "$EVENT" ]; then
    EVENT_PATH=".github/workflows/test-events/${EVENT}.json"
    if [ -f "$EVENT_PATH" ]; then
        CMD+=("--eventpath" "$EVENT_PATH")
    else
        echo "Warning: Event file $EVENT_PATH not found"
    fi
fi

# Add dry run flag if requested
if [ "$DRY_RUN" = true ]; then
    CMD+=("--dryrun")
    echo "Dry run mode - showing what would be executed:"
else
    # Add privileged and bind flags for actual execution
    CMD+=("--privileged" "--bind")
    echo "Executing workflow: $WORKFLOW"
fi

# Run the command with filtered output
OUTPUT=$("${CMD[@]}" 2>&1)

# Filter output to remove common noise
FILTERED_OUTPUT=$(echo "$OUTPUT" | grep -v "time=" | grep -v "level=" | grep -v "Using docker host" | grep -v "You are using Apple M-series chip")

# Format as table if listing workflows
if [ "$LIST_ONLY" = true ]; then
    echo "$FILTERED_OUTPUT" | column -t
else
    echo "$FILTERED_OUTPUT"
fi