"""
Planner Agent - Analyzes Java project and creates test plans
"""

import os
import re
from datetime import datetime
from typing import Any, Dict, List

from ..shared.file_manager import FileManager
from ..shared import constants
from . import prompts


class Planner:
    """Planner Agent - Analyzes Java project structure and creates test plans"""

    def __init__(self, project_root: str, file_manager: FileManager):
        self.project_root = project_root
        self.file_manager = file_manager

    def analyze_project(self, project_path: str, requirements: str = "") -> Dict[str, Any]:
        """
        Analyze Java project and create class_list.json and test_plan.json

        Args:
            project_path: Path to the Java project
            requirements: User requirements (optional)

        Returns:
            Dictionary with analysis results
        """
        print(f"[Planner] Analyzing project: {project_path}")

        # Discover all Java classes
        classes = self._discover_classes(project_path)

        # Create class_list.json
        class_list_data = {
            "project_path": project_path,
            "scan_date": datetime.now().strftime("%Y-%m-%d"),
            "classes": classes
        }
        self.file_manager.save_class_list(class_list_data)

        # Create test_plan.json
        test_plan_data = self._create_test_plan(classes)
        self.file_manager.save_test_plan(test_plan_data)

        # Initialize progress.txt
        progress_content = self._init_progress(classes)
        self.file_manager.save_progress(progress_content)

        print(f"[Planner] Found {len(classes)} classes")

        return {
            "total_classes": len(classes),
            "class_list": class_list_data,
            "test_plan": test_plan_data
        }

    def _discover_classes(self, project_path: str) -> List[Dict[str, Any]]:
        """Discover all Java classes in the project"""
        classes = []
        src_main_java = os.path.join(project_path, "src", "main", "java")

        if not os.path.exists(src_main_java):
            print(f"[Planner] Warning: {src_main_java} not found")
            return classes

        for root, dirs, files in os.walk(src_main_java):
            for file in files:
                if file.endswith(".java"):
                    file_path = os.path.join(root, file)
                    class_info = self._analyze_class(file_path, project_path)
                    if class_info:
                        classes.append(class_info)

        # Sort by priority
        classes.sort(key=lambda x: x.get("priority", 5))
        return classes

    def _analyze_class(self, file_path: str, project_root: str) -> Dict[str, Any]:
        """Analyze a single Java class file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract class name
            class_name = self._extract_class_name(content, file_path)
            if not class_name:
                return None

            # Extract package
            package = self._extract_package(content)

            # Determine class type
            class_type = self._determine_class_type(class_name, package, content)

            # Determine priority
            priority = self._determine_priority(class_type, class_name)

            # Calculate relative path
            relative_path = os.path.relpath(file_path, project_root)

            return {
                "name": class_name,
                "package": package,
                "path": relative_path,
                "type": class_type,
                "priority": priority,
                "tested": False
            }
        except Exception as e:
            print(f"[Planner] Error analyzing {file_path}: {e}")
            return None

    def _extract_class_name(self, content: str, file_path: str) -> str:
        """Extract class name from Java file"""
        # Match class, interface, or enum declaration
        patterns = [
            r'public\s+class\s+(\w+)',
            r'public\s+interface\s+(\w+)',
            r'public\s+enum\s+(\w+)',
            r'class\s+(\w+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        # Fallback to filename
        return os.path.basename(file_path).replace('.java', '')

    def _extract_package(self, content: str) -> str:
        """Extract package declaration"""
        match = re.search(r'package\s+([\w\.]+);', content)
        return match.group(1) if match else ""

    def _determine_class_type(self, class_name: str, package: str, content: str) -> str:
        """Determine the type of class based on naming and content"""
        # Check naming patterns
        name_lower = class_name.lower()

        if 'controller' in name_lower or 'rest' in name_lower or 'api' in name_lower:
            return constants.CLASS_TYPE_CONTROLLER
        if 'service' in name_lower or 'impl' in name_lower:
            return constants.CLASS_TYPE_SERVICE
        if 'repository' in name_lower or 'dao' in name_lower:
            return constants.CLASS_TYPE_REPOSITORY
        if 'entity' in name_lower or 'model' in name_lower or 'domain' in name_lower:
            return constants.CLASS_TYPE_ENTITY
        if 'util' in name_lower or 'helper' in name_lower or 'helper' in name_lower:
            return constants.CLASS_TYPE_UTILS

        # Check content for annotations
        if '@Entity' in content or '@Table' in content:
            return constants.CLASS_TYPE_ENTITY
        if '@Service' in content:
            return constants.CLASS_TYPE_SERVICE
        if '@RestController' in content or '@Controller' in content:
            return constants.CLASS_TYPE_CONTROLLER
        if '@Repository' in content:
            return constants.CLASS_TYPE_REPOSITORY

        return constants.CLASS_TYPE_OTHER

    def _determine_priority(self, class_type: str, class_name: str) -> int:
        """Determine testing priority (1 = highest)"""
        type_priorities = {
            constants.CLASS_TYPE_SERVICE: 1,
            constants.CLASS_TYPE_CONTROLLER: 1,
            constants.CLASS_TYPE_REPOSITORY: 2,
            constants.CLASS_TYPE_UTILS: 3,
            constants.CLASS_TYPE_ENTITY: 4,
            constants.CLASS_TYPE_OTHER: 3
        }
        return type_priorities.get(class_type, 3)

    def _create_test_plan(self, classes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create test plan from discovered classes"""
        features = []

        for cls in classes:
            tests = self._design_tests_for_class(cls)
            features.append({
                "class_name": cls["name"],
                "package": cls["package"],
                "type": cls["type"],
                "tests": tests
            })

        return {
            "plan_version": constants.PLAN_VERSION,
            "total_classes": len(classes),
            "coverage_target": {
                "line": constants.LINE_COVERAGE_THRESHOLD,
                "branch": constants.BRANCH_COVERAGE_THRESHOLD,
                "method": constants.METHOD_COVERAGE_THRESHOLD
            },
            "features": features
        }

    def _design_tests_for_class(self, class_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design test cases for a single class"""
        class_name = class_info["name"]
        class_type = class_info["type"]

        tests = []

        # Common tests for all classes
        tests.append({
            "test_name": f"shouldReturnInstanceWhenCreated",
            "type": constants.TYPE_NORMAL_PATH,
            "passes": False
        })

        # Type-specific tests
        if class_type == constants.CLASS_TYPE_SERVICE:
            tests.extend(self._design_service_tests(class_name))
        elif class_type == constants.CLASS_TYPE_CONTROLLER:
            tests.extend(self._design_controller_tests(class_name))
        elif class_type == constants.CLASS_TYPE_ENTITY:
            tests.extend(self._design_entity_tests(class_name))
        elif class_type == constants.CLASS_TYPE_REPOSITORY:
            tests.extend(self._design_repository_tests(class_name))

        # Add boundary condition tests
        tests.extend([
            {
                "test_name": f"shouldHandleNullInput",
                "type": constants.TYPE_BOUNDARY_CONDITION,
                "passes": False
            },
            {
                "test_name": f"shouldHandleEmptyInput",
                "type": constants.TYPE_BOUNDARY_CONDITION,
                "passes": False
            }
        ])

        return tests

    def _design_service_tests(self, class_name: str) -> List[Dict[str, Any]]:
        """Design tests for service classes"""
        return [
            {
                "test_name": f"shouldReturnResultWhenValidInput",
                "type": constants.TYPE_NORMAL_PATH,
                "passes": False
            },
            {
                "test_name": f"shouldThrowExceptionWhenInvalidInput",
                "type": constants.TYPE_EXCEPTION,
                "passes": False
            }
        ]

    def _design_controller_tests(self, class_name: str) -> List[Dict[str, Any]]:
        """Design tests for controller classes"""
        return [
            {
                "test_name": f"shouldReturn200WhenValidRequest",
                "type": constants.TYPE_NORMAL_PATH,
                "passes": False
            },
            {
                "test_name": f"shouldReturn400WhenInvalidRequest",
                "type": constants.TYPE_EXCEPTION,
                "passes": False
            },
            {
                "test_name": f"shouldReturn404WhenResourceNotFound",
                "type": constants.TYPE_EDGE_CASE,
                "passes": False
            }
        ]

    def _design_entity_tests(self, class_name: str) -> List[Dict[str, Any]]:
        """Design tests for entity classes"""
        return [
            {
                "test_name": f"shouldCreateWithValidFields",
                "type": constants.TYPE_NORMAL_PATH,
                "passes": False
            },
            {
                "test_name": f"shouldEqualsWhenSameId",
                "type": constants.TYPE_NORMAL_PATH,
                "passes": False
            },
            {
                "test_name": f"shouldNotEqualsWhenDifferentId",
                "type": constants.TYPE_NORMAL_PATH,
                "passes": False
            }
        ]

    def _design_repository_tests(self, class_name: str) -> List[Dict[str, Any]]:
        """Design tests for repository classes"""
        return [
            {
                "test_name": f"shouldFindById",
                "type": constants.TYPE_NORMAL_PATH,
                "passes": False
            },
            {
                "test_name": f"shouldReturnNullWhenNotFound",
                "type": constants.TYPE_BOUNDARY_CONDITION,
                "passes": False
            }
        ]

    def _init_progress(self, classes: List[Dict[str, Any]]) -> str:
        """Initialize progress.txt"""
        lines = [
            "# UT Generation Progress",
            f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Completed",
            "- None yet",
            "",
            "## In Progress",
            "- None",
            "",
            "## Pending",
        ]

        for cls in classes:
            lines.append(f"- {cls['name']} ({cls['type']})")

        lines.extend([
            "",
            "Coverage: 0%",
            ""
        ])

        return "\n".join(lines)

    def get_plan_status(self) -> Dict[str, Any]:
        """Get current plan status"""
        class_list = self.file_manager.load_class_list()
        test_plan = self.file_manager.load_test_plan()

        total = len(class_list.get("classes", []))
        tested = sum(1 for cls in class_list.get("classes", []) if cls.get("tested", False))

        return {
            "total_classes": total,
            "tested_classes": tested,
            "pending_classes": total - tested,
            "coverage_target": test_plan.get("coverage_target", {})
        }