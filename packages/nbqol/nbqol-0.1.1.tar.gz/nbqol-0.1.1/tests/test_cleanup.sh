#!/bin/bash

set -e

TARGETS=("dist" "build" "__pycache__" "*.egg-info" ".pytest_cache" ".coverage" "htmlcov" ".venv")
KEEP=()
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep)
      KEEP+=("$2")
      shift 2
      ;;
    --keep=*)
      KEEP+=("${1#*=}")
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--keep <pattern>] [--dry-run]"
      exit 1
      ;;
  esac
done

# Function to check if an item should be kept
should_keep() {
  local item="$1"
  for keep_pattern in "${KEEP[@]}"; do
    if [[ "$item" == *"$keep_pattern"* ]]; then
      return 0  # True, should keep
    fi
  done
  return 1  # False, should not keep
}

# Get project root directory (assuming script is in tests/ directory)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Find all items to delete
ITEMS_TO_DELETE=()
for target in "${TARGETS[@]}"; do
  # Use find to locate all matching items
  while IFS= read -r item; do
    # Skip if empty (find returns nothing)
    if [[ -z "$item" ]]; then
      continue
    fi
    
    # Check if this item should be kept
    if ! should_keep "$item"; then
      ITEMS_TO_DELETE+=("$item")
    fi
  done < <(find . -name "$target" -type d -o -name "$target" -type f 2>/dev/null || true)
done

# Nothing to delete
if [ ${#ITEMS_TO_DELETE[@]} -eq 0 ]; then
  echo "No items found to delete."
  exit 0
fi

# List what will be deleted
echo "The following will be deleted:"
for item in "${ITEMS_TO_DELETE[@]}"; do
  echo "  $item"
done

# In dry-run mode, stop here
if [ "$DRY_RUN" = true ]; then
  echo "Dry run completed. No files were deleted."
  exit 0
fi

# Ask for confirmation
read -p "Are you sure you want to delete these items? (y/N) " answer
if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
  echo "Cleanup cancelled."
  exit 0
fi

# Delete the items
for item in "${ITEMS_TO_DELETE[@]}"; do
  echo "Deleting $item"
  rm -rf "$item"
done

echo "Cleanup completed."