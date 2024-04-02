#!/bin/bash
# A Bash script which add the directory contains it (SCRIPT_DIRECTORY) into PYTHONPATH environment variable
SCRIPT_DIRECTORY=$(dirname "$0")
export PYTHONPATH="$PYTHONPATH:$SCRIPT_DIRECTORY"
# than start VSCode in the SCRIPT_DIRECTORY
code "$SCRIPT_DIRECTORY"