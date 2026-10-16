# Installation and usage / 安装与使用

第一次使用？先看 [逐步上手指南](docs/getting-started.md)，按“跑示例 → 安装 → 发起任务 → 查看产物 → 恢复项目”操作。本页保留安装方式、CLI 与发布包的参考说明。

## 中文

### 1. 选择安装方式

同一宿主优先只启用一种方式，避免两份技能重复触发。

| 使用环境 | 安装方式 | 调用 |
| --- | --- | --- |
| Claude Code | 下方 marketplace 命令，或 `claude --plugin-dir .` | `/research-workflow:research-mentor` |
| Claude Code 独立 Skill | 复制 `skills/research-mentor/` 到宿主 skills 目录 | 自然语言或 `/research-mentor` |
| Claude.ai 自定义 Skill | 上传 Release 中 `research-mentor-1.0.0.zip` 并启用 | 自然语言指定 `research-mentor` |
| Codex CLI 插件 | `codex plugin marketplace add` 后 `codex plugin add`，详见下方命令 | 新会话指定 `$research-mentor` |
| ChatGPT Work 桌面本地插件 | 注册本地 marketplace，在桌面 Plugins 来源中安装；界面链路待实测 | 从 `@` 菜单选择 Research Workflow |
| ChatGPT Work 网页工作区插件 | 管理员 Admin → Plugins → Add → Import marketplace；真实导入待验收 | 安装后从 `@` 菜单选择插件 |
| 其他 Agent Skills 宿主 | 仅安装 `skills/research-mentor/` | 按宿主方式触发 |

**Codex CLI 快速安装**（原生 0.163.0 已实测，终端执行）：

```bash
codex plugin marketplace add HaoYangJin/Research-workflow-Skill --ref v1.0.0
codex plugin add research-workflow@research-workflow-marketplace
codex plugin list --marketplace research-workflow-marketplace --json
```

安装后开启新会话。ChatGPT Work 桌面、网页管理员导入、权限和失败分支见 [Codex / ChatGPT Work 安装指南](docs/openai-install.md)，不要把本机 Skill 复制当作云端安装。

Claude Code：

```text
/plugin marketplace add HaoYangJin/Research-workflow-Skill
/plugin install research-workflow@research-workflow-marketplace
```

独立安装脚本支持 Linux、macOS、Windows 的 Python 3.10+，必须指定精确目标目录：

```bash
python scripts/install_skill.py --target ~/.claude/skills/research-mentor
```

对于使用 `~/.agents/skills/` 目录的 Codex 配置：

```bash
python scripts/install_skill.py --target ~/.agents/skills/research-mentor
```

Windows PowerShell 示例：

```powershell
python scripts/install_skill.py --target "$HOME\.claude\skills\research-mentor"
```

目标已存在时脚本拒绝覆盖。更新前审阅、备份旧目录，再安装新版本。不要直接把 `.git`、研究数据和本地会话日志当作 Skill 打包。

ChatGPT Work / Codex 各入口的可用性受产品与账户影响。此仓库提供 `.codex-plugin/plugin.json` 和 Claude 兼容 marketplace；未承诺已经通过平台公开目录审核。独立 Skill 是支持本地技能目录的宿主的备用路径，不会自动注册云端插件。

### 2. 模式与阶段

先按需求选择：[导师模式：收敛问题与设计下一步](docs/conversation-examples.md#1-导师模式把兴趣变成可以执行的问题) · [审稿模式：检查已有材料](docs/conversation-examples.md#2-审稿模式检查已有实验不替缺失证据背书) · [混合模式：推进并自审](docs/conversation-examples.md#3-混合模式推进实验同时保留推翻结论的检查)。示例采用“用户：…；AI：…”多轮对话，标明预期行为与实际执行的区别。

```text
导师模式：帮我把这个兴趣收敛为一个能验证的研究问题。
审稿模式：审查下面的实验设计，区分确认的问题与缺少的信息。
混合模式：先给行动建议，再指出最可能推翻结论的证据缺口。
```

明确的模式优先；引用中的 reviewer 不会自动切模式。`literature review` 仍可在导师模式中完成。阶段可从中间进入，不要求先完成九阶段。

### 3. 实际研究项目

提供问题、材料、预算和一个空输出目录。Skill 会先读取现有状态，按需调用宿主工具，并产出真实文件。也可手动使用 CLI：

```bash
python skills/research-mentor/scripts/workflow.py init ./my-study --title "Research question" --mode mixed
python skills/research-mentor/scripts/workflow.py template --phase 1
python skills/research-mentor/scripts/workflow.py checkpoint ./my-study --phase 1 --artifact artifacts/01-scope.json
python skills/research-mentor/scripts/workflow.py validate ./my-study
```

`template` 只向终端打印模板，不创建或填写研究结论；先保存并填写，再运行 `checkpoint`。完整格式见 [项目状态协议](skills/research-mentor/references/project-state.md)。

- `done`：阶段产物已生成并通过结构检查。
- `blocked`：缺数据/计算/来源，留在当前阶段并说明原因。
- `skipped`：明确不在任务范围内，记录原因后继续。
- `reopen`：修改上游时清除该阶段及下游检查点，保留文件待复核。
- `not_ready`：已完成投稿条件判断，但研究还未达到要求。

`valid: true` 只检查结构、证据关联和文件哈希。AI/研究者仍须判断来源是否支持结论、实验是否公平、统计是否正确。脚本既不自动打开文献，也不执行台账中记录的命令。

### 4. 插件化与权限

一个插件封装一个主技能、九阶段按需参考、状态 CLI 和能力适配协议。搜索、论文读取、实验执行、Git、文档导出可使用宿主已有的插件或工具；没有这些服务时明确记录限制。核心没有网络副作用、自动 hooks、后台进程或固定 MCP 端点。不要把“已写适配协议”解释为“所有第三方服务已集成并通过认证”。

### 5. 构建与校验

```bash
python -m unittest discover -s tests -v
python scripts/validate_repo.py
python scripts/build_release.py --output dist
claude plugin validate .claude-plugin/plugin.json --strict
claude plugin validate .claude-plugin/marketplace.json --strict
```

发布包：

- `research-mentor-1.0.0.zip`：顶层 `research-mentor/`，可作独立 Skill。
- `research-workflow-1.0.0.zip`：插件根目录直接包含清单与 `skills/`，不含研究数据、凭据或 Git 元数据。
- `SHA256SUMS.txt`：校验和。

## English

Choose one install route per host: Claude marketplace plugin, standalone `skills/research-mentor/`, or the corresponding release ZIP. Claude plugin invocation is `/research-workflow:research-mentor`. Use the commands and destination examples above; the installer refuses existing destinations. Product-specific plugin import availability depends on the host/account. See the current official documentation linked below rather than assuming directory publication or an unverified command.

For a research project, provide the question, available artifacts, constraints, budget, and an empty output directory. The local CLI uses Python 3.10+ without dependencies. It supports `init`, `template`, `status`, `checkpoint`, `validate`, and `reopen`. Fill printed templates with real evidence before checkpointing. Resume from `project.json` and `evidence.json`; reopening invalidates downstream checkpoints. A blocked run is not a successful experiment, and a completed readiness assessment may be `not_ready`.

The plugin packages instructions, phase modules, capability handoffs, and a local state CLI. It has no remote MCP server, credentials, automatic hooks, or background process. Tool availability and permissions belong to the host. Structure/hash validation does not prove execution, entailment, scientific correctness, or publication readiness.

## Official format references / 官方格式依据

Checked on 2026-10-16; host behavior may change.

- [Claude Code plugins](https://code.claude.com/docs/en/plugins)
- [Claude manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference)
- [Claude marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [OpenAI plugin packaging and submission](https://developers.openai.com/plugins/deploy/submission)
- [OpenAI local plugin and marketplace packaging](https://developers.openai.com/plugins/build/plugins)
- [Codex plugin browser](https://learn.chatgpt.com/docs/plugins)
- [ChatGPT workspace marketplace import](https://learn.chatgpt.com/docs/enterprise/plugin-management)
- [ChatGPT Work plugin development](https://learn.chatgpt.com/docs/build-plugins)
- [Skills documentation](https://learn.chatgpt.com/docs/build-skills)
