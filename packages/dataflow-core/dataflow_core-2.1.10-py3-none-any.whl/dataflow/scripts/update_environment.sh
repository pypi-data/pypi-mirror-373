#!/bin/bash
# filepath: /home/hari/dbo/dataflow-core/dataflow/scripts/update_environment.sh
set -e

# Accept parameters
yaml_file_path=$1
conda_env_path=$2

# Validate inputs
if [ -z "$yaml_file_path" ] || [ -z "$conda_env_path" ]; then
    echo "Error: Missing required parameters"
    exit 1
fi

if [ ! -f "$yaml_file_path" ]; then
    echo "Error: YAML file does not exist: $yaml_file_path"
    exit 1
fi

if [ ! -d "$conda_env_path" ]; then
    echo "Error: Conda environment does not exist at: $conda_env_path"
    exit 1
fi

# Extract just the env name (basename) from the target path
env_name=$(basename "$conda_env_path")

# Set unique cache dir per environment
export CONDA_PKGS_DIRS="/dataflow/envs/cache/${env_name}"
mkdir -p "$CONDA_PKGS_DIRS"

# Update the conda environment using the YAML file
conda env update --prefix "$conda_env_path" --file "$yaml_file_path" --prune

if [ ! -L "$yaml_file_path" ]; then
    conda env export --prefix "$conda_env_path" > "$yaml_file_path"
fi