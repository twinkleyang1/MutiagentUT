# MutiagentUT

Multi-Agent Unit Test Generation System - 自动生成 Java 项目 UT 测试的多智能体系统

## 项目概述

基于长时间运行智能体架构的 UT 自动生成系统，可以为任意 Java 项目自动编写单元测试。

## 核心架构

```
┌─────────────────────────────────────────────────────┐
│  规划器 (Planner)  → 分析项目结构，生成测试计划      │
│  生成器 (Generator) → 逐个类编写 UT 测试              │
│  评估器 (Evaluator) → 验证测试质量和覆盖率            │
└─────────────────────────────────────────────────────┘
```

## 目录结构

```
/home/twinkle/app/808/Agent_UT/
├── MutiagentUT/              # Agent 代码主目录
│   ├── Agent/
│   │   ├── planner/          # 规划器 (planner.py, prompts.py)
│   │   ├── generator/        # 生成器 (generator.py, ut_template.py, prompts.py)
│   │   ├── evaluator/        # 评估器 (evaluator.py, prompts.py)
│   │   └── shared/           # 共享工具 (file_manager.py, constants.py)
│   ├── Test/                 # 生成的测试输出
│   ├── shared/               # 共享协调文件 (class_list.json, test_plan.json, progress.txt, coverage_report.json)
│   ├── main.py               # 入口点
│   └── README.md
├── Plan/                     # 架构设计文档
├── Rule/                     # 规则文档
│   ├── Java_UT_Testing_Rules.md
│   └── Long_Running_Agent_Rules.md
└── Test/                     # 生成的测试输出
```

## 使用方法

```bash
# 分析 Java 项目并生成测试
python main.py --java-project-path /path/to/java/project --max-iterations 50

# 或通过环境变量
export JAVA_PROJECT_PATH=/path/to/java/project
python main.py --max-iterations 50
```

## 远程仓库

- **GitHub**: https://github.com/twinkleyang1/MutiagentUT
- **SSH**: git@github.com:twinkleyang1/MutiagentUT.git

## 代码推送规则

所有代码修改必须遵循以下流程：

1. **每次功能完成** → 立即提交到本地 Git
2. **提交信息规范**：
   ```
   feat: [功能描述]

   - 具体改动1
   - 具体改动2

   Progress: X/Y classes complete
   ```
3. **推送到远程** → 每次提交后立即推送到 origin/master

## 智能体职责

### 规划器 (Planner)
- 扫描 Java 项目结构
- 生成 class_list.json（所有待测类列表）
- 生成 test_plan.json（详细测试计划）

### 生成器 (Generator)
- 根据测试计划逐个类编写 UT
- 遵循 AAA 模式（Arrange-Act-Assert）
- 使用 JUnit 5 + Mockito
- 覆盖边界条件（null、0、空值、最大值）
- 每次完成后 Git commit + push

### 评估器 (Evaluator)
- 运行 `mvn test` 执行测试
- 运行 JaCoCo 分析覆盖率
- 验证质量标准
- 覆盖率目标：行 > 70%，分支 > 60%

## UT 编写规范

### 命名约定
```java
// 测试类
class UserServiceImplTest { }

// 测试方法：should[预期行为]When[条件]
void shouldReturnUserWhenUserExists()
void shouldThrowExceptionWhenIdIsNull()
```

### AAA 模式
```java
@Test
void shouldReturnUserWhenUserExists() {
    // Arrange - 准备测试数据和 Mock
    User expected = new User("1", "Alice");
    when(userRepository.findById("1")).thenReturn(expected);

    // Act - 执行被测方法
    User result = userService.getUser("1");

    // Assert - 验证结果
    assertNotNull(result);
    assertEquals("Alice", result.getName());
}
```

### 覆盖率要求
| 类型 | 最低目标 | 良好目标 |
|------|----------|----------|
| 行覆盖率 | 70% | 90% |
| 分支覆盖率 | 60% | 80% |
| 方法覆盖率 | 80% | 95% |

## 共享文件格式

### class_list.json
```json
{
  "project_path": "/path/to/java/project",
  "classes": [
    {
      "name": "UserServiceImpl",
      "package": "com.example.service.impl",
      "type": "service",
      "priority": 1,
      "tested": false
    }
  ]
}
```

### progress.txt
```
## 已完成
- UserServiceImpl: 5 tests

## 进行中
- ShopServiceImpl: 2/7 tests

## 待完成
- BlogController
- VoucherOrderController
```

### coverage_report.json
```json
{
  "overall_coverage": {
    "line": 0.72,
    "branch": 0.65
  },
  "quality_scores": {
    "test_correctness": 9.5,
    "naming_convention": 9.0
  },
  "sprint_status": "pass"
}
```

## 开发流程

### Phase 1: 初始化
```
规划器扫描项目 → 生成 class_list.json → 生成 test_plan.json
```

### Phase 2: Sprint 循环
```
生成器编写 UT → 评估器验证 → 通过则下一类，不通过则返工
```

### Phase 3: 完成
```
最终覆盖率检查 → 生成报告 → 输出 <promise>CODE_IMPROVED</promise>
```

## 相关文档

- [架构设计 Plan](./Plan/Multi_Agent_UT_Generation_Plan.md)
- [Java UT 测试规范](./Rule/Java_UT_Testing_Rules.md)
- [长时间运行 Agent 规范](./Rule/Long_Running_Agent_Rules.md)
