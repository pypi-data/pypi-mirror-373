#!/bin/bash
set -e

source_env_name=$1
target_env_path=$2

# Extract just the env name (basename) from the target path
env_name=$(basename "$target_env_path")

# Set unique cache dir per environment
export CONDA_PKGS_DIRS="/dataflow/envs/cache/${env_name}"
mkdir -p "$CONDA_PKGS_DIRS"

# 1. Cloning conda env
conda create --clone ${source_env_name} --prefix ${target_env_path} --yes

conda env export --prefix "$conda_env_path" > "$yaml_file_path"

echo "Environment Creation Successful"