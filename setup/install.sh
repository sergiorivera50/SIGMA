#!/bin/zsh

# Setup Conda environment with machine learning dependencies
# for the M1 chip (arm64) using the zsh shell.

if [ -z "$1" ]; then
  echo "Usage: install.sh [ENV_NAME]"
else
  conda deactivate > /dev/null 2>&1  # deactivate current environment
  echo "Setting up environment \"$1\"..." \
  && conda env create -n $1 -f setup/tf-metal-arm64.yaml \
  && conda activate $1 \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && echo "Installing Jupyter kernel..." \
  && python -m ipykernel install --user --name $1 \
  && echo "Verifying installation..." \
  && python setup/verify.py \
  && echo "Installation complete."
fi
