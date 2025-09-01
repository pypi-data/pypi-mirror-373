#!/bin/bash

# Default values
PYTHON_CMD="python"
VENV_NAME="test_env"
TEST_MODE="import"  # Options: import, tests, all
PACKAGE_NAME="nbqol"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --python=*)
      PYTHON_CMD="${1#*=}"
      shift
      ;;
    --venv=*)
      VENV_NAME="${1#*=}"
      shift
      ;;
    --mode=*)
      TEST_MODE="${1#*=}"
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --python=COMMAND   Specify Python command (e.g., python3.9, python3.10)"
      echo "  --venv=NAME        Specify virtual environment name"
      echo "  --mode=MODE        Specify test mode (import, tests, all)"
      echo "  --help, -h         Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo "Creating virtual environment '$VENV_NAME' using $PYTHON_CMD..."
$PYTHON_CMD -m venv $VENV_NAME
source $VENV_NAME/bin/activate

echo "Installing package in development mode..."
python -m pip install -e .

if [[ "$TEST_MODE" == "import" || "$TEST_MODE" == "all" ]]; then
  echo "Testing import..."
  python -c "import $PACKAGE_NAME; print(f'Package imported successfully')"
fi

if [[ "$TEST_MODE" == "tests" || "$TEST_MODE" == "all" ]]; then
  echo "Running tests..."
  python -m pytest
fi

echo "Deactivating virtual environment..."
deactivate

echo "Done!"