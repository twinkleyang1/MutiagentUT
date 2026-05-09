"""
Harness Module - State Manager

Manages state files in the shared/ directory for Claude Code iteration.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class StateManager:
    """Manages state files for the UT generation harness"""

    SHARED_DIR = "shared"

    # File names
    CLASS_LIST = "class_list.json"
    TEST_PLAN = "test_plan.json"
    PROGRESS = "progress.txt"
    COVERAGE_REPORT = "coverage_report.json"

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.shared_dir = os.path.join(project_root, self.SHARED_DIR)
        os.makedirs(self.shared_dir, exist_ok=True)

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.shared_dir, filename)

    # ==================== Existence Checks ====================

    def class_list_exists(self) -> bool:
        """Check if class_list.json exists"""
        return os.path.exists(self._get_path(self.CLASS_LIST))

    def test_plan_exists(self) -> bool:
        """Check if test_plan.json exists"""
        return os.path.exists(self._get_path(self.TEST_PLAN))

    def coverage_report_exists(self) -> bool:
        """Check if coverage_report.json exists"""
        return os.path.exists(self._get_path(self.COVERAGE_REPORT))

    # ==================== Class List Operations ====================

    def load_class_list(self) -> Dict[str, Any]:
        """Load class list from JSON file"""
        path = self._get_path(self.CLASS_LIST)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_class_list(self, data: Dict[str, Any]) -> None:
        """Save class list to JSON file"""
        path = self._get_path(self.CLASS_LIST)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_untested_classes(self) -> List[Dict[str, Any]]:
        """Get list of untested classes"""
        data = self.load_class_list()
        return [cls for cls in data.get("classes", []) if not cls.get("tested", False)]

    def mark_class_tested(self, class_name: str) -> None:
        """Mark a class as tested"""
        data = self.load_class_list()
        for cls in data.get("classes", []):
            if cls.get("name") == class_name:
                cls["tested"] = True
                break
        self.save_class_list(data)

    # ==================== Test Plan Operations ====================

    def load_test_plan(self) -> Dict[str, Any]:
        """Load test plan from JSON file"""
        path = self._get_path(self.TEST_PLAN)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_test_plan(self, data: Dict[str, Any]) -> None:
        """Save test plan to JSON file"""
        path = self._get_path(self.TEST_PLAN)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_pending_tests(self, class_name: str) -> List[Dict[str, Any]]:
        """Get pending tests for a specific class"""
        data = self.load_test_plan()
        for feature in data.get("features", []):
            if feature.get("class_name") == class_name:
                return [t for t in feature.get("tests", []) if not t.get("passes", False)]
        return []

    def mark_test_passed(self, class_name: str, test_name: str) -> None:
        """Mark a test as passed"""
        data = self.load_test_plan()
        for feature in data.get("features", []):
            if feature.get("class_name") == class_name:
                for test in feature.get("tests", []):
                    if test.get("test_name") == test_name:
                        test["passes"] = True
                        break
                break
        self.save_test_plan(data)

    def all_tests_complete(self) -> bool:
        """Check if all tests are complete and passing"""
        data = self.load_test_plan()
        for feature in data.get("features", []):
            for test in feature.get("tests", []):
                if not test.get("passes", False):
                    return False
        return True

    # ==================== Progress Operations ====================

    def load_progress(self) -> str:
        """Load progress from text file"""
        path = self._get_path(self.PROGRESS)
        if not os.path.exists(path):
            return ""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def save_progress(self, content: str) -> None:
        """Save progress to text file"""
        path = self._get_path(self.PROGRESS)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def append_progress(self, message: str) -> None:
        """Append message to progress file"""
        path = self._get_path(self.PROGRESS)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] {message}\n")

    def get_current_class(self) -> Optional[str]:
        """Get the next class to be tested from progress"""
        content = self.load_progress()
        # Look for "## In Progress" section
        lines = content.split('\n')
        in_progress = False
        for line in lines:
            if '## In Progress' in line:
                in_progress = True
                continue
            if in_progress:
                if line.startswith('- '):
                    return line[2:].split(':')[0].strip()
                if line.startswith('## '):
                    break
        return None

    # ==================== Coverage Report Operations ====================

    def load_coverage_report(self) -> Dict[str, Any]:
        """Load coverage report from JSON file"""
        path = self._get_path(self.COVERAGE_REPORT)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_coverage_report(self, data: Dict[str, Any]) -> None:
        """Save coverage report to JSON file"""
        path = self._get_path(self.COVERAGE_REPORT)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_coverage_status(self) -> Dict[str, float]:
        """Get current coverage status"""
        report = self.load_coverage_report()
        return report.get("overall_coverage", {
            "line": 0.0,
            "branch": 0.0,
            "method": 0.0
        })

    def coverage_targets_met(self) -> bool:
        """Check if coverage targets are met"""
        coverage = self.get_coverage_status()
        line_ok = coverage.get("line", 0.0) >= 0.70
        branch_ok = coverage.get("branch", 0.0) >= 0.60
        return line_ok and branch_ok

    # ==================== Status ====================

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the harness"""
        class_list = self.load_class_list()
        test_plan = self.load_test_plan()
        coverage = self.load_coverage_report()

        total_classes = len(class_list.get("classes", []))
        tested_classes = sum(1 for cls in class_list.get("classes", []) if cls.get("tested", False))

        total_tests = sum(len(f.get("tests", [])) for f in test_plan.get("features", []))
        passed_tests = sum(
            sum(1 for t in f.get("tests", []) if t.get("passes", False))
            for f in test_plan.get("features", [])
        )

        coverage_status = coverage.get("overall_coverage", {})

        return {
            "initialized": self.class_list_exists() and self.test_plan_exists(),
            "total_classes": total_classes,
            "tested_classes": tested_classes,
            "pending_classes": total_classes - tested_classes,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pending_tests": total_tests - passed_tests,
            "coverage": {
                "line": coverage_status.get("line", 0.0),
                "branch": coverage_status.get("branch", 0.0),
                "method": coverage_status.get("method", 0.0)
            },
            "targets_met": self.coverage_targets_met(),
            "all_tests_complete": self.all_tests_complete()
        }

    def reset(self) -> None:
        """Reset all state files"""
        for filename in [self.CLASS_LIST, self.TEST_PLAN, self.PROGRESS, self.COVERAGE_REPORT]:
            path = self._get_path(filename)
            if os.path.exists(path):
                os.remove(path)