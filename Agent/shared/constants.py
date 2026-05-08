"""
Constants for Multi-Agent UT Generation System
"""

# Agent roles
PLANNER = "planner"
GENERATOR = "generator"
EVALUATOR = "evaluator"

# Shared files
CLASS_LIST_JSON = "class_list.json"
TEST_PLAN_JSON = "test_plan.json"
PROGRESS_TXT = "progress.txt"
COVERAGE_REPORT_JSON = "coverage_report.json"

# Coverage thresholds
LINE_COVERAGE_THRESHOLD = 0.70
BRANCH_COVERAGE_THRESHOLD = 0.60
METHOD_COVERAGE_THRESHOLD = 0.80

# Quality thresholds
TEST_CORRECTNESS_THRESHOLD = 9.0
TEST_INDEPENDENCE_THRESHOLD = 9.0
NAMING_CONVENTION_THRESHOLD = 8.5
MOCK_USAGE_THRESHOLD = 8.0
AAA_STRUCTURE_THRESHOLD = 9.0

# File versions
CURRENT_VERSION = "1.0"
PLAN_VERSION = "1.0"

# Status values
STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_PASS = "pass"
STATUS_FAIL = "fail"

# Test types
TYPE_NORMAL_PATH = "normal_path"
TYPE_BOUNDARY_CONDITION = "boundary_condition"
TYPE_EXCEPTION = "exception"
TYPE_EDGE_CASE = "edge_case"

# Class types
CLASS_TYPE_ENTITY = "entity"
CLASS_TYPE_SERVICE = "service"
CLASS_TYPE_CONTROLLER = "controller"
CLASS_TYPE_UTILS = "utils"
CLASS_TYPE_REPOSITORY = "repository"
CLASS_TYPE_OTHER = "other"

# Git commit patterns
COMMIT_PREFIX = "UT"
COMMIT_TEMPLATE = "{prefix}: add tests for {class_name} - {description}"

# Test naming pattern
TEST_METHOD_PATTERN = "should{expected}When{condition}"

# Coverage report keys
KEY_LINE_COVERAGE = "line"
KEY_BRANCH_COVERAGE = "branch"
KEY_METHOD_COVERAGE = "method"

# Quality score keys
KEY_TEST_CORRECTNESS = "test_correctness"
KEY_TEST_INDEPENDENCE = "test_independence"
KEY_NAMING_CONVENTION = "naming_convention"
KEY_MOCK_USAGE = "mock_usage"
KEY_AAA_STRUCTURE = "aaa_structure"

# Sprint status
SPRINT_STATUS_PASS = "pass"
SPRINT_STATUS_REWORK = "rework"

# Promise message
COMPLETION_PROMISE = "CODE_IMPROVED"

# Max iterations for loop
MAX_ITERATIONS = 50