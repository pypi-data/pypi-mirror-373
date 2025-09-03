#!/bin/bash
# filepath: /home/hari/dbo/dataflow-core/dataflow/scripts/create_environment.sh
set -e

# Accept new parameters
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

# Extract just the env name (basename) from the target path
env_name=$(basename "$conda_env_path")

# Set unique cache dir per environment
export CONDA_PKGS_DIRS="/dataflow/envs/cache/${env_name}"
mkdir -p "$CONDA_PKGS_DIRS"

# Create the conda environment from the YAML file
conda env create --file "$yaml_file_path" --prefix "$conda_env_path" --yes

conda env export --prefix "$conda_env_path" > "$yaml_file_path"