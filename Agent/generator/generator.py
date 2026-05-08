"""
Generator Agent - Generates JUnit 5 unit tests
"""

import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..shared.file_manager import FileManager
from ..shared import constants
from . import prompts
from . import ut_template


class Generator:
    """Generator Agent - Generates unit tests based on test plan"""

    def __init__(self, project_root: str, file_manager: FileManager):
        self.project_root = project_root
        self.file_manager = file_manager
        self.test_output_dir = os.path.join(project_root, "Test")

    def generate_tests(self, class_name: str) -> Dict[str, Any]:
        """
        Generate tests for a specific class

        Args:
            class_name: Name of the class to generate tests for

        Returns:
            Dictionary with generation results
        """
        print(f"[Generator] Generating tests for: {class_name}")

        # Load class info from class_list.json
        class_list = self.file_manager.load_class_list()
        class_info = self._find_class(class_list, class_name)

        if not class_info:
            return {"success": False, "error": f"Class {class_name} not found"}

        # Load source code
        source_code = self._load_source_code(class_info)

        # Analyze source code
        methods = self._extract_methods(source_code, class_info)

        # Generate test content
        test_content = self._generate_test_class(class_info, methods)

        # Save test file
        test_path = self._save_test_file(class_info, test_content)

        # Update progress
        self._update_progress(class_name, test_path)

        return {
            "success": True,
            "class_name": class_name,
            "test_path": test_path,
            "methods_tested": len(methods)
        }

    def generate_all_pending(self) -> List[Dict[str, Any]]:
        """
        Generate tests for all pending classes

        Returns:
            List of generation results
        """
        results = []
        test_plan = self.file_manager.load_test_plan()

        for feature in test_plan.get("features", []):
            class_name = feature.get("class_name")
            tests = feature.get("tests", [])

            # Check if any tests are pending
            pending_tests = [t for t in tests if not t.get("passes", False)]

            if pending_tests:
                result = self.generate_tests(class_name)
                results.append(result)

        return results

    def _find_class(self, class_list: Dict, class_name: str) -> Optional[Dict]:
        """Find class info from class list"""
        for cls in class_list.get("classes", []):
            if cls.get("name") == class_name:
                return cls
        return None

    def _load_source_code(self, class_info: Dict) -> str:
        """Load source code from file"""
        source_path = os.path.join(self.project_root, class_info.get("path", ""))
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[Generator] Error loading source: {e}")
            return ""

    def _extract_methods(self, source_code: str, class_info: Dict) -> List[Dict]:
        """Extract public methods from source code"""
        methods = []
        class_type = class_info.get("type", "other")

        # Pattern for method extraction
        pattern = r'(public|private|protected)?\s+(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)'

        matches = re.finditer(pattern, source_code)

        for match in matches:
            access_mod = match.group(1)
            return_type = match.group(2)
            method_name = match.group(3)
            params = match.group(4)

            # Only include public methods
            if access_mod and 'public' not in access_mod:
                continue

            # Skip constructors and common Object methods
            if method_name in ['toString', 'equals', 'hashCode', 'wait', 'notify', 'notifyAll']:
                continue

            methods.append({
                "name": method_name,
                "return_type": return_type,
                "parameters": params,
                "params_list": [p.strip() for p in params.split(',') if p.strip()]
            })

        return methods

    def _generate_test_class(self, class_info: Dict, methods: List[Dict]) -> str:
        """Generate complete test class content"""
        class_name = class_info.get("name")
        package = class_info.get("package", "")
        class_type = class_info.get("type", "other")

        # Generate mock fields
        mock_fields = self._generate_mock_fields(class_info, methods)

        # Generate constructor args
        constructor_args = self._generate_constructor_args(methods)

        # Generate test methods
        test_methods = self._generate_test_methods(class_info, methods)

        # Get imports
        imports = ut_template.UTTemplate.get_imports(class_type)

        return ut_template.UTTemplate.generate_test_content(
            class_name=class_name,
            package_name=package,
            class_type=class_type,
            mock_fields=mock_fields,
            constructor_args=constructor_args,
            test_methods=test_methods
        )

    def _generate_mock_fields(self, class_info: Dict, methods: List[Dict]) -> List[str]:
        """Generate mock field declarations"""
        mock_types = set()

        # Add common mocks based on class type
        class_type = class_info.get("type", "other")
        if class_type == "service":
            mock_types.add(("Repository", "userRepository"))
            mock_types.add(("Service", "innerService"))
        elif class_type == "controller":
            mock_types.add(("Service", "userService"))

        # Infer from method parameters
        for method in methods:
            for param in method.get("params_list", []):
                # Simple heuristic
                if 'Repository' in param:
                    mock_name = param.split('.')[-1] if '.' in param else param[0].lower() + param[1:]
                    mock_types.add((param, mock_name))
                elif 'Service' in param:
                    mock_name = param.split('.')[-1] if '.' in param else param[0].lower() + param[1:]
                    mock_types.add((param, mock_name))

        mock_fields = []
        for mock_type, mock_name in mock_types:
            mock_fields.append(f"    @Mock\n    private {mock_type} {mock_name};")

        return mock_fields

    def _generate_constructor_args(self, methods: List[Dict]) -> str:
        """Generate constructor arguments"""
        if not methods:
            return ""

        # Use first method's parameters as constructor args
        first_method = methods[0]
        params = first_method.get("params_list", [])

        # Generate placeholder args
        args = []
        for param in params:
            param_type = param.split()[-1] if ' ' in param else param
            if param_type == "String":
                args.append('"test"')
            elif param_type == "int" or param_type == "Integer":
                args.append("0")
            elif param_type == "long" or param_type == "Long":
                args.append("0L")
            elif param_type == "boolean" or param_type == "Boolean":
                args.append("true")
            else:
                args.append("null")

        return ", ".join(args) if args else ""

    def _generate_test_methods(self, class_info: Dict, methods: List[Dict]) -> str:
        """Generate test methods"""
        test_methods = []

        # Add basic test for instance creation
        test_methods.append(self._generate_basic_test(class_info))

        # Add tests for each method
        for method in methods:
            test_methods.append(self._generate_method_test(class_info, method))

        # Add boundary condition tests
        test_methods.append(self._generate_boundary_test(class_info))

        # Add exception test
        test_methods.append(self._generate_exception_test(class_info))

        return "\n".join(test_methods)

    def _generate_basic_test(self, class_info: Dict) -> str:
        """Generate basic instance test"""
        class_name = class_info.get("name")

        return f'''
    @Test
    @DisplayName("Should create instance successfully")
    void shouldCreateInstanceSuccessfully() {{
        // Arrange & Act
        {class_name} instance = new {class_name}();

        // Assert
        assertNotNull(instance);
    }}
'''

    def _generate_method_test(self, class_info: Dict, method: Dict) -> str:
        """Generate test for a specific method"""
        class_name = class_info.get("name")
        method_name = method.get("name")
        return_type = method.get("return_type")
        params = method.get("params_list", [])

        # Generate mock name
        instance_name = class_name[0].lower() + class_name[1:] if len(class_name) > 1 else class_name

        # Generate act statement
        if return_type == "void":
            act = f"{instance_name}.{method_name}({self._generate_args(params)});"
            assert_stmt = "verify(" + instance_name + ")." + method_name + f"({self._generate_args(params)});"
        else:
            call = f"{instance_name}.{method_name}({self._generate_args(params)})"
            act = f"{return_type} result = {call};"
            assert_stmt = f"assertNotNull(result);"

        return f'''
    @Test
    @DisplayName("Should execute {method_name} successfully")
    void shouldExecute{method_name.replace('_', '').title()}Successfully() {{
        // Arrange
        // TODO: Setup mocks if needed

        // Act
        {act}

        // Assert
        {assert_stmt}
    }}
'''

    def _generate_boundary_test(self, class_info: Dict) -> str:
        """Generate boundary condition test"""
        return '''
    @Test
    @DisplayName("Should handle null inputs gracefully")
    void shouldHandleNullInputsGracefully() {
        // Arrange
        // TODO: Setup for null handling

        // Act & Assert
        // TODO: Verify null handling behavior
    }
'''

    def _generate_exception_test(self, class_info: Dict) -> str:
        """Generate exception handling test"""
        return '''
    @Test
    @DisplayName("Should throw exception when invalid input")
    void shouldThrowExceptionWhenInvalidInput() {
        // Arrange
        // TODO: Setup invalid input scenario

        // Act & Assert
        assertThrows(RuntimeException.class, () -> {
            // TODO: Call method with invalid input
        });
    }
'''

    def _generate_args(self, params: List[str]) -> str:
        """Generate argument string for method call"""
        if not params:
            return ""

        args = []
        for param in params:
            param_type = param.split()[-1] if ' ' in param else param
            if param_type == "String":
                args.append('"test"')
            elif param_type in ["int", "Integer", "long", "Long", "double", "Double", "float", "Float"]:
                args.append("0")
            elif param_type in ["boolean", "Boolean"]:
                args.append("true")
            else:
                args.append("null")

        return ", ".join(args)

    def _save_test_file(self, class_info: Dict, content: str) -> str:
        """Save test file and return path"""
        package = class_info.get("package", "")
        class_name = class_info.get("name")

        # Convert package to path
        package_path = package.replace('.', '/') if package else ""
        test_dir = os.path.join(self.test_output_dir, "src", "test", "java", package_path)

        os.makedirs(test_dir, exist_ok=True)

        test_file_path = os.path.join(test_dir, f"{class_name}Test.java")

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[Generator] Saved test to: {test_file_path}")
        return test_file_path

    def _update_progress(self, class_name: str, test_path: str) -> None:
        """Update progress.txt after generating tests"""
        progress = self.file_manager.load_progress()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add to completed section
        lines = progress.split('\n')

        # Find Completed section and add entry
        new_lines = []
        in_completed = False
        for line in lines:
            if "## Completed" in line:
                in_completed = True
            if in_completed and "- None yet" in line:
                new_lines.append(f"- {class_name}: {len(self._get_test_methods(test_path))} tests ({timestamp})")
                in_completed = False
                continue
            new_lines.append(line)

        self.file_manager.save_progress('\n'.join(new_lines))

    def _get_test_methods(self, test_path: str) -> List[str]:
        """Count test methods in generated file"""
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return re.findall(r'@Test[\s\S]*?void\s+(\w+)\(', content)
        except:
            return []

    def git_commit(self, class_name: str, description: str = "") -> bool:
        """
        Commit generated tests to git

        Args:
            class_name: Name of the class
            description: Additional description

        Returns:
            True if commit successful
        """
        try:
            import subprocess
            test_dir = self.test_output_dir

            # Add files
            subprocess.run(["git", "-C", test_dir, "add", "."], check=True)

            # Commit
            commit_msg = f"UT: add tests for {class_name}"
            if description:
                commit_msg += f" - {description}"

            result = subprocess.run(
                ["git", "-C", test_dir, "commit", "-m", commit_msg],
                capture_output=True,
                text=True
            )

            return result.returncode == 0
        except Exception as e:
            print(f"[Generator] Git commit failed: {e}")
            return False

    def get_pending_class(self) -> Optional[str]:
        """Get next class that needs testing"""
        class_list = self.file_manager.load_class_list()

        for cls in class_list.get("classes", []):
            if not cls.get("tested", False):
                return cls.get("name")

        return None

    def get_generation_status(self) -> Dict[str, Any]:
        """Get current generation status"""
        test_plan = self.file_manager.load_test_plan()

        total_tests = 0
        passed_tests = 0

        for feature in test_plan.get("features", []):
            for test in feature.get("tests", []):
                total_tests += 1
                if test.get("passes", False):
                    passed_tests += 1

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pending_tests": total_tests - passed_tests,
            "progress_percent": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }