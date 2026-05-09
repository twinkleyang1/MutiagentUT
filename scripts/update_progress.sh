#!/bin/bash
# Update progress.txt with current status

PROGRESS_FILE="${1:-shared/progress.txt}"
MESSAGE="${2:-Progress update}"

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$TIMESTAMP] $MESSAGE" >> "$PROGRESS_FILE"
echo "Progress updated."