#!/bin/bash

set -e

# Get the docs directory
DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$DOCS_DIR/source"

# Define the standard RST header hierarchy
HEADER_CHARS=('=' '-' '~' '"' "'" '.' '_' '*' '+' '^')

# Function to remove trailing whitespace
fix_trailing_whitespace() {
    local file="$1"
    local dry_run="$2"
    local temp_file="$(mktemp)"
    local changes_made=false
    
    # Process file and remove trailing whitespace
    if sed 's/[[:space:]]*$//' "$file" > "$temp_file"; then
        # Check if the files differ
        if ! cmp -s "$file" "$temp_file"; then
            changes_made=true
            if [[ "$dry_run" != "true" ]]; then
                echo "Removed trailing whitespace in $file"
                cat "$temp_file" > "$file"
            else
                echo "[DRY RUN] Would remove trailing whitespace in $file"
            fi
        fi
    fi
    
    # Clean up
    rm -f "$temp_file"
    
    # Return whether we made changes
    if [[ "$changes_made" == "true" ]]; then
        return 0
    else
        return 1
    fi
}

# Function to fix underlines in RST files
fix_rst_underlines() {
    local file="$1"
    local dry_run="$2"
    local temp_file="$(mktemp)"
    local changes_made=false
    
    # Process the file line by line
    local line_num=1
    local prev_line=""
    
    while IFS= read -r line; do
        # Write the current line to temp file
        echo "$line" >> "$temp_file"
        
        # Check if the current line consists only of underline characters (=, -, ~, etc.)
        if [[ "$line" =~ ^[=\-~\^\"\'\.\_\*\+\#\:\<\>]+$ ]]; then
            # Get the character used for underlining
            underline_char="${line:0:1}"
            
            # Get the length of the previous line (header)
            prev_length=${#prev_line}
            
            # Get the length of the current line (underline)
            underline_length=${#line}
            
            # If lengths don't match, fix the underline
            if [[ $prev_length -ne $underline_length ]]; then
                changes_made=true
                # Create new underline with correct length
                new_underline=$(printf "%${prev_length}s" | tr ' ' "$underline_char")
                
                # Replace the last line in the temp file with the new underline
                sed -i.bak "$ s/.*/$new_underline/" "$temp_file"
                
                if [[ "$dry_run" != "true" ]]; then
                    echo "Fixed underline in $file (line $line_num)"
                    echo "  Header: \"$prev_line\""
                    echo "  Old underline: \"$line\" (length: $underline_length)"
                    echo "  New underline: \"$new_underline\" (length: $prev_length)"
                else
                    echo "[DRY RUN] Would fix underline in $file (line $line_num)"
                    echo "  Header: \"$prev_line\""
                    echo "  Old underline: \"$line\" (length: $underline_length)"
                    echo "  New underline: \"$new_underline\" (length: $prev_length)"
                fi
            fi
        fi
        
        # Store current line for next iteration
        prev_line="$line"
        line_num=$((line_num + 1))
    done < "$file"
    
    # If we made changes and this is not a dry run, update the original file
    if [[ "$changes_made" == "true" && "$dry_run" != "true" ]]; then
        cat "$temp_file" > "$file"
    fi
    
    # Clean up
    rm -f "$temp_file" "$temp_file.bak"
    
    # Return whether we made changes
    if [[ "$changes_made" == "true" ]]; then
        return 0
    else
        return 1
    fi
}

# Function to check and suggest header hierarchy consistency
check_header_hierarchy() {
    local file="$1"
    local dry_run="$2"
    local changes_made=false
    
    # Create temporary files
    local temp_file="$(mktemp)"
    local headers_file="$(mktemp)"
    
    # Extract headers with their underline character and line number
    awk '
    {
        line = $0;
        line_num = NR;
        
        # If line matches an underline pattern
        if ($0 ~ /^[=\-~\^"'\''\.\_\*\+\#\:\<\>]+$/ && NR > 1) {
            # Get the character used for underlining
            underline_char = substr($0, 1, 1);
            
            # Previous line is the header text
            printf "%s|%s|%d\n", prev_line, underline_char, line_num - 1;
        }
        
        # Store current line for next iteration
        prev_line = line;
    }
    ' "$file" > "$headers_file"
    
    # Display headers and hierarchy warnings if any
    if [[ -s "$headers_file" ]]; then
        # Track seen characters and their levels
        local seen_chars=""
        local seen_levels=""
        local current_depth=0
        local prev_char=""
        local issue_found=false
        
        # Process each header
        while IFS='|' read -r header_text char line_num; do
            # Check if we've seen this character before
            local char_level=""
            local i=0
            local found=false
            
            # Look for the character in our seen_chars list
            for c in $seen_chars; do
                if [[ "$c" == "$char" ]]; then
                    # Get the corresponding level
                    char_level=$(echo "$seen_levels" | cut -d' ' -f$((i+1)))
                    found=true
                    break
                fi
                i=$((i+1))
            done
            
            # If we haven't seen this character, assign it the next level
            if [[ "$found" != "true" ]]; then
                # This is a new header character
                if [[ -z "$prev_char" ]]; then
                    # First header should use character at index 0
                    if [[ "$char" != "${HEADER_CHARS[0]}" ]]; then
                        issue_found=true
                        if [[ "$dry_run" != "true" ]]; then
                            echo "HIERARCHY WARNING in $file (line $line_num)"
                            echo "  Header: \"$header_text\""
                            echo "  Uses character '$char' but document's first header should use '${HEADER_CHARS[0]}'"
                        else
                            echo "[DRY RUN] HIERARCHY WARNING in $file (line $line_num)"
                            echo "  Header: \"$header_text\""
                            echo "  Uses character '$char' but document's first header should use '${HEADER_CHARS[0]}'"
                        fi
                    fi
                    char_level=0
                else
                    # For new levels, character should be next in hierarchy
                    local prev_level=0
                    
                    # Find the level of the previous character
                    i=0
                    for c in $seen_chars; do
                        if [[ "$c" == "$prev_char" ]]; then
                            prev_level=$(echo "$seen_levels" | cut -d' ' -f$((i+1)))
                            break
                        fi
                        i=$((i+1))
                    done
                    
                    local next_level=$((prev_level + 1))
                    
                    # Only check if there's a next character in our hierarchy
                    if [[ $next_level -lt ${#HEADER_CHARS[@]} ]]; then
                        local expected_char="${HEADER_CHARS[$next_level]}"
                        
                        if [[ "$char" != "$expected_char" ]]; then
                            issue_found=true
                            if [[ "$dry_run" != "true" ]]; then
                                echo "HIERARCHY WARNING in $file (line $line_num)"
                                echo "  Header: \"$header_text\""
                                echo "  Uses character '$char' but should use '$expected_char' for proper hierarchy"
                            else
                                echo "[DRY RUN] HIERARCHY WARNING in $file (line $line_num)"
                                echo "  Header: \"$header_text\""
                                echo "  Uses character '$char' but should use '$expected_char' for proper hierarchy"
                            fi
                        fi
                    fi
                    
                    char_level=$next_level
                fi
                
                # Add this character and its level to our tracking lists
                seen_chars="$seen_chars $char"
                seen_levels="$seen_levels $char_level"
            fi
            
            prev_char="$char"
        done < "$headers_file"
        
        if [[ "$issue_found" == "true" ]]; then
            changes_made=true
            echo "Standard RST header hierarchy: ${HEADER_CHARS[*]}"
        fi
    fi
    
    # Clean up
    rm -f "$temp_file" "$headers_file"
    
    # Return whether we found issues
    if [[ "$changes_made" == "true" ]]; then
        return 0
    else
        return 1
    fi
}

# Parse arguments
DRY_RUN=false
VERBOSE=false

for arg in "$@"; do
    if [[ "$arg" == "--dry-run" ]]; then
        DRY_RUN=true
    elif [[ "$arg" == "--verbose" ]]; then
        VERBOSE=true
    elif [[ "$arg" == "--help" ]]; then
        echo "Usage: $0 [--dry-run] [--verbose] [--help]"
        echo ""
        echo "Options:"
        echo "  --dry-run    Show what would be fixed without making changes"
        echo "  --verbose    Show detailed information about each file"
        echo "  --help       Show this help message"
        exit 0
    else
        echo "Unknown option: $arg"
        echo "Usage: $0 [--dry-run] [--verbose] [--help]"
        exit 1
    fi
done

# Find all RST files in the source directory
echo "Checking RST files in $SOURCE_DIR"
RST_FILES=$(find "$SOURCE_DIR" -name "*.rst")

# Initialize counters
FIXED_FILES=0
ALREADY_CORRECT=0

# Process each RST file
for file in $RST_FILES; do
    if [[ "$VERBOSE" == "true" ]]; then
        echo "Checking $file..."
    fi
    
    # Track if any fixes were made to this file
    file_fixed=false
    
    # Check for trailing whitespace
    if fix_trailing_whitespace "$file" "$DRY_RUN"; then
        file_fixed=true
    fi
    
    # Check for RST underline issues
    if fix_rst_underlines "$file" "$DRY_RUN"; then
        file_fixed=true
    fi
    
    # Check for header hierarchy issues
    if check_header_hierarchy "$file" "$DRY_RUN"; then
        file_fixed=true
    fi
    
    # Update counters
    if [[ "$file_fixed" == "true" ]]; then
        FIXED_FILES=$((FIXED_FILES + 1))
    else
        ALREADY_CORRECT=$((ALREADY_CORRECT + 1))
        if [[ "$VERBOSE" == "true" ]]; then
            echo "  No issues found"
        fi
    fi
done

# Show summary
if [[ "$DRY_RUN" == "true" ]]; then
    echo "DRY RUN SUMMARY: Would fix $FIXED_FILES files, $ALREADY_CORRECT files already formatted correctly"
else
    echo "SUMMARY: Fixed $FIXED_FILES files, $ALREADY_CORRECT files already formatted correctly"
fi

exit 0 