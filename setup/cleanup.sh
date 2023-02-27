#!/bin/zsh


if [ -z "$1" ]; then
  echo "Usage: cleanup.sh [ENV_NAME]"
else
  conda deactivate > /dev/null 2>&1
  conda env remove -n $1
fi
