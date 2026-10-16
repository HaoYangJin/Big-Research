# Research Workflow

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://github.com/HaoYangJin/Research-workflow-Skill/actions/workflows/ci.yml/badge.svg)

**面向科研九阶段的导师与审稿插件：用真实产物、证据关联和可恢复检查点推进研究。**

An evidence-aware research mentor/reviewer plugin with nine research phases, reproducible artifacts, and resumable checkpoints.

## 中文

### v1.0.0 能做什么

- 保留 `research-mentor` 技能与 `mentor / reviewer / mixed` 三种模式；只加载当前阶段需要的参考资料。
- 覆盖选题与文献、假设、实验设计、数据复现、结果消融、写作、自审、修改回应、投稿就绪判断。
- 用 `project.json` 保存进度，用 `evidence.json` 关联来源、实际实验与结论；缺证据时记录阻塞。
- 提供 Python 标准库 CLI：初始化、检查点、验证、恢复，以及产物变更检测。
- 提供 Claude 与 Codex 插件清单、Claude marketplace、独立 Skill 安装与可重复构建的发布包。
- 按能力连接宿主已有的搜索、论文、执行、文件与 Git 工具；工具不可用时明确降级。

**适用边界**：它是需要宿主 AI 和工具执行的科研工作流，不是独立训练/检索服务。CLI 检查结构、关联和文件完整性，不认证科学正确性，不保证创新性或录用。没有绑定或假装实现远程 MCP 服务。

### 快速开始

Claude Code 插件安装：

```text
/plugin marketplace add HaoYangJin/Research-workflow-Skill
/plugin install research-workflow@research-workflow-marketplace
```

也可在已克隆的仓库中本地试用：

```bash
claude --plugin-dir .
```

调用插件技能：

```text
/research-workflow:research-mentor
混合模式。请用可复现的低成本实验推进我的研究：<问题、已有材料、预算、输出目录>。
```

单独安装 Skill（Python 3.10+，不覆盖已有目录）：

```bash
git clone https://github.com/HaoYangJin/Research-workflow-Skill.git
cd Research-workflow-Skill
python scripts/install_skill.py --target ~/.claude/skills/research-mentor
```

Codex / ChatGPT Work 的插件导入与独立 Skill 路径见 [USAGE.md](USAGE.md)。宿主支持、账户权限与目录审核是各平台自己的机制；仓库发布不等于官方插件目录上架。

### 第一次运行

```text
使用 research-mentor，mixed 模式。
问题：时间序列发生漂移时，随机划分是否会低估未来预测误差？
资源：Python 标准库，合成数据，不调用付费 API。
输出：<一个空的项目目录>。请实际执行一个最小实验，写短稿、自审、修改，最后判断是否具备投稿条件。
```

不需要完整流程时，直接提供论文/草稿或指定阶段。单次提问不强制初始化项目。

手动检查项目：

```bash
python skills/research-mentor/scripts/workflow.py init ./my-study --title "Bounded question" --mode mixed
python skills/research-mentor/scripts/workflow.py template --phase 1
python skills/research-mentor/scripts/workflow.py status ./my-study
```

### 验证与复现

```bash
python -m unittest discover -s tests -v
python scripts/validate_repo.py
python scripts/build_release.py --output dist
```

真实试跑、已知限制与验收证据见 [验证报告](docs/validation-v1.0.0.md)。阶段 JSON 和证据格式见 [状态协议](skills/research-mentor/references/project-state.md)，扩展服务见 [能力适配](skills/research-mentor/references/tool-adapters.md)。

可直接重跑的 [合成时序研究示例](examples/drift-study/README.md) 包含冻结协议、代码和数学/时间隔离检查；发布文件见 [v1.0.0 Release](https://github.com/HaoYangJin/Research-workflow-Skill/releases/tag/v1.0.0)。

### 从 0.1.0 迁移

正式 Skill 源码移至 `skills/research-mentor/`。根 `SKILL.md` 保留兼容入口；旧的 `references/` 与示例已迁入正式 Skill。推荐备份旧安装后只复制正式 Skill 目录，或切换为插件，避免同时启用两份。0.1.0 没有状态格式，因此不存在旧项目状态的自动迁移。

## English

Research Workflow supports nine phases: scope/literature, hypotheses, design, data/reproducibility, results/ablations, drafting, self-review, revision/rebuttal, and submission readiness. Choose mentor, reviewer, or mixed mode; short requests do not require a project.

Install the Claude Code plugin using the two marketplace commands above, or run `claude --plugin-dir .` from a clone. Invoke `/research-workflow:research-mentor`. For a standalone skill, run `python scripts/install_skill.py --target <your-skill-directory>/research-mentor`. See [USAGE.md](USAGE.md) for Codex/ChatGPT Work and ZIP import details.

Python 3.10+ is required only for the local CLI. There are no runtime dependencies, credentials, bundled remote MCP servers, or paid model calls. Search, paper access, execution, and export depend on tools available in your host. Checkpoints track real files and evidence IDs; structural validation is not scientific validation or a publication guarantee. A completed assessment may correctly conclude `not_ready`.

Run the three validation/build commands above. The [validation report](docs/validation-v1.0.0.md) distinguishes observed checks from untested host behavior. See the [release notes](docs/RELEASE-v1.0.0.md) and [CHANGELOG](CHANGELOG.md).

## Structure

```text
.claude-plugin/        Claude plugin and marketplace manifests
.codex-plugin/         Codex plugin manifest
skills/research-mentor/ canonical skill, references, examples, and local CLI
scripts/               install, repository checks, deterministic release builder
tests/                 lifecycle and distribution regression tests
examples/              reproducible research demonstration
docs/                  release and validation evidence
.github/workflows/     CI and tagged release packaging
SKILL.md               legacy compatibility entry
```

## Contributing and license

Read [CONTRIBUTING.md](CONTRIBUTING.md). Keep the core domain-agnostic, preserve source integrity, and include real validation evidence when changing workflow behavior. MIT © 2026 JinhAo Yang; see [LICENSE](LICENSE).
