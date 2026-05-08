"""
Generator Agent Prompts for Multi-Agent UT Generation System
"""

# UT Generation prompt
UT_GENERATION_PROMPT = """You are the Generator Agent in a Multi-Agent UT Generation System.

Your task is to generate JUnit 5 unit tests following the Java UT Testing Rules.

## Source Class Information
- Class: {class_name}
- Package: {package}
- Type: {class_type}
- Source Path: {source_path}

## Test Requirements

Generate tests following these standards:

### 1. Naming Convention
- Test class: [ClassName]Test.java
- Test method: should[ExpectedBehavior]When[Condition]

### 2. AAA Pattern
```java
@Test
void shouldReturnUserWhenUserExists() {
    // Arrange - prepare test data and mocks
    User expected = new User("1", "Alice");
    when(userRepository.findById("1")).thenReturn(expected);

    // Act - execute method under test
    User result = userService.getUser("1");

    // Assert - verify results
    assertNotNull(result);
    assertEquals("Alice", result.getName());
    verify(userRepository).findById("1");
}
```

### 3. Test Coverage Types
- Normal Path: Basic functionality
- Boundary Condition: null, 0, empty, max values
- Exception: Error handling
- Edge Case: Special values

### 4. Mock Usage
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;
}
```

## Output
Generate complete test file content for the given class.
Follow the rules exactly. Return only the test code."""

# Test method generation prompt
TEST_METHOD_PROMPT = """Generate test method for:

Class: {class_name}
Method: {method_name}
Return Type: {return_type}
Parameters: {parameters}

Test Type: {test_type}

Generate a single test method following:
- should[Expected]When[Condition] naming
- AAA pattern (Arrange/Act/Assert)
- Proper Mock usage if needed

Return the test method code only."""

# Boundary condition prompt
BOUNDARY_CONDITION_PROMPT = """Design boundary condition tests for:

Class: {class_name}

Consider these boundary cases:
1. null input
2. empty string / empty collection
3. zero values
4. maximum values
5. negative values (if applicable)

Return test methods covering these scenarios."""

# Exception handling prompt
EXCEPTION_HANDLING_PROMPT = """Design exception handling tests for:

Class: {class_name}
Method: {method_name}

Identify:
1. What exceptions can be thrown
2. What conditions trigger exceptions
3. How exceptions should be handled

Return test methods for exception scenarios."""

# Mock setup prompt
MOCK_SETUP_PROMPT = """Set up mocks for testing:

Class Under Test: {class_name}
Dependencies: {dependencies}

For each dependency:
1. Create @Mock field
2. Create @InjectMocks field
3. Set up return values in Arrange section

Return mock setup code."""

# Verification prompt
VERIFICATION_PROMPT = """What assertions and verifications are needed for:

Class: {class_name}
Method: {method_name}

Consider:
1. Return value assertions
2. State change assertions
3. Method call verifications (verify)
4. Exception assertions (assertThrows)

Return assertion code."""