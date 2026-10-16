# v1.0.0 validation

验证日期：2026-10-16。该报告区分实际运行、结构检查与尚未覆盖的行为。详细运行数据由本地隔离工作目录生成，不将维护会话、私有数据或完整对话提交到仓库。

## Acceptance criteria

1. Preserve nine phases and three modes; clarify explicit-mode priority.
2. Execute a real, low-cost research loop with code, raw outputs, bounded conclusions, draft, review, revision, and an honest readiness assessment.
3. Resume progress, reject missing evidence, detect altered artifacts, and reopen downstream work.
4. Produce installable standalone-skill and cross-host-plugin packages with consistent versions and no unrelated files.
5. Pass lifecycle/distribution regression tests and Claude's native manifest validation; report untested host imports separately.

## Baseline

基线提交 `b089a37bfd9143426bf00f5cdf7eeff78db73568`，声明版本 0.1.0。

使用原 Skill 的独立任务从合成时序研究开始，实际运行实验而非仅列计划。它可以在有能力的运行平台中完成科学推理和文件产出，因此“没有 CLI”不意味着“原 Skill 完全不能工作”。差距在于：输出格式依赖执行代理，没有标准状态恢复、证据台账、阶段门槛、插件清单、发布构建或回归校验。

试跑也说明科研结论必须有限定：强漂移构造可出现乐观偏差，噪声下降构造可出现相反方向。不能把示例变成“随机划分总是低估误差”的普遍结论。

## v1.0.0 checks

| 检查 | 实际结果 | 能说明什么 |
| --- | --- | --- |
| 流程与分发回归 | 20/20 通过 | 恢复、阻塞、计划结果隔离、证据/输出变更检测、完整及中途入口就绪判断、路径约束、安装不覆盖和确定性发布包 |
| 示例数学与时间隔离检查 | 7/7 通过 | 已知回归系数、划分互斥、未来标签不影响拟合、奇异矩阵显式失败、手算参考值 |
| 公开示例实际运行 | 两次各 7,200 拟合、无失败；9 个确定性输出逐字节一致 | 示例可按已记录配置复现；环境时间/路径记录不参与逐字节比较 |
| Skill 标准校验 | `quick_validate.py` 通过 | 技能入口元数据有效 |
| 版本/路径/文档检查 | `scripts/validate_repo.py` 通过 | 版本一致、资源存在、Markdown 本地链接有效 |
| Claude 原生验证 | Claude Code 2.1.301，两份 manifest 均 `--strict` 通过 | Claude 格式与清单结构被原生工具接受 |
| Claude 实际安装 | 隔离配置中 marketplace add、plugin install、plugin list 成功，识别 1.0.0/enabled | 本地插件安装链路有效；没有调用 Claude 模型 |
| 模式/引文隔离任务 | 三个独立请求分别选择 mentor、mentor、reviewer；拒绝伪造录用率 | 这三例观察到正确路由及对引文指令的隔离，不构成全面安全保证 |

### 迭代过程中观察到的问题

在一次非冻结版本试跑中，阶段 2 的假设间接引用了计划实验 E1；后续将 E1 原地改成 executed，导致早期证据快照失效。CLI 拒绝继续，任务通过 reopen 最早受影响阶段并复核下游而恢复。这验证了变更检测，也暴露了协议说明不足。

改进：明确计划与实际运行使用独立 ID、假设与结果结论使用独立 ID；纠正旧记录时显式重开。该试跑中主代理更新过 CLI，因此只作为迭代证据，不列作最终冻结版本通过证据。

非冻结会话还曾出现一次检查点返回与后续状态读取不一致的观察，原因未确定；重新记录后两次校验均成功。本地另做 30 轮顺序 checkpoint/status 持久化检查，未复现回退。该观察不被宣称为已定位或修复的代码缺陷；最终验收以独立冻结副本为准，持久化记录也不宣称是防篡改或跨运行平台故障恢复系统。

### 最终冻结版验证

最终技能由 17 个源文件构成；`scripts/workflow.py` SHA-256 为 `837834bcc305cf1575c406c9b7ebc5ca08cdb48aea000665347f1016bf962822`。独立任务使用这份冻结副本，不接收先前试跑的数字、预期结论或缺陷诊断。

独立冻结任务实际完成全部九阶段：200 个固定种子 × 5 种预设场景 × 2 种划分 × 4 种模型（包含不可部署的 oracle 诊断），共 8,000 行原始指标、40 格汇总。首次运行 5.49 秒，同配置重跑 5.70 秒；六类确定性产物字节一致，审计重算 360 组汇总量，修订稿的 8 行数值核验通过。

主设定中固定斜率模型的随机验证 MSE 为 1.087919，同模型未来 MSE 为 1.394060；差为 0.306141，近似 95% Monte Carlo 均值区间 [0.281246, 0.331036]，相对低估约 21.96%。平稳与正确指定模型接近零，未来重置设定出现反方向。该数字来自另一独立任务的生成器，不能和基线 46.5% 作性能优劣比较。

实际运行的命令包括：

```bash
python artifacts/experiment.py --config artifacts/config.json --out artifacts/run-001
python artifacts/experiment.py --config artifacts/config.json --out artifacts/run-reproduce
python artifacts/audit_results.py
python artifacts/check_manuscript.py
python tools/workflow.py validate .
```

交付包含范围、假设、事前协议、代码、原始指标、证据台账、初稿、自审、修订稿、逐项回应和投稿判断。九阶段均 done、`current_phase=null`、`workflow_complete=true`；最终校验 `valid=true`、`structural_only`，投稿结论 `not_ready`。真实/独立任务验证和明确研究增量仍是阻塞项；没有真实投稿或模型 API 调用。

主代理以发布源码再次运行 `validate` 确认相同结果，并核对冻结的 17 个源文件哈希均未变化。最后这次流程使用独立计划/运行记录，没有通过忽略校验来推进。

## Scope of confidence

### Post-release follow-up / 发布后补测

2026-10-16，使用官方 npm 包 `@openai/codex@0.163.0`，实际从公开仓库的 `v1.0.0` 标签运行 `codex plugin marketplace add`、`codex plugin add` 和 `codex plugin list`。结果识别 marketplace `research-workflow-marketplace`、插件 `research-workflow`、版本 `1.0.0`，并返回 `installed=true`、`enabled=true`。测试后移除本次新增的安装与来源。该结果补足 CLI 安装链路，不包含模型调用、桌面 UI 或 Work 云端工作区导入。

在临时项目模拟持锁进程 `os._exit(17)`，观察到 `.workflow.lock` 遗留，下一次 checkpoint 以锁定错误退出。该异常恢复缺陷在原标签中仍存在；详见 [缺陷与限制](limitations-v1.0.0.md)。原先冻结科研闭环的验收结果不因此扩展到强制退出恢复。

插件安装后，本会话运行平台技能清单还同时暴露根兼容入口与正式目录的两个 `research-mentor` 条目。根入口转读正式技能；本次没有调用模型，不判断其对实际自动选择的影响，也不将该运行平台观察推广到所有客户端。

以下边界仍成立：

- A source marked verified records agent inspection; the CLI does not fetch the URL or authenticate scholarly claims.
- Matching experiment hashes verifies recorded files, not that an arbitrary command was truly run or that a conclusion follows.
- A successful synthetic example tests workflow mechanics and bounded statistical reasoning, not real-world generalization or novelty.
- An independent skill task tests observed behavior in this host. It is not a statistical model comparison, broad benchmark, or reproducible guarantee of future agent outputs.
- Native Claude checks and installation, plus the post-release Codex CLI installation check above, were exercised here. Full desktop/Work cloud imports, runtime research behavior in those surfaces, and directory review remain separate acceptance work and are not established by package validation.

