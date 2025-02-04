#!/bin/bash

# Loop through all .txt files in the people folder
for file in people/*.txt; do
    # Extract the filename without extension
    name=$(basename "$file" .txt)
    python sqlite.py --username "$name"
done
