#!/bin/bash
# Run JaCoCo coverage report and parse results

PROJECT_PATH="${1:-.}"

echo "Generating coverage report for: $PROJECT_PATH"
echo "=============================================="

cd "$PROJECT_PATH" || exit 1

# Generate report
mvn jacoco:report 2>&1

# Parse coverage
COVERAGE_FILE="$PROJECT_PATH/target/site/jacoco/jacoco-ut/index.html"

if [ -f "$COVERAGE_FILE" ]; then
    echo ""
    echo "Coverage Report:"
    echo "----------------"

    # Extract percentages using grep/sed
    LINE_COV=$(grep -o 'Line Coverage.*[0-9]\+%' "$COVERAGE_FILE" | grep -o '[0-9]\+%' | head -1)
    BRANCH_COV=$(grep -o 'Branch Coverage.*[0-9]\+%' "$COVERAGE_FILE" | grep -o '[0-9]\+%' | head -1)
    COMPLEX_COV=$(grep -o 'Complexity.*[0-9]\+%' "$COVERAGE_FILE" | grep -o '[0-9]\+%' | head -1)

    echo "Line Coverage:    $LINE_COV"
    echo "Branch Coverage:  $BRANCH_COV"
    echo "Complexity:       $COMPLEX_COV"
else
    echo ""
    echo "Warning: Coverage file not found at $COVERAGE_FILE"
    echo "Make sure JaCoCo plugin is configured and tests have run."
fi