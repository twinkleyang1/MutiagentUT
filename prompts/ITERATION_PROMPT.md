# ITERATION PROMPT - Ralph Loop Mode

这是 UT Generation Harness 的主迭代模板，专为 Ralph Loop 设计。每次迭代自动判断当前阶段并执行相应角色。

## Ralph Loop 配置

```
/ralph-loop:ralph-loop "执行 UT 生成任务" --completion-promise "CODE_IMPROVED" --max-iterations 200
```

## 当前状态

```
Project: /home/twinkle/app/808/Agent_UT/dianping
Phase: {phase}
Tested Classes: {tested}/{total}
Passed Tests: {passed}/{total_tests}
Coverage: Line {line}%, Branch {branch}%
```

## 阶段判断逻辑

自动判断当前 phase：

```
IF class_list.json 不存在 THEN phase = "init"
ELSE IF 所有类 tested=true AND 覆盖率达到标 THEN phase = "complete"
ELSE IF 有新测试生成 THEN phase = "evaluate"
ELSE phase = "generate"
```

## 执行流程

### Phase: init (初始阶段)

参见 `prompts/PLANNER_PROMPT.md`

**任务**:
1. 扫描 `/home/twinkle/app/808/Agent_UT/dianping/src/main/java/` 下所有 `.java` 文件
2. 分类：service/controller/repository/entity/utils/other
3. 生成 `shared/class_list.json`
4. 生成 `shared/test_plan.json`
5. 生成 `shared/progress.txt`

**当前状态**: class_list.json 已存在，扫描完成 (73 个类)

---

### Phase: generate (生成阶段)

参见 `prompts/GENERATOR_PROMPT.md`

**任务**:
1. 从 `shared/class_list.json` 获取下一个未测试的类
2. 读取该类的源代码
3. 生成 JUnit 5 测试到 `src/test/java/{package}/{ClassName}Test.java`
4. 更新 `shared/class_list.json` (tested=true)
5. 更新 `shared/test_plan.json` (passes=true)
6. 更新 `shared/progress.txt`

**重要: Mock 规则**:
- 所有外部依赖必须使用 `@Mock` 注解 Mock
- ServiceImpl 类的 MyBatis 链式调用 (query(), orderByDesc() 等) 无法直接 Mock
- 对于 ServiceImpl，优先测试独立方法（不含 MyBatis 链式调用的方法）
- 或者使用更简单的 Stub 方式测试
- Controller 层测试最简单高效，优先覆盖

---

### Phase: evaluate (评估阶段)

参见 `prompts/EVALUATOR_PROMPT.md`

**任务**:
1. 运行 `cd /home/twinkle/app/808/Agent_UT/dianping && mvn test`
2. 运行 `cd /home/twinkle/app/808/Agent_UT/dianping && mvn jacoco:report`
3. 解析覆盖率 (目标: Line > 70%, Branch > 60%)
4. 更新 `shared/coverage_report.json`

---

### Phase: complete (完成阶段)

```
## 任务完成

所有测试已生成，覆盖率目标已达成。

输出: <promise>CODE_IMPROVED</promise>
```

## 规则

1. **状态文件位置**: `shared/` 目录
   - `class_list.json` - 类列表
   - `test_plan.json` - 测试计划
   - `progress.txt` - 进度
   - `coverage_report.json` - 覆盖率

2. **测试输出位置**: `Test/src/test/java/`

3. **覆盖率目标**:
   - Line > 70%
   - Branch > 60%
   - Method > 80%

4. **测试命名**: `should[Expected]When[Condition]`

5. **AAA 模式**:
   ```java
   @Test
   void shouldReturnXWhenY() {
       // Arrange
       ...

       // Act
       ...

       // Assert
       ...
   }
   ```

6. **完成条件**:
   - 所有测试通过
   - 覆盖率达标 (Line > 70%, Branch > 60%)
   - 输出: `<promise>CODE_IMPROVED</promise>`

## 执行规则

1. 读取 `shared/` 下的状态文件了解当前进度
2. 根据 phase 选择对应的 prompt
3. 执行任务后更新状态文件
4. 检查是否满足完成条件
5. 如果未完成，继续下一个 iteration (Ralph Loop 会自动循环)

## 错误处理

如果某一步失败：
1. 记录错误信息到 `shared/progress.txt`
2. 提供具体的修复建议
3. 继续下一个 iteration