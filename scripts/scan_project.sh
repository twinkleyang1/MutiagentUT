#!/bin/bash
# Scan Java project and list all classes

PROJECT_PATH="${1:-.}"

echo "Scanning Java project: $PROJECT_PATH"
echo "=================================="

if [ ! -d "$PROJECT_PATH/src/main/java" ]; then
    echo "Error: src/main/java not found in $PROJECT_PATH"
    exit 1
fi

echo ""
echo "Classes found:"
echo "-------------"

find "$PROJECT_PATH/src/main/java" -name "*.java" | while read file; do
    # Extract package and class name
    package=$(grep -m1 "^package " "$file" | sed 's/package //;s/;//')
    class=$(basename "$file" .java)

    # Get relative path
    rel_path="${file#$PROJECT_PATH/}"

    # Classify type
    if [[ "$class" == *"Service"* ]] || [[ "$class" == *"Impl"* ]]; then
        type="service"
    elif [[ "$class" == *"Controller"* ]] || [[ "$class" == *"Rest"* ]]; then
        type="controller"
    elif [[ "$class" == *"Repository"* ]] || [[ "$class" == *"DAO"* ]]; then
        type="repository"
    elif [[ "$class" == *"Entity"* ]] || [[ "$class" == *"Model"* ]]; then
        type="entity"
    elif [[ "$class" == *"Util"* ]] || [[ "$class" == *"Helper"* ]]; then
        type="utils"
    else
        type="other"
    fi

    echo "$type | $class | $package | $rel_path"
done | sort

echo ""
echo "Scan complete."