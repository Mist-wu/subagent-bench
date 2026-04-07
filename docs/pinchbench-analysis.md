# PinchBench 借鉴与改进

## 值得直接继承的部分

### 1. 任务格式简单且审阅友好

`PinchBench` 用 `Markdown + YAML frontmatter` 定义任务，这一点非常适合继续保留。

原因：

- task diff 易读，适合 code review。
- Prompt、Expected Behavior、Grading Criteria、Automated Checks 能放在同一个文件里。
- 新任务的维护成本低，适合快速扩 benchmark。

### 2. 自动评分优先

`PinchBench` 最有价值的地方不是任务题材本身，而是“尽量把判断做成可验证的自动检查”。

这点在 orchestration benchmark 里仍然成立，只是被检查的对象要从最终产物扩展到：

- 是否委托
- 委托次数
- 委托输入是否完整
- 子任务是否并行/串行合理
- 失败后是否 replan
- 最终是否完成集成

### 3. 用 workspace files 模拟真实世界

它没有强依赖真实 API、OAuth、邮件服务，这让 benchmark 更容易复现。

对 orchestration benchmark，同样可以先用：

- 预置文件
- mock trace
- 结构化 artifacts

来验证 main-agent 的委托与编排质量。

## 需要明确改进的部分

### 1. 不能只看 end-to-end

`PinchBench` 更像单 agent 的 end-to-end benchmark。对于 subagent 系统，这会导致错误归因不清：

- 是主 agent 拆错了？
- 还是子 agent 执行差了？
- 还是结果回收失败了？

所以这个库把 orchestration trace 变成一等公民。

### 2. 不能把 delegation 和 execution 混成一个分数

建议分成两层：

- `delegation_score`
- `execution_score`

当前仓库先把 delegation/orchestration 层独立起来。后续如果接真实 subagent runtime，可以把 execution 层并进来。

### 3. 需要显式建模中间过程

要测主 agent，就必须观测中间语义，而不是只看最终文件。最低限度至少要有这些事件：

- `delegate`
- `subagent_result`
- `replan`
- `artifact_written`

### 4. 需要支持 execution-normalized 比较

一个重要实验设计是：

- 固定 subagent 与工具环境
- 只改变 main agent
- 比较最终成功率和 orchestration 评分差异

这个实验比单纯看 end-to-end 排名更能证明“主 agent 分配能力”本身是否重要。

## 结论

如果目标是“研究多 agent 系统里主 agent 分配任务能力”，最合理的路线不是推翻 `PinchBench`，而是：

1. 继承它的任务文件结构和自动评分思路。
2. 增加 orchestration trace 观测层。
3. 在任务层面专门设计 delegation / replan / integration 题目。
4. 再决定是否需要进一步拆成独立 runtime benchmark。

进一步说，比较合理的结构是：

- 用 `PinchBench` 的任务文件风格承载 `C6a / C6b`。
- 用结构化 trace 显式区分 `分配错` 和 `执行错`。
- 把 `T1-T7` 作为主 agent orchestration 任务族。
- 额外补一组 `C6b` 执行任务，单独测 subagent quality。
