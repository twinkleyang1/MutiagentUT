# ITERATION PROMPT

这是 UT Generation Harness 的主迭代模板。根据当前状态，决定下一步操作。

## 当前状态

```
Project: {project_path}
Phase: {phase}
Tested Classes: {tested}/{total}
Passed Tests: {passed}/{total_tests}
Coverage: Line {line}%, Branch {branch}%
Targets Met: {targets_met}
All Tests Complete: {all_complete}
```

## 阶段判断逻辑

```
IF class_list.json 不存在 THEN phase = "init"
ELSE IF tested_classes == 0 THEN phase = "generate"
ELSE IF targets_met == false THEN phase = "evaluate"
ELSE IF all_complete == true THEN phase = "complete"
ELSE phase = "generate"
```

## 阶段指令

### Phase: init

参见 `prompts/PLANNER_PROMPT.md`

### Phase: generate

参见 `prompts/GENERATOR_PROMPT.md`

### Phase: evaluate

参见 `prompts/EVALUATOR_PROMPT.md`

### Phase: complete

```
## 任务完成

所有测试已生成，覆盖率目标已达成。

输出: <promise>CODE_IMPROVED</promise>
```

## 通用规则

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

## Claude Code 操作指南

1. 读取 `shared/` 下的状态文件了解当前进度
2. 根据 phase 选择对应的 prompt
3. 执行任务后更新状态文件
4. 检查是否满足完成条件

## 错误处理

如果某一步失败：
1. 记录错误信息到 `shared/progress.txt`
2. 提供具体的修复建议
3. 继续下一个 iteration