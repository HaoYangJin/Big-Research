# Codex / ChatGPT Work 插件快速安装

核对日期：2026-10-16。插件名为 `research-workflow`，显示名为 **Research Workflow**，技能名为 `research-mentor`，marketplace 名为 `research-workflow-marketplace`。

## 1. Codex CLI：两条命令安装

前提：已安装并配置支持 `codex plugin` 的 Codex CLI。本次实际验证版本为 **0.163.0**，不代表已确定最低兼容版本。

在系统终端依次执行：

```bash
codex plugin marketplace add HaoYangJin/Research-workflow-Skill --ref v1.0.0
codex plugin add research-workflow@research-workflow-marketplace
```

第一条注册插件来源，第二条才安装插件。`--ref v1.0.0` 固定正式版；希望跟随开发分支时，可将该值改为 `main`。

检查安装结果：

```bash
codex plugin list --marketplace research-workflow-marketplace --json
```

应在 `installed` 中看到 `name: research-workflow`、`version: 1.0.0`、`enabled: true`。随后**开启新的 Codex 会话**，输入：

```text
使用 $research-mentor，导师模式。请帮我把“智能体长期记忆”收敛成一个低成本可检验的问题。
先说明你可用的检索、执行与写文件能力；本轮不运行实验。
```

也可以先运行 `codex`，在其交互界面输入 `/plugins`，切换到本 marketplace 并安装。若 `plugin add` 不被识别，先用 `codex plugin --help` 确认本机版本支持的命令，再参考官方插件浏览器入口。

**验证范围**：本次从公开 GitHub 仓库的 `v1.0.0` 标签实际执行 marketplace add、plugin add、plugin list，得到 1.0.0 / installed / enabled。未发起模型请求，没有把“安装成功”当作“科研任务已执行”。验证后移除了本次测试新增的插件和来源。

命令的官方依据：[marketplace 注册与版本固定](https://developers.openai.com/plugins/build/plugins)、[Codex 插件浏览器及新会话要求](https://learn.chatgpt.com/docs/plugins)；`plugin add` 的具体语法由 0.163.0 原生 `--help` 与上述安装实测共同确认。

## 2. ChatGPT Work 桌面端：选择本地 marketplace

这条路径用于读取本机 marketplace 的桌面环境，与云端工作区导入分开。

1. 在同一操作系统用户下，先执行第 1 节的 `codex plugin marketplace add` 注册来源。
2. 重启 ChatGPT 桌面应用，打开 **Plugins**，在来源选择中寻找 `research-workflow-marketplace`。如果已经安装，查看 Installed；否则打开 **Research Workflow** 并安装。
3. 开启新的 **Work** 对话，在输入框键入 `@`，从菜单选择 **Research Workflow**，再发送任务。
4. 先做一个不需要执行代码的单次任务，再验证文件写入、代码执行和状态恢复是否在该环境可用。

本仓库使用官方支持的 `.claude-plugin/marketplace.json` 兼容目录格式，同时提供 `.codex-plugin/plugin.json`。本地目录的发现、安装缓存和云端插件可用性需要分别验收。若桌面应用没有显示该本地来源，不要据此宣称 Work 已安装成功，也不要假设本机目录已同步到网页版。

本节操作依据：[本地 marketplace 与桌面插件目录](https://developers.openai.com/plugins/build/plugins)、[在 Work 中选择已安装插件](https://learn.chatgpt.com/docs/build-plugins)。**本仓库尚未完成该桌面界面的端到端实测。**

## 3. ChatGPT Work 网页版：工作区管理员从 GitHub 导入

需要工作区管理员权限和可访问本仓库的 GitHub 连接。按照官方工作区导入入口：

1. 打开 **Admin → Plugins → Add → Import marketplace**。
2. 填写以下值，然后执行导入并按提示授权 GitHub 访问。

| 字段 | 填写内容 |
| --- | --- |
| Source | `https://github.com/HaoYangJin/Research-workflow-Skill` |
| Path | 留空，marketplace 位于仓库根目录 |
| Branch, tag, or commit | `v1.0.0`，或选择 `main` 接收后续更新 |

3. 查看导入报告，为目标用户或角色配置安装策略。
4. 用户打开 Plugins 的工作区来源，安装 **Research Workflow**；新建 Work 对话，用 `@` 从菜单选择该插件后发送任务。

官方支持导入本仓库采用的 Claude-compatible marketplace 和 Codex manifest，但这只是格式与入口依据。**本仓库尚未完成真实工作区导入验收**；以实际导入报告为准。参见 [工作区导入与同步](https://learn.chatgpt.com/docs/enterprise/plugin-management)。

没有 Admin 入口的个人账户不能直接照用这条管理员流程。此项目没有提供可承诺适用于所有账户的“粘贴仓库 URL 即安装”按钮。向普通对话上传 ZIP、粘贴 GitHub URL，或在电脑上复制 Skill，都不等于已在云端 Work 注册插件。公共目录发布需要独立的上传、审核与发布流程，见 [官方发布说明](https://developers.openai.com/plugins/deploy/submission)。

## 4. 只想先在 Codex 使用：独立 Skill 备用方式

如果插件入口不可用，但你的 Codex 配置读取 `~/.agents/skills/`，可以使用仓库已有安装器：

```bash
git clone --branch v1.0.0 https://github.com/HaoYangJin/Research-workflow-Skill.git
cd Research-workflow-Skill
python scripts/install_skill.py --target ~/.agents/skills/research-mentor
```

开启新会话后指定 `$research-mentor`。这会安装 Skill 文件，不会注册完整插件，也不会使网页版 Work 自动获得该技能。目标已存在时安装器拒绝覆盖；同一宿主避免同时启用插件与重复的独立 Skill。

三种模式的具体用法见 [用户 / AI 对话示例](conversation-examples.md)，首次运行与恢复见 [上手指南](getting-started.md)。
