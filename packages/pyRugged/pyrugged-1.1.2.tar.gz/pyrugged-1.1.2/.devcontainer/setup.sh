#!/bin/sh -ex
# This file is meant to setup a developpement environement alongside VSCode
# It can run on debian:12, compatible system, or in a devcontainer:
# docker build -t asgard-devcontainer .devcontainer

test -r ~/.inputrc || cat << EOF > ~/.inputrc
"\e[A": history-search-backward
"\e[B": history-search-forward
EOF

grep group-directories-first ~/.bashrc >/dev/null || cat << EOF > ~/.bashrc
. /etc/bash_completion
$(dircolors)
alias l='ls -alhF --color=auto --group-directories-first'
EOF

# Check if virtual Python environment was created
if test -e .venv
then
    # Activate virtual Python environment
    . .venv/bin/activate
    # Check if math_utils cython module was already built
    if pytest tests/utils/test_math_utils.py
    then
        echo "OK"
        exit 0
    else
        echo ".venv might be corrupted, remove it to reset setup."
    fi
fi
# Run main setup
sh -ex .devcontainer/install.sh
