#!/bin/bash
# Run Maven tests for a Java project

PROJECT_PATH="${1:-.}"

echo "Running tests for: $PROJECT_PATH"
echo "================================"

cd "$PROJECT_PATH" || exit 1

# Run tests
mvn clean test -Dsurefire.useFile=false 2>&1

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed"
else
    echo "✗ Tests failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE