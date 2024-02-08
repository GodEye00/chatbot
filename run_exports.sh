#!/bin/bash

EXPORTS_FILE="configs.txt"

if [ -f "$EXPORTS_FILE" ]; then
    while IFS= read -r line; do
        eval "$line"
    done < "$EXPORTS_FILE"
    echo "$EXPORTS_FILE successfully run"
else
    echo "Exports file not found!"
fi
