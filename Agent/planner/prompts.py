"""
Planner Agent Prompts for Multi-Agent UT Generation System
"""

from datetime import datetime

# Project analysis prompt
PROJECT_ANALYSIS_PROMPT = """You are the Planner Agent in a Multi-Agent UT Generation System.

Your task is to analyze a Java project and create a comprehensive test plan.

## Input
- Java project path: {project_path}
- User requirements: {requirements}

## Output
Create a class_list.json and test_plan.json with the following structure:

### class_list.json structure:
{{
    "project_path": "{project_path}",
    "scan_date": "{scan_date}",
    "classes": [
        {{
            "name": "ClassName",
            "package": "com.example.package",
            "path": "src/main/java/.../ClassName.java",
            "type": "service|controller|entity|repository|utils|other",
            "priority": 1-5,
            "tested": false
        }}
    ]
}}

### test_plan.json structure:
{{
    "plan_version": "1.0",
    "total_classes": N,
    "coverage_target": {{
        "line": 0.70,
        "branch": 0.60,
        "method": 0.80
    }},
    "features": [
        {{
            "class_name": "ClassName",
            "tests": [
                {{
                    "test_name": "should[ExpectedBehavior]When[Condition]",
                    "type": "normal_path|boundary_condition|exception|edge_case",
                    "passes": false
                }}
            ]
        }}
    ]
}}

## Rules for Analysis

1. **Class Discovery**: Scan all Java files under src/main/java/
2. **Priority Assignment**:
   - Priority 1: Core business services, controllers
   - Priority 2: Data access layers, repositories
   - Priority 3: Utility classes, helpers
   - Priority 4: Entity/model classes
   - Priority 5: Configuration classes

3. **Test Design**:
   - Normal path: Basic functionality tests
   - Boundary condition: null, 0, empty, max values
   - Exception: Error handling scenarios
   - Edge case: Special values, corner cases

4. **Coverage Targets**:
   - Line coverage: 70% minimum
   - Branch coverage: 60% minimum
   - Method coverage: 80% minimum

## Analysis Process

1. Scan project structure recursively
2. Identify all .java files in src/main/java/
3. Classify by package and naming patterns
4. Prioritize based on business importance
5. Design test cases for each class

Return your analysis in JSON format."""

# Class analysis prompt
CLASS_ANALYSIS_PROMPT = """Analyze the following Java class for test planning:

Class: {class_name}
Package: {package}
Path: {path}

## Analysis Requirements

1. Identify public methods and their signatures
2. Determine input parameters and return types
3. Identify dependencies (other classes used)
4. Analyze edge cases and boundary conditions
5. Determine exception handling patterns

## Test Case Design

For each public method, design tests covering:
- Normal execution path
- Boundary conditions (null, empty, max values)
- Exception scenarios
- Edge cases

Return test case specifications in JSON format."""

# Priority determination prompt
PRIORITY_PROMPT = """Determine the priority for testing the following class:

Class: {class_name}
Package: {package}
Type: {class_type}

Priority Scale:
- 1: Critical - Core business logic, frequently used
- 2: High - Important services, data layers
- 3: Medium - Utility classes, helpers
- 4: Low - Entity models, DTOs
- 5: Minimal - Configuration, constants

Consider:
- Business criticality
- Complexity and dependencies
- Testability
- Risk of changes

Return priority as integer (1-5)."""