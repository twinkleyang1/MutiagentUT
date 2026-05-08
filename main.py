"""
Multi-Agent UT Generation System - Main Entry Point

This system uses three agents to automatically generate unit tests:
1. Planner - Analyzes project and creates test plan
2. Generator - Generates JUnit 5 tests based on plan
3. Evaluator - Verifies test quality and coverage

Usage:
    python main.py --project-path /path/to/java/project [--max-iterations N]

Environment Variables:
    JAVA_PROJECT_PATH: Path to Java project (alternative to --project-path)
    MAX_ITERATIONS: Maximum iterations (default: 50)
"""

import argparse
import os
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional

# Add Agent module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Agent"))

from Agent.shared.file_manager import FileManager
from Agent.shared import constants
from Agent.planner.planner import Planner
from Agent.generator.generator import Generator
from Agent.evaluator.evaluator import Evaluator


class UTGenerationSystem:
    """Main system coordinating multi-agent UT generation"""

    def __init__(self, project_root: str, java_project_path: Optional[str] = None):
        self.project_root = project_root
        self.java_project_path = java_project_path or project_root

        # Initialize file manager
        self.file_manager = FileManager(self.project_root)

        # Initialize agents
        self.planner = Planner(self.project_root, self.file_manager)
        self.generator = Generator(self.project_root, self.file_manager)
        self.evaluator = Evaluator(self.project_root, self.file_manager)

        # State
        self.current_iteration = 0
        self.max_iterations = constants.MAX_ITERATIONS

    def run(self, max_iterations: int = 50) -> Dict[str, Any]:
        """
        Run the UT generation system

        Args:
            max_iterations: Maximum number of iterations

        Returns:
            Final status and results
        """
        print("=" * 60)
        print("Multi-Agent UT Generation System")
        print("=" * 60)

        self.max_iterations = max_iterations

        # Phase 1: Initialization
        print("\n[Phase 1] Initializing...")

        # Check Java project path
        if not os.path.exists(self.java_project_path):
            return {
                "success": False,
                "error": f"Java project not found: {self.java_project_path}"
            }

        src_main_java = os.path.join(self.java_project_path, "src", "main", "java")
        if not os.path.exists(src_main_java):
            return {
                "success": False,
                "error": f"src/main/java not found in: {self.java_project_path}"
            }

        # Phase 2: Planning
        print("\n[Phase 2] Running Planner...")
        plan_result = self.planner.analyze_project(self.java_project_path)
        print(f"  Found {plan_result['total_classes']} classes")

        # Phase 3: Sprint Loop
        print("\n[Phase 3] Running Generator-Evaluator Loop...")

        iteration = 0
        all_complete = False

        while iteration < self.max_iterations and not all_complete:
            iteration += 1
            self.current_iteration = iteration

            print(f"\n  --- Iteration {iteration}/{self.max_iterations} ---")

            # Get next class to test
            class_name = self.generator.get_pending_class()

            if not class_name:
                print("  All classes tested!")
                all_complete = True
                break

            print(f"  Processing: {class_name}")

            # Generate tests
            print(f"  [Generator] Generating tests...")
            gen_result = self.generator.generate_tests(class_name)

            if not gen_result.get("success", False):
                print(f"  [Generator] Failed: {gen_result.get('error', 'Unknown error')}")
                continue

            # Evaluate tests
            print(f"  [Evaluator] Evaluating tests...")
            eval_result = self.evaluator.evaluate_class(class_name)

            # Check status
            if eval_result.get("sprint_status") == constants.SPRINT_STATUS_PASS:
                print(f"  [Evaluator] PASS - Coverage: {eval_result.get('coverage', {})}")

                # Mark class as tested
                self.file_manager.update_class_tested_status(class_name, True)

                # Commit if git available
                self.generator.git_commit(class_name)
            else:
                print(f"  [Evaluator] REWORK - Feedback: {eval_result.get('feedback', [])}")
                # Generator will regenerate on next iteration

            # Check completion
            all_complete = self.file_manager.all_tests_complete()

        # Phase 4: Completion
        print("\n[Phase 4] Finalizing...")

        final_coverage = self.file_manager.get_coverage_status()

        print(f"\n  Final Coverage:")
        print(f"    Line: {final_coverage.get('line', 0)*100:.1f}%")
        print(f"    Branch: {final_coverage.get('branch', 0)*100:.1f}%")
        print(f"    Method: {final_coverage.get('method', 0)*100:.1f}%")

        # Check if targets met
        targets_met = (
            final_coverage.get('line', 0) >= constants.LINE_COVERAGE_THRESHOLD and
            final_coverage.get('branch', 0) >= constants.BRANCH_COVERAGE_THRESHOLD
        )

        print("\n" + "=" * 60)
        if targets_met:
            print("COMPLETION-PROMISE: CODE_IMPROVED")
            print("<promise>CODE_IMPROVED</promise>")
        else:
            print("Coverage targets not fully met, but work is in progress")
        print("=" * 60)

        return {
            "success": True,
            "iterations": iteration,
            "coverage": final_coverage,
            "targets_met": targets_met,
            "promise": "CODE_IMPROVED" if targets_met else None
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Multi-Agent UT Generation System"
    )

    parser.add_argument(
        "--project-root",
        default="/home/twinkle/app/808/Agent_UT/MutiagentUT",
        help="Root directory for UT generation system"
    )

    parser.add_argument(
        "--java-project-path",
        help="Path to Java project to generate tests for"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=50,
        help="Maximum number of iterations"
    )

    args = parser.parse_args()

    # Determine Java project path
    java_project = args.java_project_path or os.environ.get("JAVA_PROJECT_PATH")

    if not java_project:
        print("Error: --java-project-path or JAVA_PROJECT_PATH required")
        sys.exit(1)

    # Create and run system
    system = UTGenerationSystem(
        project_root=args.project_root,
        java_project_path=java_project
    )

    result = system.run(max_iterations=args.max_iterations)

    # Output result as JSON
    print("\n--- Result ---")
    print(json.dumps(result, indent=2))

    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()