# 上手指南：从安装到看到结果

这个仓库把科研过程组织成一个可调用的技能：你向宿主 AI 提供任务，它读取相应阶段的指导，使用宿主已有的工具完成研究工作，再把产物、证据和进度保存下来。

先分清三个入口：

| 入口 | 你在哪里操作 | 实际作用 |
| --- | --- | --- |
| `research-mentor` 技能 | Claude Code、Codex 等支持技能的宿主对话中 | 指导 AI 阅读、分析、执行实验、写作和审查 |
| `examples/drift-study/experiment.py` | 本地终端 | 运行仓库附带的一个合成实验，查看真实结果文件 |
| `skills/research-mentor/scripts/workflow.py` | 本地终端，通常由 AI 调用 | 初始化项目、保存检查点、校验文件与恢复进度；不会调用模型或执行实验 |

只想先看结果，做第 1 节。想用它研究自己的问题，从第 2 节开始。已有项目或论文，直接看第 4 节。

## 1. 先跑一个不需要 AI 的示例

需要 Git、Python 3.10+；不需要 GPU、API Key 或第三方 Python 包。以下命令在终端执行，后续命令均以仓库根目录为工作目录。若已经克隆仓库，直接进入现有目录。

```bash
git clone https://github.com/HaoYangJin/Research-workflow-Skill.git
cd Research-workflow-Skill
python examples/drift-study/experiment.py --out ./outputs/first-demo
```

输出目录必须不存在或为空；再次运行时换一个目录，例如 `./outputs/second-demo`，以保留上一次结果。

实验研究的是：**时间序列发生漂移时，内部留出误差与未来预测误差会怎样变化？** 默认完成 7,200 次拟合。它是一个已写好的合成实验示例，不能代替自己的研究，也不会自动生成完整九阶段项目。

命令完成后，按这个顺序查看：

| 文件（均位于 `outputs/first-demo/`） | 看什么 |
| --- | --- |
| `summary.md` | 先读结果概览 |
| `summary.csv` | 比较不同情形、模型和划分协议的误差 |
| `paired_contrasts.csv` | 查看配对比较 |
| `replicates.csv` | 回溯到逐种子的原始指标 |
| `config_used.json`、`environment.json` | 核对实验配置、环境与运行信息 |
| `hypotheses.json`、`analytic_reference.json` | 查看事前假设检查和解析参照 |

**完成标志**：终端返回 `failed_fits: 0`，上述文件存在；能从 `summary.csv` 找到具体数值，而不只是得到一段文字建议。如何解释结果及其限制，见 [示例说明](../examples/drift-study/README.md)、[冻结协议](../examples/drift-study/protocol.md)。

## 2. 安装技能并发起第一次任务

### 2.1 选择一种安装方式

同一宿主只需启用一种方式。

**Claude Code 插件**：在 Claude Code 中依次输入，以下不是终端命令：

```text
/plugin marketplace add HaoYangJin/Research-workflow-Skill
/plugin install research-workflow@research-workflow-marketplace
```

安装后调用：

```text
/research-workflow:research-mentor
```

**独立 Skill**：在已克隆的仓库根目录中，根据宿主实际使用的技能目录安装：

```bash
# Claude Code 的独立 Skill 目录
python scripts/install_skill.py --target ~/.claude/skills/research-mentor

# 使用 ~/.agents/skills/ 的 Codex 配置
python scripts/install_skill.py --target ~/.agents/skills/research-mentor
```

这两条是替代选项，只运行与你的宿主对应的一条。目标目录已有内容时，安装脚本会拒绝覆盖。其他宿主的 ZIP 导入、Windows 路径和更新方式见 [安装参考](../USAGE.md)。

**完成标志**：宿主能加载 `research-mentor`。能够克隆仓库或运行 Python 脚本，只说明文件可用，还需要在宿主中启用技能。插件导入是否可用取决于宿主与账户；Codex 完整插件导入的验证范围见 [版本验证报告](validation-v1.0.0.md)。

### 2.2 复制这段话开始

在已启用技能的 AI 对话中发送。将输出目录替换成你有写权限的空目录；有现成研究时，把问题和材料换成自己的。

```text
使用 research-mentor，混合模式。

研究问题：时间序列发生漂移时，随机划分是否会低估未来预测误差？
已有材料：暂无，可使用公开一手文献和合成数据。
资源限制：Python 标准库，不用 GPU、不调用付费 API。
输出目录：<填写一个空目录的绝对路径>。

请先检查你能否检索来源、执行代码和写入文件，再推进一个低成本科研闭环。
执行前冻结假设、对照、指标、种子与预算；实际运行实验并保存结果。
随后写短稿、自审、修改，最后判断是否具备投稿条件。
每个阶段保存产物和证据关联；做不到的部分记录原因，不要当作已完成。
本轮先完成阶段 1 的真实产物和检查点，并报告结果，等待我继续。
```

**完成标志**：AI 报告当前阶段、实际文件位置、来源或证据缺口，以及下一步行动。若宿主没有执行或写文件能力，应明确说明限制；对话中的草稿不等于已落盘的项目。

## 3. 从第一个阶段推进到研究交付

确认第一阶段产物后，在同一项目上下文中发送：

```text
继续当前 research-mentor 项目。先读取 project.json、evidence.json 和已有产物，
检查当前阶段，再按已确认预算继续下一阶段。需要改变协议或遇到阻塞时先说明原因。
```

九阶段是研究地图，可以按任务范围选择；完整项目的每一阶段应留下可检查的东西：

| 阶段 | 你应该看到的产物 | 你要确认什么 |
| --- | --- | --- |
| 1. 文献与范围 | 问题边界、检索记录、文献地图 | 来源是否真的读过，问题是否足够具体 |
| 2. 问题与假设 | 可检验假设、失败条件、贡献边界 | 什么结果会推翻假设 |
| 3. 实验设计 | 对照、指标、分析计划、预算与停止规则 | 是否在执行前固定协议 |
| 4. 数据与复现 | 数据来源、划分、泄漏检查、环境与复现命令 | 能否追溯数据与执行条件 |
| 5. 结果与消融 | 实际输出、比较、不确定性和负结果 | 结论是否超出证据范围 |
| 6. 论文初稿 | 可阅读的稿件、结论与证据关联 | 是否真的生成了稿件文件 |
| 7. 自审 | 有位置、有严重度的问题清单 | 哪些问题会阻止结论成立 |
| 8. 修改与回应 | 问题 → 实际修改 → 证据位置 | 是否修改了文件，而不只是承诺修改 |
| 9. 投稿就绪判断 | `ready` 或 `not_ready`、阻塞项、下一步 | 判断依据是否完整，是否仍缺验证 |

导师模式偏重行动建议；审稿模式偏重检查已有材料；混合模式同时给出两种视角。这仍是同一个 AI 的自审，不等于独立同行评审。

有文件执行能力时，项目会使用下面的结构。`artifacts/` 内部的文件名由实际任务决定，不要求固定命名：

```text
你的研究目录/
  project.json     进度、模式、阶段检查点与历史
  evidence.json    来源、实验、结论及其关联
  artifacts/      阶段记录、协议、脚本、结果、稿件与审查材料
```

**完成标志**：阶段产物可打开，记录能关联到真实来源和输出；完成本次任务时说明剩余问题。`not_ready` 可以是完整而诚实的最终判断，九阶段结束不代表论文已经可以录用。

## 4. 只做一个阶段或继续已有项目

### 只需要单次帮助

直接在启用技能的宿主对话中发送，不必先初始化项目：

```text
使用 research-mentor，导师模式。把下面的研究兴趣收敛成一个可检验问题：<兴趣与资源>。
```

```text
使用 research-mentor，审稿模式。审查这份实验设计：<粘贴内容或提供文件>。
区分已经确认的问题与尚缺的信息，并给出修复和验收方法。
```

### 中断后恢复

新对话中提供原项目目录，而不是再创建一个空项目：

```text
使用 research-mentor，混合模式。继续项目：<原项目目录的绝对路径>。
先运行 status，读取 project.json、evidence.json 和当前阶段关联文件。
如发现缺失或变更，先诊断；确认完整后从保存的阶段继续。
```

也可在仓库根目录手动查看。将 `./my-study` 换成真实项目路径：

```bash
python skills/research-mentor/scripts/workflow.py status ./my-study
python skills/research-mentor/scripts/workflow.py validate ./my-study
```

| 看到的状态 | 如何处理 |
| --- | --- |
| `done` | 阶段产物通过结构检查，继续当前未完成阶段；仍需检查科学质量 |
| `blocked` | 读取阻塞原因，补齐数据、来源或资源，再继续该阶段 |
| `skipped` | 核对跳过理由是否符合本次范围，不能用它掩盖必要验证 |
| 校验失败或上游内容改变 | 找到最早受影响的阶段，执行 `reopen`，再复核下游 |
| 阶段 9 为 `not_ready` | 按未解决问题继续研究，不应据此自动投稿 |

例如，实验设计改变且最早影响阶段 3 时：

```bash
python skills/research-mentor/scripts/workflow.py reopen ./my-study --phase 3 --reason "实验设计改变，需要复核下游证据"
```

这会清除阶段 3 及下游检查点，保留原文件供复核，不会替你重新执行实验。

## 5. 常见卡点

| 现象 | 下一步 |
| --- | --- |
| 输入 `/plugin` 后终端提示命令不存在 | marketplace 命令应在 Claude Code 内输入；本地实验命令才在终端运行 |
| 输出只有建议，没有文件 | 确认宿主具有写入与执行能力，并提供可写输出目录；要求报告实际文件路径 |
| `template` 只打印 JSON | 这是正常行为；保存模板、填写真实内容，再 `checkpoint`，不要把未填写模板当成果 |
| 检索或算力不可用 | 缩小研究范围或记录 `blocked`；明确哪些结论尚未验证 |
| 初始化或示例拒绝写入目录 | 使用新的空目录；恢复项目时使用 `status`，不要重复 `init` |
| `valid: true`，但结论仍不可靠 | 校验只覆盖结构、引用关联与文件完整性；另查来源支持程度、实验公平性和统计方法 |

手动创建阶段 JSON、证据台账及检查点时，先读 [状态协议](../skills/research-mentor/references/project-state.md)。需要了解搜索、论文、执行和导出工具如何衔接，见 [能力适配说明](../skills/research-mentor/references/tool-adapters.md)。
