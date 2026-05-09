"""
UT Generation Harness - Main Entry Point

This harness coordinates the UT generation process by:
1. Managing state files (shared/ directory)
2. Providing iteration prompts to guide Claude Code
3. Tracking progress and coverage

The actual work (analyzing code, generating tests) is done by Claude Code
based on the prompts in prompts/ directory.

Usage:
    python main.py --init --java-project-path /path/to/java/project
    python main.py --status
    python main.py --prompt

Environment Variables:
    JAVA_PROJECT_PATH: Path to Java project
    PROJECT_ROOT: Root directory of harness (default: current directory)
"""

import argparse
import os
import sys

# Add harness module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "harness"))

from harness import HarnessCoordinator


def cmd_init(coordinator: HarnessCoordinator, args) -> int:
    """Initialize the harness - analyze project and create state files"""
    java_project = args.java_project_path or os.environ.get("JAVA_PROJECT_PATH")

    if not java_project:
        print("Error: --java-project-path or JAVA_PROJECT_PATH required")
        return 1

    if not os.path.exists(java_project):
        print(f"Error: Java project not found: {java_project}")
        return 1

    src_main_java = os.path.join(java_project, "src", "main", "java")
    if not os.path.exists(src_main_java):
        print(f"Error: src/main/java not found in: {java_project}")
        return 1

    print("Initializing UT Generation Harness...")
    print(f"  Java project: {java_project}")
    print(f"  Project root: {coordinator.project_root}")

    # Check if already initialized
    if coordinator.needs_initialization():
        print("\nHarness needs initialization.")
        print("Use ralph-loop or Claude Code to run the PLANNER_PROMPT.")
        print("\nRun:")
        print(f"  cat prompts/PLANNER_PROMPT.md")
        print("\nThen execute the planner tasks and create:")
        print("  - shared/class_list.json")
        print("  - shared/test_plan.json")
        print("  - shared/progress.txt")
    else:
        print("\nHarness already initialized.")
        status = coordinator.get_status()
        print(f"  Total classes: {status.get('total_classes', 0)}")
        print(f"  Tested classes: {status.get('tested_classes', 0)}")

    return 0


def cmd_status(coordinator: HarnessCoordinator) -> int:
    """Show current harness status"""
    status = coordinator.get_status()

    print("UT Generation Harness Status")
    print("=" * 40)
    print(f"Initialized: {status.get('initialized', False)}")
    print(f"Phase: {coordinator.get_current_phase()}")
    print(f"")
    print(f"Classes:")
    print(f"  Total:   {status.get('total_classes', 0)}")
    print(f"  Tested:  {status.get('tested_classes', 0)}")
    print(f"  Pending: {status.get('pending_classes', 0)}")
    print(f"")
    print(f"Tests:")
    print(f"  Total:   {status.get('total_tests', 0)}")
    print(f"  Passed:  {status.get('passed_tests', 0)}")
    print(f"  Pending: {status.get('pending_tests', 0)}")
    print(f"")
    print(f"Coverage:")
    print(f"  Line:    {status.get('coverage', {}).get('line', 0)*100:.1f}%")
    print(f"  Branch:  {status.get('coverage', {}).get('branch', 0)*100:.1f}%")
    print(f"  Method:  {status.get('coverage', {}).get('method', 0)*100:.1f}%")
    print(f"")
    print(f"Targets Met: {status.get('targets_met', False)}")
    print(f"All Complete: {status.get('all_tests_complete', False)}")

    return 0


def cmd_prompt(coordinator: HarnessCoordinator) -> int:
    """Print the current iteration prompt"""
    prompt = coordinator.get_iteration_prompt()
    print(prompt)
    return 0


def cmd_reset(coordinator: HarnessCoordinator, args) -> int:
    """Reset harness state - delete all state files"""
    if not args.force:
        print("This will delete all state files.")
        print("Use --force to confirm.")
        return 1

    print("Resetting harness state...")
    coordinator.state_manager.reset()
    print("Done.")
    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="UT Generation Harness - Coordinate Claude Code for UT generation"
    )

    parser.add_argument(
        "--project-root",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Root directory of the harness (default: current directory)"
    )

    parser.add_argument(
        "--java-project-path",
        help="Path to Java project to generate tests for"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init command
    subparsers.add_parser("init", help="Initialize harness (check if initialized)").add_argument(
        "--java-project-path", help="Path to Java project"
    )

    # status command
    subparsers.add_parser("status", help="Show current harness status")

    # prompt command
    subparsers.add_parser("prompt", help="Print current iteration prompt")

    # reset command
    reset_parser = subparsers.add_parser("reset", help="Reset harness state")
    reset_parser.add_argument("--force", action="store_true", help="Confirm reset")

    # Default: show status
    args = parser.parse_args()

    # Create coordinator
    coordinator = HarnessCoordinator(
        project_root=args.project_root,
        java_project_path=args.java_project_path or os.environ.get("JAVA_PROJECT_PATH", "")
    )

    # Execute command
    if args.command == "init":
        return cmd_init(coordinator, args)
    elif args.command == "status":
        return cmd_status(coordinator)
    elif args.command == "prompt":
        return cmd_prompt(coordinator)
    elif args.command == "reset":
        return cmd_reset(coordinator, args)
    else:
        # Default: show status
        return cmd_status(coordinator, args)


if __name__ == "__main__":
    sys.exit(main() or 0)