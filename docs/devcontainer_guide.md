# AutoTablature DevContainer Guide

This document provides information about using the DevContainer setup for AutoTablature development.

## Overview

The DevContainer provides a consistent development environment with all necessary dependencies pre-installed. This ensures that all developers work with the same environment, regardless of their host operating system.

## Features

- **Python 3.11** with all dependencies from `requirements.txt`
- **GPU support** for machine learning tasks (if available on the host)
- **Jupyter Notebook** server pre-configured
- **VS Code extensions** for Python development, testing, and debugging
- **Persistent volumes** for data and models
- **Git integration** with GitHub CLI

## Getting Started

1. Ensure you have Docker and VS Code with the Remote Containers extension installed
2. Open the project in VS Code
3. When prompted, click "Reopen in Container" or run the command "Remote-Containers: Reopen in Container"
4. Wait for the container to build and start

## Directory Structure

The DevContainer maps the following directories:

- `/workspace`: The main project directory (mapped to the repository root)
- `/workspace/data`: Persistent volume for data files
- `/workspace/models`: Persistent volume for trained models

## Available Tasks

You can run the VS Code tasks defined in `.vscode/tasks.json` directly from the DevContainer:

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type "Tasks: Run Task" and select it
3. Choose one of the available tasks:
   - **Run Setup**: Initialize the project environment
   - **Run Basic Test**: Run basic end-to-end tests
   - **Run Component Tests**: Test specific components
   - **Open Jupyter Notebook**: Start and open the Jupyter Notebook server
   - **Collect Training Data**: Gather data for model training
   - **Extract GP Annotations**: Extract annotations from Guitar Pro files
   - **Run Demo**: Execute the demo with an audio file
   - **Open Demo Notebook**: Open the demo Jupyter notebook

## Jupyter Notebooks

The DevContainer includes a Jupyter server accessible at port 8888. To use it:

1. Run the "Open Jupyter Notebook" task
2. Click on the link in the terminal, or navigate to `http://localhost:8888` in your browser
3. The password is not set by default, just press Enter if prompted

## GPU Support

If your host machine has a CUDA-compatible GPU and the appropriate drivers, the DevContainer is configured to use it for machine learning tasks. You can verify GPU availability within the container by running:

```bash
python -c "import torch; print('GPU available:', torch.cuda.is_available())"
```

## Customizing the Environment

If you need to install additional dependencies:

1. Add them to `requirements.txt`
2. Rebuild the container (Command Palette > "Remote-Containers: Rebuild Container")

## Troubleshooting

### Container fails to build

- Check that Docker has enough resources allocated (memory, CPU)
- Ensure your Docker installation is up-to-date
- Try running `docker system prune` to clean up unused resources

### GPU not available in container

- Verify that NVIDIA Container Toolkit is installed on your host
- Check that your GPU drivers are up-to-date
- Make sure Docker Desktop has GPU support enabled

### Jupyter Notebook not accessible

- Check that port 8888 is not already in use on your host machine
- Verify that the notebook server is running (check terminal output)
- Try accessing via `http://localhost:8888` instead of the provided link
