#!/bin/bash

# Typical prompt elements:
echo_user_host() {
       echo "\u@\h"
   }

echo_current_dir() {
    # uppercase
    echo "\W"
}

echo_current_dirpath() {
    # lowercase
    echo "\w"
}

# git branch echo1:
fetch_git_branch() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null
}

# git branch echo2:
parse_git_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/'
}

parse_pyenv() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        echo " ($(basename "$VIRTUAL_ENV"))"
    fi
}

parse_conda() {
    if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
        echo " ($CONDA_DEFAULT_ENV)"
    fi
}

# Prompt symbol options:
define_prompt_symbol() {
    case "$1" in
        "hashtag") echo "#";;
        "at-symbol") echo "@";;
        "tilde") echo "~";;
        "double-dash") echo "--";;
        "dollar") echo "\$";;
        "percent") echo "%";;
        "arrow-head") echo ">";;
        "lambda") echo "λ";;
        *) echo "\$";; # Default to $ if input is not recognized
    esac
}

# Define base path mappings
typeset -A path_tags
path_tags=(
    [DropBox]="/Users/username/DropBox"
    [Personal]="DropBox (Personal)"
)

function abridge_path {
    local cur_path="${1:-$PWD}"
    local num_dirs="${2:-3}"  
    local by_part="${3:-false}" 
    local tag_color="${4:-blue}"

    local display_tag="•••"
    [[ "$by_part" == "true" ]] && display_tag="•"

    if [[ -n $tag_color ]]; then
        display_tag="%F{$tag_color}$display_tag%f"
    fi
    
    # Normalize path to ensure it ends with a slash for easier processing
    [[ "$cut_path" != */ ]] && cur_path+="/"
    
    local path_parts=("${(@s:/:)cur_path}")
    local num_parts=${#path_parts[@]}
    local display_path=""; local i=1

    while (( i < num_parts )); do
        if (( i + 2 * num_dirs + 1 < num_parts )); then
            # Abridgment required; append directories
            for (( j=i; j<i+num_dirs; j++ )); do
                display_path+="/${path_parts[j]}"
            done

            # Append the abridgment marker
            if [[ "$by_part" == "true" ]]; then
                for (( j=0; j<num_parts-2*num_dirs-i; j++ )); do
                    display_path+="/$display_tag"
                done
            else
                display_path+="/$display_tag"
            fi

            # Skip to the last few directories
            i=$(( num_parts - num_dirs ))
            for (( j=i; j<num_parts; j++ )); do
                display_path+="/${path_parts[j]}"
            done
            break  # Since we've processed the abridgment, we can break out of the loop
        else
            # Not enough directories left to abridge, append the rest normally
            display_path+="/${path_parts[i]}"
            ((i++))
        fi
    done

    # Remove leading slash added for processing
    display_path="${display_path:1}"

    echo "$display_path"
}

function custom_path {
    local cur_path="$PWD"
    local tagged_path=""
    local shorten_path=${1:-0}
    
    # add optional color arg
    local tag_color="${1:-blue}"

    # Check tags and update tagged_path:
    for tag path in ${(kv)path_tags}; do
        if [[ "$cur_path" == *"$path"* ]]; then
            tag="%F{$tag_color}$tag%f"
            cur_path=${cur_path//$path/$tag}
        fi
    done

    if [[ "$cur_path" == "$HOME"* ]]; then
        cur_path=${cur_path//$HOME/}; fi

    if [[ "$cur_path" != /* ]]; then
        cur_path="/$cur_path"; fi

    if [[ "$PWD" == "$HOME"* ]]; then
        cur_path="~$cur_path"; fi

    local path_parts=("${(@s:/:)cur_path}")
    if [[ ${#path_parts} -gt 4 ]]; then
        local tag="%F{$tag_color}•••%f"
        if [[ $shorten_path -eq 1 ]]; then
            #cur_path="${path_parts[1]}/${path_parts[2]}/${tag}/${path_parts[-1]}"
            cur_path=$(abridge_path "$cur_path" 3 true, "$tag_color")
        fi
    fi

    echo "$cur_path"
}

function find_environment {
    if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
        echo "conda:$CONDA_DEFAULT_ENV"
    elif [[ -n "$NVM_DIR" ]]; then
        echo "nvm:$NVM_DIR"
    elif command -v pyenv >/dev/null 2>&1; then
        local pyenv_version=$(pyenv version-name 2>/dev/null)
        [[ -n "$pyenv_version" ]] && echo "pyenv:$pyenv_version"
    elif command -v rbenv >/dev/null 2>&1; then
        local rbenv_version=$(rbenv global 2>/dev/null)
        [[ -n "$rbenv_version" ]] && echo "rbenv:$rbenv_version"
    fi
}

function get_env_prompt {
    local parentheses=${1:-false}
    local use_color="${2:-blue}"
    local with_emoji=${3:-false}
    
    local env_output=$(find_environment)
    local env_type="${env_output%%:*}"
    local env_name="${env_output#*:}"

    # No environment found, return empty string
    if [[ -z "$env_type" ]]; then
        echo ""
        return
    fi

    # Initialize the formatted environment string
    local formatted_env=""

    # Determine the icon based on environment type
    local icon=""
    if [[ "$with_emoji" == "true" ]]; then
        case "$env_type" in
            conda) icon="🐍" ;;
            nvm)   icon="⚡" ;;
            pyenv) icon="🐍" ;;
            rbenv) icon="💎" ;;
            *)     icon="" ;;
        esac
    fi

    # Combine icon with environment name
    formatted_env="$icon $env_name"

    # Apply color if specified
    if [[ -n "$use_color" ]]; then
        formatted_env="%{$fg[$use_color]%}$formatted_env%{$reset_color%}"
    fi

    # Apply parentheses if specified
    if [[ "$parentheses" == "true" ]]; then
        formatted_env="($formatted_env)"
    fi

    echo "$formatted_env" # for use in prompt
}

trim_end() {
    local var="$1"
    echo "${var%"${var##*[![:space:]]}"}"
}


function conda_prompt {
    local tag_color="$1"
    #local tag_color="${1:-magenta}"

    #echo "Modifier: $CONDA_PROMPT_MODIFIER"

    # default prefix: conda env name
    local PREFIX=$CONDA_PROMPT_MODIFIER

    # remove existing conda prefix:
    PROMPT=${PROMPT//"$PREFIX"/}

    # echo "Prefix (1): $PREFIX"

    if [[ -z $PREFIX ]]; then
        PREFIX="($CONDA_DEFAULT_ENV)"
    fi

    # echo "Prefix (2): $PREFIX"
    
    # remove trailing whitespace
    PREFIX=$(trim_end $PREFIX)

    # default with added tag color
    if [[ -n $tag_color ]]; then
        PREFIX="%F{$tag_color}$PREFIX%f"; fi

    # echo "Prefix (3): $PREFIX"

    echo $PREFIX
}

function git_prompt {
    local tag_color="$1"
    local add_wrap="${2:-true}"

    local GIT_BRANCH=$(parse_git_branch)
    local GIT_SYMBOL=$(define_prompt_symbol "$tag_symbol")

    if [[ -n "$GIT_BRANCH" ]]; then
        if [[ "$add_wrap" == true ]]; then
            GIT_BRANCH="git:($GIT_BRANCH)"
        fi
        
        if [[ -n "$tag_color" ]]; then
            echo "%F{$tag_color}$GIT_BRANCH%f"
        else
            echo "$GIT_BRANCH"
        fi
    fi
}

# Example prompt specification:
#PROMPT='$(conda_prompt green) %F{cyan}%n@%m%f $(custom_path) %# '