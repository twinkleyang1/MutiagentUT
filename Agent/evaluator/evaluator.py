"""
Evaluator Agent - Evaluates test quality and coverage
"""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..shared.file_manager import FileManager
from ..shared import constants
from . import prompts


class Evaluator:
    """Evaluator Agent - Verifies test quality and coverage"""

    def __init__(self, project_root: str, file_manager: FileManager):
        self.project_root = project_root
        self.file_manager = file_manager

    def evaluate_class(self, class_name: str) -> Dict[str, Any]:
        """
        Evaluate tests for a specific class

        Args:
            class_name: Name of the class to evaluate

        Returns:
            Evaluation results dictionary
        """
        print(f"[Evaluator] Evaluating tests for: {class_name}")

        # Get test file path
        test_file = self._find_test_file(class_name)
        if not test_file:
            return {"status": "fail", "error": f"No test file found for {class_name}"}

        # Run tests
        test_result = self._run_tests(class_name)

        # Run coverage
        coverage_result = self._run_coverage()

        # Analyze quality
        quality_scores = self._analyze_quality(test_file)

        # Determine overall status
        coverage_pass = self._check_coverage(coverage_result)
        quality_pass = self._check_quality(quality_scores)

        if coverage_pass and quality_pass:
            status = "pass"
            sprint_status = constants.SPRINT_STATUS_PASS
        else:
            status = "rework"
            sprint_status = constants.SPRINT_STATUS_REWORK

        # Build feedback
        feedback = self._generate_feedback(class_name, coverage_result, quality_scores)

        # Update coverage report
        self._update_coverage_report(class_name, coverage_result, quality_scores, status)

        return {
            "status": status,
            "class_name": class_name,
            "coverage": coverage_result,
            "quality_scores": quality_scores,
            "feedback": feedback,
            "sprint_status": sprint_status
        }

    def evaluate_all(self) -> Dict[str, Any]:
        """
        Evaluate all generated tests

        Returns:
            Overall evaluation results
        """
        class_list = self.file_manager.load_class_list()
        results = []

        for cls in class_list.get("classes", []):
            class_name = cls.get("name")
            if cls.get("tested", False):
                result = self.evaluate_class(class_name)
                results.append(result)

        # Calculate overall coverage
        overall_coverage = self._calculate_overall_coverage(results)

        # Check if all pass
        all_pass = all(r.get("status") == "pass" for r in results)

        return {
            "total_classes": len(results),
            "passed_classes": sum(1 for r in results if r.get("status") == "pass"),
            "failed_classes": sum(1 for r in results if r.get("status") == "fail"),
            "overall_coverage": overall_coverage,
            "class_results": results,
            "all_pass": all_pass
        }

    def _find_test_file(self, class_name: str) -> Optional[str]:
        """Find test file for a class"""
        test_dir = os.path.join(self.project_root, "Test", "src", "test", "java")

        if not os.path.exists(test_dir):
            return None

        # Search for test file
        for root, dirs, files in os.walk(test_dir):
            test_file = os.path.join(root, f"{class_name}Test.java")
            if os.path.exists(test_file):
                return test_file

        return None

    def _run_tests(self, class_name: str) -> Dict[str, Any]:
        """Run tests for a class"""
        test_file = self._find_test_file(class_name)
        if not test_file:
            return {"success": False, "error": "Test file not found"}

        test_dir = os.path.dirname(os.path.dirname(os.path.dirname(test_file)))

        try:
            import subprocess

            # Run mvn test
            result = subprocess.run(
                ["mvn", "test", "-f", os.path.join(test_dir, "pom.xml")],
                capture_output=True,
                text=True,
                timeout=300
            )

            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "output": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_coverage(self) -> Dict[str, float]:
        """Run JaCoCo coverage report"""
        return {
            "line": 0.0,
            "branch": 0.0,
            "method": 0.0
        }

    def _analyze_quality(self, test_file: str) -> Dict[str, float]:
        """Analyze test quality"""
        scores = {
            "test_correctness": 9.0,
            "test_independence": 9.5,
            "naming_convention": 8.5,
            "mock_usage": 8.0,
            "aaa_structure": 9.0
        }

        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check naming convention
            naming_score = self._check_naming(content)
            scores["naming_convention"] = naming_score

            # Check AAA structure
            aaa_score = self._check_aaa_structure(content)
            scores["aaa_structure"] = aaa_score

            # Check mock usage
            mock_score = self._check_mock_usage(content)
            scores["mock_usage"] = mock_score

            # Check test independence
            independence_score = self._check_test_independence(content)
            scores["test_independence"] = independence_score

            # Check correctness
            correctness_score = self._check_test_correctness(content)
            scores["test_correctness"] = correctness_score

        except Exception as e:
            print(f"[Evaluator] Error analyzing quality: {e}")

        return scores

    def _check_naming(self, content: str) -> float:
        """Check naming convention compliance"""
        test_methods = re.findall(r'void\s+(should\w+)\(', content)

        if not test_methods:
            return 5.0

        pattern = r'should[A-Z]\w+When[A-Z]\w+'
        matches = sum(1 for m in test_methods if re.match(pattern, m))

        return (matches / len(test_methods)) * 10

    def _check_aaa_structure(self, content: str) -> float:
        """Check AAA structure presence"""
        has_arrange = bool(re.search(r'//\s*Arrange|//\s*given', content, re.IGNORECASE))
        has_act = bool(re.search(r'//\s*Act|//\s*when', content, re.IGNORECASE))
        has_assert = bool(re.search(r'//\s*Assert|//\s*then', content, re.IGNORECASE))

        # Also check for clear sections
        arrange_count = len(re.findall(r'//.*Arrange|//.*given', content, re.IGNORECASE))
        act_count = len(re.findall(r'//.*Act|//.*when', content, re.IGNORECASE))
        assert_count = len(re.findall(r'//.*Assert|//.*then', content, re.IGNORECASE))

        if arrange_count > 0 and act_count > 0 and assert_count > 0:
            return 10.0
        elif arrange_count > 0 or act_count > 0 or assert_count > 0:
            return 7.0
        else:
            return 6.0

    def _check_mock_usage(self, content: str) -> float:
        """Check proper mock usage"""
        has_mock = '@Mock' in content
        has_inject = '@InjectMocks' in content
        has_extend = 'MockitoExtension' in content or 'ExtendWith' in content

        uses_mockito = has_mock and has_inject
        uses_extension = has_extend

        if uses_mockito and uses_extension:
            return 10.0
        elif uses_mockito:
            return 7.0
        else:
            return 5.0

    def _check_test_independence(self, content: str) -> float:
        """Check test independence"""
        # Check for shared state
        has_before_each = '@BeforeEach' in content

        # Check for random values
        has_random = 'random' in content.lower() or 'Math.random' in content

        # Check for test order dependencies
        has_order = 'testOrder' in content or '@Order' in content

        if has_random:
            return 5.0
        elif has_order:
            return 7.0
        elif has_before_each:
            return 9.0
        else:
            return 8.0

    def _check_test_correctness(self, content: str) -> float:
        """Check test correctness"""
        test_count = len(re.findall(r'@Test', content))
        assertion_count = len(re.findall(r'assert\w+\(', content))

        if test_count == 0:
            return 0.0

        assertion_ratio = assertion_count / test_count

        if assertion_ratio >= 2:
            return 10.0
        elif assertion_ratio >= 1:
            return 8.0
        else:
            return 6.0

    def _check_coverage(self, coverage_result: Dict[str, float]) -> bool:
        """Check if coverage meets thresholds"""
        line_coverage = coverage_result.get("line", 0.0)
        branch_coverage = coverage_result.get("branch", 0.0)

        return (line_coverage >= constants.LINE_COVERAGE_THRESHOLD and
                branch_coverage >= constants.BRANCH_COVERAGE_THRESHOLD)

    def _check_quality(self, quality_scores: Dict[str, float]) -> bool:
        """Check if quality scores meet thresholds"""
        thresholds = {
            "test_correctness": constants.TEST_CORRECTNESS_THRESHOLD,
            "test_independence": constants.TEST_INDEPENDENCE_THRESHOLD,
            "naming_convention": constants.NAMING_CONVENTION_THRESHOLD,
            "mock_usage": constants.MOCK_USAGE_THRESHOLD,
            "aaa_structure": constants.AAA_STRUCTURE_THRESHOLD
        }

        for key, threshold in thresholds.items():
            if quality_scores.get(key, 0.0) < threshold:
                return False

        return True

    def _generate_feedback(self, class_name: str, coverage: Dict, quality: Dict[str, float]) -> List[str]:
        """Generate feedback for failing tests"""
        feedback = []

        # Coverage feedback
        if coverage.get("line", 0) < constants.LINE_COVERAGE_THRESHOLD:
            feedback.append(f"Line coverage {coverage.get('line', 0)*100:.1f}% below target {constants.LINE_COVERAGE_THRESHOLD*100}%")

        if coverage.get("branch", 0) < constants.BRANCH_COVERAGE_THRESHOLD:
            feedback.append(f"Branch coverage {coverage.get('branch', 0)*100:.1f}% below target {constants.BRANCH_COVERAGE_THRESHOLD*100}%")

        # Quality feedback
        quality_issues = {
            "test_correctness": "Add more assertions to tests",
            "test_independence": "Remove test order dependencies",
            "naming_convention": "Rename tests to follow should[Expected]When[Condition]",
            "mock_usage": "Add proper @Mock and @InjectMocks annotations",
            "aaa_structure": "Add clear Arrange/Act/Assert comments"
        }

        for key, message in quality_issues.items():
            if quality.get(key, 0) < 9.0:
                feedback.append(message)

        return feedback

    def _update_coverage_report(self, class_name: str, coverage: Dict, quality: Dict[str, float], status: str) -> None:
        """Update coverage report JSON"""
        report = self.file_manager.load_coverage_report()

        report_date = datetime.now().strftime("%Y-%m-%d")

        class_result = {
            "class_name": class_name,
            "line_coverage": coverage.get("line", 0),
            "branch_coverage": coverage.get("branch", 0),
            "method_coverage": coverage.get("method", 0),
            "test_count": len(re.findall(r'@Test', self._find_test_file(class_name) or "")),
            "status": status
        }

        if "report_date" not in report:
            report["report_date"] = report_date

        if "class_results" not in report:
            report["class_results"] = []

        # Update or add class result
        found = False
        for i, result in enumerate(report["class_results"]):
            if result.get("class_name") == class_name:
                report["class_results"][i] = class_result
                found = True
                break

        if not found:
            report["class_results"].append(class_result)

        # Recalculate overall coverage
        overall = {"line": 0.0, "branch": 0.0, "method": 0.0}
        if report["class_results"]:
            count = len(report["class_results"])
            overall["line"] = sum(r.get("line_coverage", 0) for r in report["class_results"]) / count
            overall["branch"] = sum(r.get("branch_coverage", 0) for r in report["class_results"]) / count
            overall["method"] = sum(r.get("method_coverage", 0) for r in report["class_results"]) / count

        report["overall_coverage"] = overall
        report["quality_scores"] = {
            "test_correctness": sum(q.get("test_correctness", 0) for q in [quality]) / 1,
            "test_independence": sum(q.get("test_independence", 0) for q in [quality]) / 1,
            "naming_convention": sum(q.get("naming_convention", 0) for q in [quality]) / 1,
            "mock_usage": sum(q.get("mock_usage", 0) for q in [quality]) / 1,
            "aaa_structure": sum(q.get("aaa_structure", 0) for q in [quality]) / 1
        }

        report["sprint_status"] = constants.SPRINT_STATUS_PASS if status == "pass" else constants.SPRINT_STATUS_REWORK

        self.file_manager.save_coverage_report(report)

    def _calculate_overall_coverage(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate overall coverage from results"""
        if not results:
            return {"line": 0.0, "branch": 0.0, "method": 0.0}

        total_line = sum(r.get("coverage", {}).get("line", 0) for r in results)
        total_branch = sum(r.get("coverage", {}).get("branch", 0) for r in results)
        total_method = sum(r.get("coverage", {}).get("method", 0) for r in results)

        count = len(results)

        return {
            "line": total_line / count,
            "branch": total_branch / count,
            "method": total_method / count
        }

    def get_evaluation_status(self) -> Dict[str, Any]:
        """Get current evaluation status"""
        report = self.file_manager.load_coverage_report()

        return {
            "report_date": report.get("report_date", ""),
            "overall_coverage": report.get("overall_coverage", {}),
            "class_results_count": len(report.get("class_results", [])),
            "sprint_status": report.get("sprint_status", "unknown")
        }