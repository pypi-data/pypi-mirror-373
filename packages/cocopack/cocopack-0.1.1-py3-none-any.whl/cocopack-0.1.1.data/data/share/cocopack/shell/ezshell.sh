#!/bin/bash

# General Helpers ---------------------------------------------------

show_symlinks() {
    find . -maxdepth 1 -type l -not -path '*snapshot*' -ls
}

# Function to show storage usage of files and directories in the current directory
show_storage() {
    find . -maxdepth 1 -exec du -sh "{}" \; | sort -h
}

make_hidden() {
    local target_path=$1
    local dir_name=$(dirname "$target_path")
    local base_name=$(basename "$target_path")

    # Check if the file or folder exists
    if [[ -e $target_path ]]; then
        # Rename the file or folder to make it hidden
        mv "$target_path" "$dir_name/.$base_name"
        echo "Hidden: $dir_name/.$base_name"
    else
        echo "Error: $target_path does not exist."
    fi
}

safe_rename() {
    local old_path=$1
    local new_path=$2
    local search_dir=${3:-~} 
    # default home, / for root

    # Check if the original file/directory exists
    if [[ ! -e $old_path ]]; then
        echo "Error: $old_path does not exist."
        return 1
    fi

    # Rename the file or directory
    mv "$old_path" "$new_path"

    # Find and update symlinks in the specified directory
    find "$search_dir" -type l 2>/dev/null | while read symlink; do
        # Check if the symlink points to the old path
        if [[ $(readlink "$symlink") == $old_path* ]]; then
            # Compute the new target path
            local old_target=$(readlink "$symlink")
            local new_target=${old_target/#$old_path/$new_path}

            # Update the symlink
            ln -snf "$new_target" "$symlink"
            echo "Updated symlink: $symlink -> $new_target"
        fi
    done
}

move_with_symlink() {
    local src=$1
    local dst=$2

    # Check if the source file/directory exists
    if [[ ! -e $src ]]; then
        echo "Error: Source $src does not exist."
        return 1
    fi

    # Move the file or directory
    mv "$src" "$dst"

    # Check if the move was successful
    if [[ ! -e $dst ]]; then
        echo "Error: Failed to move $src to $dst."
        return 1
    fi

    # Create a symlink from the original source location to the new destination
    ln -s "$dst" "$src"
    echo "Moved $src to $dst and created a symlink."
}

# quickly change into a subdir
recursive_cd_subdir() {
  local target="$1"
  local source="$(pwd)"
  local fuzzy=0 # Fuzzy search is disabled by default

  # Process arguments
  for arg in "$@"; do
    case "$arg" in
      --fuzzy) fuzzy=1 ;;
      *) if [ -d "$arg" ] || [ -z "$start_dir" ]; then source="$arg"; fi ;;
    esac
  done

  # Perform search based on fuzzy flag
  if [ "$fuzzy" -eq 1 ]; then
    local target_dir=$(find "$source" -type d -name "*$target*" -print -quit)
  else
    local target_dir=$(find "$source" -type d -name "$target" -print -quit)
  fi

  if [ -n "$target_dir" ]; then
    cd "$target_dir" || return
    echo "Changing directory to $target_dir ($target)"
  else
    echo "No directory found matching target: $target"
  fi
}

rcd() {
  local target="$1"
  local source="$(pwd)"

  recursive_cd_subdir $target $source
}

rcdf() {
  local target="$1"
  local source="$(pwd)"

  recursive_cd_subdir $target $source --fuzzy
}

safe_remove() {
    local target_path="$1"
    local recursive="${2:-true}"  # Default to true if not specified

    # Check if the target path is provided
    if [[ -z "$target_path" ]]; then
        echo "No path provided. Exiting."
        exit 1
    fi

    # Prevent removal of the home directory alone
    if [[ "$target_path" == "$HOME" || "$target_path" == "$HOME/" ]]; then
        echo "Dangerous operation blocked: You cannot remove the home directory."
        exit 1
    fi

    # Check if the target directory exists
    if [[ ! -e "$target_path" ]]; then
        echo "The specified path does not exist."
        exit 1
    fi

    # Display the files and directories that will be removed
    echo "The following items will be removed from '$target_path':"
    find "$target_path" -mindepth 1

    # Ask for user confirmation
    read -p "Are you sure you want to remove the above items? [yes/no] " response
    case "$response" in
        [yY][eE][sS]|[yY])
            if [[ "$recursive" == "true" ]]; then
                rm -rf "$target_path"/*
            else
                rm -f "$target_path"/*
            fi
            echo "Items removed successfully."
            ;;
        *)
            echo "Operation cancelled."
            ;;
    esac
}

saferm() {
    local target_path="$1"
    local recursive="${2:-true}"

    safe_remove $target_path $recursive

}

# function to split PATH into an array
split_path() {
    if (IFS=':' read -r -a path_array <<< "$PATH") 2>/dev/null; then :
    elif [ -n "$ZSH_VERSION" ]; then
        IFS=':' read -r -A path_array <<< "$PATH"
    else
        OLD_IFS="$IFS"
        IFS=':'
        path_array=($PATH)
        IFS="$OLD_IFS"
    fi
}

# function to clean extraneous PATH entries
path_cleanup() {
    local remove_duplicates=true
    local remove_empties=false
    local remove_missing=false
    local keep_first_entry=true

    local dry_run=true
    local verbose=true
    local ignore_patterns=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            --remove-duplicates)
                remove_duplicates=true
                ;;
            --remove-empties)
                remove_empties=true
                ;;
            --remove-missing)
                remove_missing=true
                ;;
            --keep-duplicates)
                remove_duplicates=false
                ;;
            --keep-empties)
                remove_empties=false
                ;;
            --keep-missing)
                remove_missing=false
                ;;
            --keep-first-entry)
                keep_first_entry=true
                ;;
            --keep-last-entry)
                keep_first_entry=false
                ;;
            --apply)
                dry_run=false
                ;;
            --quiet)
                verbose=false
                ;;
            --ignore)
                shift
                ignore_patterns+=("$1")
                ;;
            *)
                echo "Unknown argument: $1"
                return 1
                ;;
        esac
        shift
    done

    split_path # using the custom function above

    # Function to check if the path should be ignored
    should_ignore() {
        local path=$1
        for pattern in "${ignore_patterns[@]}"; do
            if [[ $path =~ $pattern ]]; then
                return 0 # Should ignore
            fi
        done
        return 1 # Should not ignore
    }

    # arrays to store removals:
    local removed_duplicates=()
    local removed_empties=()
    local removed_missing=()
    local updated_path_array=()

    # Remove duplicate entries:
    if $remove_duplicates; then
        local unique_paths=()
        local seen=()
        if $keep_first_entry; then
            for entry in "${path_array[@]}"; do
                if [[ ! " ${seen[*]} " =~ " $entry " ]] \
                && ! should_ignore "$entry"; then
                    unique_paths+=("$entry")
                    seen+=("$entry")
                elif should_ignore "$entry"; then
                    unique_paths+=("$entry")
                else
                    removed_duplicates+=("$entry")
                fi
            done
        else
            for ((i=${#path_array[@]}-1; i>=0; i--)); do
                entry="${path_array[i]}"
                if [[ ! " ${seen[*]} " =~ " $entry " ]] \
                && ! should_ignore "$entry"; then
                    unique_paths=("$entry" "${unique_paths[@]}")
                    seen+=("$entry")
                elif should_ignore "$entry"; then
                    unique_paths=("$entry" "${unique_paths[@]}")
                else
                    removed_duplicates+=("$entry")
                fi
            done
        fi
        updated_path_array=("${unique_paths[@]}")
    fi

    # Filter out empty + missing, if not ignored
    for entry in "${updated_path_array[@]}"; do
        if $remove_empties && [ -z "$entry" ] \
        && ! should_ignore "$entry"; then
            removed_empties+=("$entry")
        elif $remove_missing && [ ! -d "$entry" ] \
        && ! should_ignore "$entry"; then
            removed_missing+=("$entry")
        else
            path_array+=("$entry")
        fi
    done

    if ! $dry_run; then
        path_array=("${updated_path_array[@]}")
    fi

    # Print removal reports if in verbose or dry_run mode
    run_status="(Dry Run) Removing"
    if ! $dry_run; then
        run_status="Removing"
    fi

    if $verbose || $dry_run; then
        for entry in "${removed_duplicates[@]}"; do
            echo "$run_status duplicate: $entry"
        done
        for entry in "${removed_empties[@]}"; do
            echo "$run_status empty: $entry"
        done
        for entry in "${removed_missing[@]}"; do
            echo "$run_status missing: $entry"
        done

        end_message="Path cleanup complete."

        # if length of entries is zero, alert user
        if [ ${#removed_duplicates[@]} -eq 0 ] && \
            [ ${#removed_empties[@]} -eq 0 ] && \
            [ ${#removed_missing[@]} -eq 0 ]; then
            end_message+=" No entries removed."; fi

        echo $end_message

    fi

    # Reconstruct the PATH variable if not in dry run mode
    if ! $dry_run; then
        PATH=$(IFS=':'; echo "${path_array[*]}")
        export PATH
    fi
}

print_python_versions() {
    # Default packages to check if no arguments are given
    local default_packages=("torch" "numpy" "pandas" "sklearn")
    local packages=()
    local conda_env=""

    # Parse arguments for packages and conda_env
    for arg in "$@"; do
        if [[ "$arg" =~ ^conda_env= ]]; then
            conda_env="${arg#*=}"
        else
            packages+=("$arg")
        fi
    done

    # If no package arguments are provided, use the default packages
    if [ ${#packages[@]} -eq 0 ]; then
        packages=("${default_packages[@]}")
    fi

    # If conda_env is specified, activate it
    if [[ -n "$conda_env" ]]; then
        echo "Activating Conda environment: $conda_env"
        source activate "$conda_env"
    fi

    # Print the Python version
    local python_version=$(python --version 2>&1)
    echo "Python version: $python_version"

    echo "Checking versions of installed Python packages..."
    echo "-----------------------------------------------"

    # Loop through the list of packages and print their versions using Python
    for pkg in "${packages[@]}"; do
        version=$(python -c "import $pkg; print($pkg.__version__)" 2>/dev/null)
        if [[ -z "$version" ]]; then
            echo "$pkg: Not installed or no __version__ attribute"
        else
            echo "$pkg = $version"
        fi
    done

    # If conda_env was activated, deactivate it
    if [[ -n "$conda_env" ]]; then
        echo "Deactivating Conda environment: $conda_env"
        conda deactivate
    fi
}
