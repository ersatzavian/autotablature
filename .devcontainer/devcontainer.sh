#!/bin/bash
# DevContainer utility script for AutoTablature

set -e

show_help() {
    echo "AutoTablature DevContainer Utilities"
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  test       - Run environment tests"
    echo "  setup      - Run initial setup"
    echo "  jupyter    - Start Jupyter notebook server"
    echo "  demo       - Run the demo notebook"
    echo "  lint       - Run code linting"
    echo "  format     - Format code with black"
    echo "  clean      - Clean temporary files"
    echo "  help       - Show this help"
}

run_tests() {
    echo "Running environment tests..."
    python test_environment.py
}

run_setup() {
    echo "Running setup..."
    python setup.py
}

start_jupyter() {
    echo "Starting Jupyter notebook server..."
    jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
        --NotebookApp.token='' --NotebookApp.password=''
}

run_demo() {
    echo "Opening demo notebook..."
    if command -v jupyter &> /dev/null; then
        jupyter notebook notebooks/audio_to_tablature_demo.ipynb
    else
        echo "Jupyter not available. Please run 'devcontainer.sh jupyter' first."
    fi
}

run_lint() {
    echo "Running code linting..."
    flake8 src/ tests/ examples/ --max-line-length=88 --extend-ignore=E203,W503
    echo "Linting completed."
}

format_code() {
    echo "Formatting code with black..."
    black src/ tests/ examples/
    echo "Code formatting completed."
}

clean_files() {
    echo "Cleaning temporary files..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    echo "Cleanup completed."
}

# Main command processing
case "${1:-help}" in
    test)
        run_tests
        ;;
    setup)
        run_setup
        ;;
    jupyter)
        start_jupyter
        ;;
    demo)
        run_demo
        ;;
    lint)
        run_lint
        ;;
    format)
        format_code
        ;;
    clean)
        clean_files
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
