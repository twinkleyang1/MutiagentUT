# MutiagentUT

Multi-Agent Unit Test Generation System - 自动生成 Java 项目 UT 测试的多智能体系统

## 项目概述

基于长时间运行智能体架构的 UT 自动生成系统，可以为任意 Java 项目自动编写单元测试。

## 核心架构

```
┌─────────────────────────────────────────────────────┐
│                 Harness Mode (Claude Code 驱动)      │
├─────────────────────────────────────────────────────┤
│  协调层 (Python)                                      │
│  └── harness/ (state_manager + coordinator)          │
│                                                      │
│  执行层 (Claude Code)                                 │
│  └── prompts/ (PLANNER/GENERATOR/EVALUATOR prompts)  │
│                                                      │
│  状态文件 (shared/)                                   │
│  └── class_list.json, test_plan.json, progress.txt   │
│                                                      │
│  Ralph-Loop 控制迭代                                  │
└─────────────────────────────────────────────────────┘
```

## 目录结构

```
/home/twinkle/app/808/Agent_UT/
├── MutiagentUT/              # Harness 代码主目录
│   ├── harness/              # Python 协调层
│   │   ├── state_manager.py  # 状态文件读写
│   │   └── coordinator.py    # 主协调器
│   ├── prompts/              # Claude Code 指令
│   │   ├── PLANNER_PROMPT.md
│   │   ├── GENERATOR_PROMPT.md
│   │   ├── EVALUATOR_PROMPT.md
│   │   └── ITERATION_PROMPT.md
│   ├── scripts/              # 辅助脚本
│   ├── rules/                 # 规则文档
│   ├── shared/               # 共享状态文件
│   ├── Test/                 # 生成的测试输出
│   ├── main.py               # 入口点
│   └── README.md
├── Plan/                     # 架构设计文档
└── Rule/                     # 规则文档
```

## 使用方法

### Harness 命令
```bash
# 检查状态
python main.py status

# 显示当前迭代 prompt
python main.py prompt

# 初始化检查
python main.py init --java-project-path /path/to/java/project

# 重置状态
python main.py reset --force
```

### Ralph-Loop 启动
```bash
cd /home/twinkle/app/808/Agent_UT/MutiagentUT

/ralph-loop "根据 Plan 和 Rule，为 {java_project_path} 生成 UT。覆盖率达到 Line>70%, Branch>60% 时输出 <promise>CODE_IMPROVED</promise>" --max-iterations 50 --completion-promise "CODE_IMPROVED"
```

## 远程仓库

- **GitHub**: https://github.com/twinkleyang1/MutiagentUT
- **SSH**: git@github.com:twinkleyang1/MutiagentUT.git

## 代码推送规则

**重要**: 每次 git commit 创建新分支，不要在同一个分支上连续提交。

### 原因
- 允许多个版本并行存在，便于对比和回溯
- 当某个提交出问题，可以轻松切回之前的分支
- 避免在 master/main 上累积不可追溯的更改

### 流程
1. **创建新分支**: `git checkout -b feature/xxx-YYYYMMDD`
2. **提交代码**: `git add . && git commit -m "description"`
3. **推送远程**: `git push -u origin feature/xxx-YYYYMMDD`
4. **合并方式**: 使用 PR，不要直接 push 到 master

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
