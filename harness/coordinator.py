"""
Harness Module - Coordinator

Coordinates the UT generation process by reading state and providing prompts.
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional

from .state_manager import StateManager


class HarnessCoordinator:
    """
    Main coordinator for the UT generation harness.

    Manages state files and provides iteration prompts to guide Claude Code.
    """

    def __init__(self, project_root: str, java_project_path: str):
        self.project_root = project_root
        self.java_project_path = java_project_path
        self.state_manager = StateManager(project_root)

    def needs_initialization(self) -> bool:
        """Check if the harness needs initialization"""
        return not self.state_manager.class_list_exists()

    def is_complete(self) -> bool:
        """Check if UT generation is complete"""
        status = self.state_manager.get_status()
        return status.get("all_tests_complete", False) and status.get("targets_met", False)

    def get_status(self) -> Dict[str, Any]:
        """Get current harness status"""
        return self.state_manager.get_status()

    def get_current_phase(self) -> str:
        """
        Determine current phase based on state.

        Returns:
            - 'init': Need to initialize (scan project)
            - 'generate': Need to generate tests
            - 'evaluate': Need to evaluate tests
            - 'complete': All done
        """
        status = self.state_manager.get_status()

        if not status.get("initialized"):
            return "init"

        if not status.get("tested_classes"):
            return "generate"

        if not status.get("targets_met"):
            return "evaluate"

        if status.get("all_tests_complete"):
            return "complete"

        return "generate"

    def get_iteration_prompt(self) -> str:
        """
        Get the prompt for the current iteration based on state.

        This is the main entry point for Claude Code to understand what to do.
        """
        phase = self.get_current_phase()
        status = self.state_manager.get_status()

        prompt_parts = []

        # Header
        prompt_parts.append(f"""# UT Generation Harness - Iteration Prompt

## System Status
- Phase: {phase}
- Project: {self.java_project_path}
- Tested Classes: {status.get('tested_classes', 0)}/{status.get('total_classes', 0)}
- Passed Tests: {status.get('passed_tests', 0)}/{status.get('total_tests', 0)}
- Coverage: Line {status.get('coverage', {}).get('line', 0)*100:.1f}%, Branch {status.get('coverage', {}).get('branch', 0)*100:.1f}%

""")

        # Phase-specific instructions
        if phase == "init":
            prompt_parts.append(self._get_init_prompt())
        elif phase == "generate":
            prompt_parts.append(self._get_generate_prompt())
        elif phase == "evaluate":
            prompt_parts.append(self._get_evaluate_prompt())
        elif phase == "complete":
            prompt_parts.append(self._get_complete_prompt())

        # Append rules
        prompt_parts.append(f"""

## Rules
Follow the rules defined in:
- rules/Java_UT_Testing_Rules.md
- rules/Long_Running_Agent_Rules.md

## State Files
State is tracked in these files (DO NOT modify directly, Claude Code updates them):
- shared/class_list.json - List of classes discovered
- shared/test_plan.json - Test plan for each class
- shared/progress.txt - Human-readable progress
- shared/coverage_report.json - Coverage and quality scores

## Output
After completing your task, update the appropriate state files.
If all tests are complete and coverage targets met, output: <promise>CODE_IMPROVED</promise>
""")

        return "\n".join(prompt_parts)

    def _get_init_prompt(self) -> str:
        return """## Phase: Initialization

You need to analyze the Java project and create the initial state files.

### Tasks
1. Scan `{java_project_path}/src/main/java/` recursively
2. Identify all .java files and classify them by type:
   - service: Classes with 'Service' or 'Impl' in name
   - controller: Classes with 'Controller', 'Rest', 'Api' in name
   - repository: Classes with 'Repository', 'DAO' in name
   - entity: Classes with 'Entity', 'Model', 'Domain' in name
   - utils: Classes with 'Util', 'Helper' in name
   - other: Everything else

3. Create class_list.json with structure:
```json
{{
  "project_path": "{java_project_path}",
  "scan_date": "{date}",
  "classes": [
    {{
      "name": "ClassName",
      "package": "com.example.package",
      "path": "relative/path/to/ClassName.java",
      "type": "service|controller|repository|entity|utils|other",
      "priority": 1-5 (1=highest),
      "tested": false
    }}
  ]
}}
```

4. Create test_plan.json with tests for each class:
```json
{{
  "plan_version": "1.0",
  "total_classes": N,
  "coverage_target": {{"line": 0.70, "branch": 0.60, "method": 0.80}},
  "features": [
    {{
      "class_name": "ClassName",
      "package": "com.example.package",
      "type": "service",
      "tests": [
        {{"test_name": "shouldReturnInstanceWhenCreated", "type": "normal_path", "passes": false}},
        {{"test_name": "shouldHandleNullInput", "type": "boundary_condition", "passes": false}}
      ]
    }}
  ]
}}
```

5. Create progress.txt:
```
# UT Generation Progress
Created: {date}

## Completed
- None yet

## Pending
[list all classes]
```

""".format(java_project_path=self.java_project_path, date=datetime.now().strftime("%Y-%m-%d"))

    def _get_generate_prompt(self) -> str:
        """Get prompt for test generation phase"""
        status = self.state_manager.get_status()
        next_class = self._get_next_pending_class()

        return """## Phase: Test Generation

### Current Status
- Tested Classes: {tested}/{total}
- Next Class: {next_class}

### Tasks
1. Read the source file for `{next_class}`
2. Analyze the class structure (public methods, dependencies)
3. Generate JUnit 5 tests following the test_plan.json for this class
4. Save tests to: `Test/src/test/java/<package>/<ClassName>Test.java`
5. Update `shared/progress.txt` to mark this class as completed

### Test Requirements
- Use JUnit 5 + Mockito
- AAA Pattern: // Arrange, // Act, // Assert
- @ExtendWith(MockitoExtension.class)
- @Mock and @InjectMocks annotations
- Method naming: `should[Expected]When[Condition]`

### Output Files
- Test file: `Test/src/test/java/<package>/<ClassName>Test.java`
- Update: `shared/progress.txt`
- Update: `shared/class_list.json` (mark class as tested)
- Update: `shared/test_plan.json` (mark tests as passes=true)

""".format(
            tested=status.get('tested_classes', 0),
            total=status.get('total_classes', 0),
            next_class=next_class if next_class else "unknown"
        )

    def _get_evaluate_prompt(self) -> str:
        """Get prompt for test evaluation phase"""
        status = self.state_manager.get_status()
        coverage = status.get('coverage', {})

        return """## Phase: Test Evaluation

### Current Coverage
- Line: {line:.1f}% (target: 70%)
- Branch: {branch:.1f}% (target: 60%)

### Tasks
1. Run `mvn test` in the Java project to execute tests
2. Run `mvn jacoco:report` to generate coverage report
3. Parse the coverage report and update `shared/coverage_report.json`
4. If coverage targets are met and all tests pass, mark as complete

### Coverage Report Format
```json
{{
  "report_date": "{date}",
  "overall_coverage": {{"line": 0.XX, "branch": 0.XX, "method": 0.XX}},
  "class_results": [
    {{
      "class_name": "ClassName",
      "line_coverage": 0.XX,
      "branch_coverage": 0.XX,
      "test_count": N,
      "status": "pass|fail"
    }}
  ],
  "quality_scores": {{
    "test_correctness": X.X,
    "test_independence": X.X,
    "naming_convention": X.X,
    "mock_usage": X.X,
    "aaa_structure": X.X
  }},
  "sprint_status": "pass|rework"
}}
```

### Decision
- If coverage targets met (Line > 70%, Branch > 60%) AND all tests pass:
  - Output: <promise>CODE_IMPROVED</promise>
- Otherwise:
  - Continue to generate more tests or fix failing tests

""".format(
            line=coverage.get('line', 0) * 100,
            branch=coverage.get('branch', 0) * 100,
            date=datetime.now().strftime("%Y-%m-%d")
        )

    def _get_complete_prompt(self) -> str:
        return """## Phase: Complete

All tests have been generated and coverage targets met!

### Final Status
- All classes tested
- Coverage targets achieved
- Quality standards met

Output: <promise>CODE_IMPROVED</promise>
"""

    def _get_next_pending_class(self) -> Optional[str]:
        """Get the next class that needs testing"""
        class_list = self.state_manager.load_class_list()
        for cls in class_list.get("classes", []):
            if not cls.get("tested", False):
                return cls.get("name")
        return None

    def get_coverage_status(self) -> Dict[str, Any]:
        """Get detailed coverage status"""
        return self.state_manager.get_coverage_status()

    def get_java_project_path(self) -> str:
        """Get the Java project path"""
        return self.java_project_path