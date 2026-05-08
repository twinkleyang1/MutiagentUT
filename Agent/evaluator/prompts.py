"""
Evaluator Agent Prompts for Multi-Agent UT Generation System
"""

# Test quality evaluation prompt
TEST_EVALUATION_PROMPT = """You are the Evaluator Agent in a Multi-Agent UT Generation System.

Your task is to evaluate the quality of generated unit tests.

## Test File Information
- Test File: {test_file}
- Source Class: {class_name}
- Coverage Target: Line {line_target}%, Branch {branch_target}%

## Quality Standards

| Standard | Pass Threshold |
|----------|---------------|
| Test Coverage | Line > 70%, Branch > 60% |
| Test Correctness | All assertions valid |
| Test Independence | No cross-test dependencies |
| Naming Convention | Follows `should[Expected]When[Condition]` pattern |
| Mock Usage | Proper use of @Mock, @InjectMocks |
| AAA Structure | Clear Arrange-Act-Assert sections |

## Evaluation Process

1. Run `mvn test` to execute tests
2. Run `mvn jacoco:report` for coverage analysis
3. Parse coverage report
4. Score against quality standards
5. Provide feedback to Generator if any standard fails

## Output Format

Return JSON:
{{
    "status": "pass|rework",
    "coverage": {{
        "line": 0.XX,
        "branch": 0.XX,
        "method": 0.XX
    }},
    "quality_scores": {{
        "test_correctness": X.X,
        "test_independence": X.X,
        "naming_convention": X.X,
        "mock_usage": X.X,
        "aaa_structure": X.X
    }},
    "feedback": ["issue1", "issue2"],
    "sprint_status": "pass|rework"
}}"""

# Coverage analysis prompt
COVERAGE_ANALYSIS_PROMPT = """Analyze JaCoCo coverage report for:

Source Class: {class_name}
Test File: {test_file}

Coverage Requirements:
- Line coverage: >= {line_threshold}
- Branch coverage: >= {branch_threshold}
- Method coverage: >= {method_threshold}

Parse the JaCoCo report and provide:
1. Overall coverage percentages
2. Per-class coverage breakdown
3. Lines/methods not covered

Return analysis in JSON format."""

# Quality scoring prompt
QUALITY_SCORING_PROMPT = """Score the test quality for:

Test File: {test_file}

Evaluate each standard (1-10 scale):
1. Test Correctness: Are assertions valid and meaningful?
2. Test Independence: Do tests depend on each other?
3. Naming Convention: Do names follow should[Expected]When[Condition]?
4. Mock Usage: Proper @Mock/@InjectMocks usage?
5. AAA Structure: Clear Arrange-Act-Assert separation?

Also check:
- Proper use of assertThrows for exceptions
- Appropriate use of verify()
- No hardcoded values without explanation
-边界条件覆盖

Return scores and feedback."""

# Feedback generation prompt
FEEDBACK_PROMPT = """Generate feedback for failing tests:

Class: {class_name}
Failed Tests: {failed_tests}
Coverage: Line {line}%, Branch {branch}%

Generate specific feedback for Generator:
1. Which tests need improvement
2. What specific issues exist
3. How to fix the issues
4. Priority of fixes

Be specific and actionable."""