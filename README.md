# MutiagentUT

Multi-Agent Unit Test Generation System - 多 Agent 循环架构的 UT 自动生成系统

## 项目概述

通过多个 Claude Code 实例相互循环，形成长时间运行的自动化 UT 生成系统，无需依赖 Ralph-Loop。

## 核心架构

```
┌──────────────────────────────────────────────────────────────┐
│               Multi-Agent Loop Architecture                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │ Planner │───▶│Generator│───▶│Evaluator│──┐                  │
│  │  规划器  │    │  生成器  │    │  评估器  │  │                  │
│  └─────────┘    └─────────┘    └─────────┘  │                  │
│       │              │              │       │                  │
│       └──────────────┴──────────────┴───────┘                  │
│                          │                                   │
│                   共享状态文件                               │
│                 (shared/ 目录)                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**核心设计**:
- **Planner**: 扫描项目，生成 class_list.json 和 test_plan.json
- **Generator**: 逐类生成测试，更新状态
- **Evaluator**: 运行测试，检查覆盖率
- **循环**: 通过 shared/ 目录自然形成闭环

## 目录结构

```
/home/twinkle/app/808/Agent_UT/
├── MutiagentUT/              # 主目录
│   ├── harness/              # Python 协调层
│   │   ├── state_manager.py  # 状态文件读写
│   │   └── coordinator.py    # 主协调器
│   ├── prompts/              # Agent 提示词
│   │   ├── PLANNER_PROMPT.md
│   │   ├── GENERATOR_PROMPT.md
│   │   ├── EVALUATOR_PROMPT.md
│   │   └── ITERATION_PROMPT.md
│   ├── scripts/              # 辅助脚本
│   ├── shared/              # 共享状态文件
│   ├── Test/                # 生成的测试输出
│   ├── main.py              # 入口点
│   └── README.md
├── Plan/                     # 架构设计文档
└── Rule/                     # 规则文档
```

## 工作流程

```
1. [Planner] 扫描项目 → shared/class_list.json, test_plan.json
         ↓
2. [Generator] 取类 → 生成测试 → 更新状态
         ↓
3. [Evaluator] 运行测试 → 检查覆盖率
         ↓
4. [Generator] 取下一个类 → ...
         ↓
... 循环直到完成 ...
         ↓
5. [Evaluator] 覆盖率达标 → 输出 <promise>CODE_IMPROVED</promise>
```

## 使用方法

### 1. 初始化 Harness
```bash
cd /home/twinkle/app/808/Agent_UT/MutiagentUT
python main.py init --java-project-path /home/twinkle/app/808/Agent_UT/dianping
```

### 2. 查看状态和应该执行的角色
```bash
python main.py status    # 显示当前状态
python main.py prompt    # 显示当前应该执行的角色和任务
```

### 3. Claude Code 执行
- **如果 phase=init**: 作为 Planner 工作
- **如果 phase=generate**: 作为 Generator 工作
- **如果 phase=evaluate**: 作为 Evaluator 工作

### 4. 完成交接
- 执行完成后，检查状态
- 根据状态决定下一个 Agent 角色
- 继续循环直到输出 `<promise>CODE_IMPROVED</promise>`

## Agent 角色

### Planner (规划器)
**触发条件**: `shared/class_list.json` 不存在

**职责**:
1. 扫描 `{project_path}/src/main/java/` 下所有 .java 文件
2. 分类: service/controller/repository/entity/utils/other
3. 生成 `shared/class_list.json`
4. 生成 `shared/test_plan.json`
5. 生成 `shared/progress.txt`

### Generator (生成器)
**触发条件**: 有未测试的类

**职责**:
1. 从 class_list.json 获取下一个未测试的类
2. 读取源代码
3. 生成 JUnit 5 测试到 `Test/src/test/java/{package}/{ClassName}Test.java`
4. 更新 class_list.json (tested=true)
5. 更新 test_plan.json (passes=true)
6. 更新 progress.txt

### Evaluator (评估器)
**触发条件**: 有新生成的测试

**职责**:
1. 运行 `mvn test`
2. 运行 `mvn jacoco:report`
3. 解析覆盖率
4. 更新 `shared/coverage_report.json`
5. 达标时输出 `<promise>CODE_IMPROVED</promise>`

## 远程仓库

- **GitHub**: https://github.com/twinkleyang1/MutiagentUT
- **SSH**: git@github.com:twinkleyang1/MutiagentUT.git

## 代码推送规则

**重要**: 每次 git commit 创建新分支，不要在同一个分支上连续提交。

### 原因
- 允许多个版本并行存在，便于对比和回溯
- 当某个提交出问题，可以轻松切回之前的分支

### 流程
1. **创建新分支**: `git checkout -b feature/xxx-YYYYMMDD`
2. **提交代码**: `git add . && git commit -m "description"`
3. **推送远程**: `git push -u origin feature/xxx-YYYYMMDD`
4. **合并方式**: 使用 PR，不要直接 push 到 master

## UT 编写规范

### 命名约定
```java
// 测试类
class UserServiceImplTest { }

// 测试方法: should[预期行为]When[条件]
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

## 完成条件

输出 `<promise>CODE_IMPROVED</promise>` 当满足:
1. 所有类的 `tested=true`
2. 所有测试的 `passes=true`
3. Line coverage >= 70%
4. Branch coverage >= 60%

## 相关文档

- [架构设计 Plan](./Plan/Multi_Agent_UT_Generation_Plan.md)
- [Java UT 测试规范](./Rule/Java_UT_Testing_Rules.md)
- [长时间运行 Agent 规范](./Rule/Long_Running_Agent_Rules.md)