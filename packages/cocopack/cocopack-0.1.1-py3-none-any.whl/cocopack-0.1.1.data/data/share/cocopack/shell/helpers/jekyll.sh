#!/bin/bash

function jekyll_restart() {
    # Clean + Restart Jekyll server
    echo "Cleaning Jekyll site..."
    bundle exec jekyll clean

    # With optional --port argument
    local port=${1:-4000}
    echo "(Re)Starting Jekyll server on port $port..."
    bundle exec jekyll serve --port $port
}

function jekyll_reload() {
    # Clean + Restart Jekyll server
    echo "Cleaning Jekyll site..."
    bundle exec jekyll clean

    # With optional --port argument
    local port=${1:-4000}
    echo "(Re)Starting Jekyll server on port $port..."
    bundle exec jekyll serve --port $port --livereload
}

function jekyll_restart_plus() {
    # Find the process ID of 'jekyll serve' and kill it
    pid=$(ps aux | grep '[j]ekyll serve' | awk '{print $2}')
    if [[ -n $pid ]]; then
        echo "Stopping Jekyll server..."
        kill $pid
    fi

    echo "Cleaning Jekyll site..."
    bundle exec jekyll clean

    local port=${1:-4000}
    echo "(Re)Starting Jekyll server on port $port..."
    bundle exec jekyll serve --port $port
}