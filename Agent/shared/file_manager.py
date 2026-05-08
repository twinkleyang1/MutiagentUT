"""
Shared file management utilities for Multi-Agent UT Generation System
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import constants


class FileManager:
    """Manages shared files for multi-agent coordination"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.shared_dir = os.path.join(project_root, "shared")
        os.makedirs(self.shared_dir, exist_ok=True)

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.shared_dir, filename)

    # ==================== Class List Operations ====================

    def save_class_list(self, data: Dict[str, Any]) -> None:
        """Save class list to JSON file"""
        path = self._get_path(constants.CLASS_LIST_JSON)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_class_list(self) -> Dict[str, Any]:
        """Load class list from JSON file"""
        path = self._get_path(constants.CLASS_LIST_JSON)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ==================== Test Plan Operations ====================

    def save_test_plan(self, data: Dict[str, Any]) -> None:
        """Save test plan to JSON file"""
        path = self._get_path(constants.TEST_PLAN_JSON)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_test_plan(self) -> Dict[str, Any]:
        """Load test plan from JSON file"""
        path = self._get_path(constants.TEST_PLAN_JSON)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ==================== Progress Operations ====================

    def save_progress(self, content: str) -> None:
        """Save progress to text file"""
        path = self._get_path(constants.PROGRESS_TXT)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def load_progress(self) -> str:
        """Load progress from text file"""
        path = self._get_path(constants.PROGRESS_TXT)
        if not os.path.exists(path):
            return ""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def append_progress(self, content: str) -> None:
        """Append to progress file"""
        path = self._get_path(constants.PROGRESS_TXT)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)

    # ==================== Coverage Report Operations ====================

    def save_coverage_report(self, data: Dict[str, Any]) -> None:
        """Save coverage report to JSON file"""
        path = self._get_path(constants.COVERAGE_REPORT_JSON)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_coverage_report(self) -> Dict[str, Any]:
        """Load coverage report from JSON file"""
        path = self._get_path(constants.COVERAGE_REPORT_JSON)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ==================== Utility Methods ====================

    def update_class_tested_status(self, class_name: str, tested: bool) -> None:
        """Update tested status for a class in class_list.json"""
        data = self.load_class_list()
        for cls in data.get("classes", []):
            if cls["name"] == class_name:
                cls["tested"] = tested
                break
        self.save_class_list(data)

    def update_test_pass_status(self, class_name: str, test_name: str, passes: bool) -> None:
        """Update test pass status in test_plan.json"""
        data = self.load_test_plan()
        for feature in data.get("features", []):
            if feature.get("class_name") == class_name:
                for test in feature.get("tests", []):
                    if test.get("test_name") == test_name:
                        test["passes"] = passes
                        break
                break
        self.save_test_plan(data)

    def get_untested_classes(self) -> List[Dict[str, Any]]:
        """Get list of untested classes"""
        data = self.load_class_list()
        return [cls for cls in data.get("classes", []) if not cls.get("tested", False)]

    def get_pending_tests(self, class_name: str) -> List[Dict[str, Any]]:
        """Get pending tests for a specific class"""
        data = self.load_test_plan()
        for feature in data.get("features", []):
            if feature.get("class_name") == class_name:
                return [t for t in feature.get("tests", []) if not t.get("passes", False)]
        return []

    def all_tests_complete(self) -> bool:
        """Check if all tests are complete and passing"""
        data = self.load_test_plan()
        for feature in data.get("features", []):
            for test in feature.get("tests", []):
                if not test.get("passes", False):
                    return False
        return True

    def get_coverage_status(self) -> Dict[str, float]:
        """Get current coverage status"""
        report = self.load_coverage_report()
        return report.get("overall_coverage", {
            "line": 0.0,
            "branch": 0.0,
            "method": 0.0
        })

    def reset(self) -> None:
        """Reset all shared files"""
        for filename in [constants.CLASS_LIST_JSON, constants.TEST_PLAN_JSON,
                         constants.PROGRESS_TXT, constants.COVERAGE_REPORT_JSON]:
            path = self._get_path(filename)
            if os.path.exists(path):
                os.remove(path)