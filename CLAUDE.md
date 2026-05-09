# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MutiagentUT is a multi-agent unit test generation system that coordinates multiple Claude Code instances in a loop to automatically generate UT tests for Java projects. The system uses state files in `shared/` to pass work between agents.

## Commands

```bash
# Initialize harness with a Java project
python main.py init --java-project-path /path/to/java/project

# Show current status
python main.py status

# Show current iteration prompt (what to do next)
python main.py prompt

# Reset all state files
python main.py reset --force
```

## Architecture

```
Planner → Generator → Evaluator → (loop via shared/ state files)
```

**Three Agent Roles:**
- **Planner**: Scans Java project, creates `shared/class_list.json` and `shared/test_plan.json`
- **Generator**: Reads source, generates JUnit 5 tests to `Test/src/test/java/`
- **Evaluator**: Runs `mvn test` + `mvn jacoco:report`, updates `shared/coverage_report.json`

**State Files (shared/):**
- `class_list.json` - Discovered classes with `tested` flag
- `test_plan.json` - Test cases per class with `passes` flag
- `progress.txt` - Human-readable progress tracker
- `coverage_report.json` - Coverage metrics (line, branch, method)

**Phase Flow:**
- `init` → `generate` → `evaluate` → (repeat until) → `complete`
- Phase is determined by which state files exist and their content

**Completion:** When all classes tested, coverage targets met (Line ≥70%, Branch ≥60%), output `<promise>CODE_IMPROVED</promise>`

## Key Files

- `main.py` - Entry point, delegates to `HarnessCoordinator`
- `harness/coordinator.py` - Determines current phase and provides iteration prompts
- `harness/state_manager.py` - Reads/writes state files in `shared/`
- `prompts/` - Agent prompts (PLANNER_PROMPT.md, GENERATOR_PROMPT.md, EVALUATOR_PROMPT.md, ITERATION_PROMPT.md)

## Git Workflow

Create new branch per feature/commit. Never commit to master/main directly.
```bash
git checkout -b feature/xxx-YYYYMMDD
git add . && git commit -m "description"
git push -u origin feature/xxx-YYYYMMDD
```