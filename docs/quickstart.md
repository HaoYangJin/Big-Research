# 开始使用 / Get started

带来你的研究问题和已有材料即可。第一次可输入：

> 我是刚入门的研究者，正在探索……。我手里有……，希望先完成……。请解释必要概念，并帮助我做出一个具体成果。

For a concise experience: “Use concise guidance. My question is …, my materials are …, and I need …”. Guided and concise explanations share the same evidence standards.

## 安装 / Installation

以下步骤可以直接照做，无需先克隆本仓库。Codex CLI 的 `codex ...` 命令在系统终端运行；Claude Code 的 `/plugin ...` 命令在 Claude Code 对话中运行。

### 1. 准备终端与工具

Windows 用户打开 PowerShell；macOS 和 Linux 用户打开终端。完整本地体验需要 uv 和 Python 3.11+，uv 可以管理 Python。先按 [uv 官方安装说明](https://docs.astral.sh/uv/getting-started/installation/) 配置 uv，然后在终端检查：

```shell
uv --version
codex --version
codex plugin marketplace --help
codex plugin add --help
```

前两条应显示版本号，后两条必须分别显示插件来源管理和插件安装的帮助。仅能运行 `codex --version` 不能证明它支持插件。使用 Claude Code 的研究者只需检查 uv，并准备好可用的 Claude Code。

如果找不到 `codex`，请按 [Codex CLI 官方安装说明](https://learn.chatgpt.com/docs/codex/cli)安装命令行工具。若已有 Node.js 和 npm，也可以在终端安装：

```shell
npm install -g @openai/codex@latest
codex --version
```

如果 Codex CLI 是通过 npm 安装的，上面同一条 `npm install` 命令也用于更新 **Codex CLI 程序**。其他安装方式请按对应的官方说明更新。如果插件命令不受支持，先按下方的 [Windows 排查](#codex-windows)确认实际调用的是哪一份程序；已有兼容版本时无需重复安装。

### 2. 安装 Big Research

Big Research 是独立第三方插件，安装标识为 `big-research`。

**Codex CLI：在系统终端逐条执行。**

```shell
codex plugin marketplace add HaoYangJin/Big-Research
codex plugin add big-research@big-research-marketplace
codex plugin list --marketplace big-research-marketplace
```

第一条添加插件来源，第二条安装本插件，第三条检查结果。输出中应出现 `big-research`、`installed, enabled` 和版本号。

**Claude Code：在 Claude Code 对话输入框中逐条执行。**

```text
/plugin marketplace add HaoYangJin/Big-Research
/plugin install big-research@big-research-marketplace
```

安装完成后，可在同一对话输入 `/plugin`，查看 Installed 中是否已有 Big Research。

### 3. 开启新会话并开始使用

日常使用从 `big-research` 开始即可，它会根据任务按需组合设置、检索、设计、分析、写作和评议能力。

**Codex 用户**在终端运行 `codex`，按提示完成首次登录，再在 **Codex 对话输入框**发送：

```text
$big-research
我刚开始研究这个问题。请帮我梳理已有材料，比较可行方向，并给出下一步。
```

**Claude Code 用户**开启新会话，在对话输入框发送：

```text
/big-research:big-research
我刚开始研究这个问题。请帮我梳理已有材料，比较可行方向，并给出下一步。
```

Claude Code 的插件 Skill 使用 `/插件名:Skill名` 格式。这里插件名和研究入口都叫 `big-research`，所以形成 `/big-research:big-research`；这是一个完整命令，整条发送一次即可。[官方命名说明](https://code.claude.com/docs/en/skills#choose-where-skills-load)

**什么时候用首次设置，什么时候用研究入口？**

| 用途 | Codex 对话中输入 | Claude Code 对话中输入 |
| --- | --- | --- |
| 开始、推进或继续研究（默认入口） | `$big-research` | `/big-research:big-research` |
| 首次设置、检查环境、调整研究保存位置（可选） | `$big-research-setup` | `/big-research:big-research-setup` |

`big-research-setup` 专门帮助确认本地运行条件、研究目录和首个项目。需要设置或排查环境时单独调用；平时直接使用 `big-research`，无需按固定顺序把两个入口都运行一遍。

**Codex 桌面应用用户**：用同一系统账户的 Codex CLI 完成上述安装后，完全退出并重新打开桌面应用，在插件页检查 Big Research 的安装与启用状态，再新建对话使用。若设置过自定义 `CODEX_HOME`，请确保 CLI 和桌面应用使用同一配置目录。桌面应用与 CLI 的具体支持情况见[兼容性说明](compatibility.md)。

首次设置会帮助你确认研究目标、已有材料、保存位置和可用工具。首次启用本地工具时，uv 可能下载锁定的依赖；模型推理和检索使用当前客户端已授权的能力。已验证的客户端版本和界面支持情况见[兼容性说明](compatibility.md)。

### 4. 更新 Big Research

**Codex CLI：在系统终端刷新来源，再安装当前版本并检查。**

```shell
codex plugin marketplace upgrade big-research-marketplace
codex plugin add big-research@big-research-marketplace
codex plugin list --marketplace big-research-marketplace
```

**Claude Code：以下更新命令也在系统终端运行。**

```shell
claude plugin marketplace update big-research-marketplace
claude plugin update big-research@big-research-marketplace
claude plugin list
```

更新完成后重新开启客户端会话，使新版本生效。旧版研究数据需要按下方的[迁移说明](#迁移已有项目)导入；更新插件不会自动转换已有项目。

如果 Codex 对话中仍找不到 `$big-research`，先在终端重新运行上面的 `plugin list` 检查安装与启用状态，再开启新会话。首次设置提示 uv 不可用时，重新打开终端并检查 `uv --version`。

命令依据：[Codex 插件命令参考](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli)、[Claude Code 插件管理](https://code.claude.com/docs/en/discover-plugins)。英文说明见[English README](../README.en.md#install-latest)。正式发行包统一从 [Latest](https://github.com/HaoYangJin/Big-Research/releases/latest) 获取。

<a id="codex-windows"></a>

## Windows：命令不支持或配置读取失败

若安装时报 `unexpected argument marketplace`、`unrecognized subcommand add`，或启动时报 `unknown variant default ... service_tier`，先在 PowerShell 检查：

```powershell
Get-Command codex -All | Select-Object CommandType, Source
codex --version
```

Windows 可以同时存在 npm 安装的 `codex.ps1` / `codex.cmd` 和桌面应用附带的 `codex.exe`。终端按命令查找顺序选择程序，不会自动选择版本较新的那份。桌面应用可用不代表终端调用的是同一个版本。

已确认 CLI 0.120.0 没有本指南使用的插件命令；CLI 0.163.0 的隔离安装检查通过。以实际命令帮助为准，不把尚未验证的版本当作兼容保证。

**已有桌面应用附带的兼容 `codex.exe` 时**，可以显式使用它。先检查版本和帮助：

```powershell
$codex = (Get-Command codex.exe -ErrorAction Stop).Source
& $codex --version
& $codex plugin marketplace --help
& $codex plugin add --help
```

确认显示对应帮助后，保持在同一个 PowerShell 窗口执行：

```powershell
& $codex plugin marketplace add HaoYangJin/Big-Research
& $codex plugin add big-research@big-research-marketplace
& $codex
```

以后在这个窗口也用 `& $codex` 启动。这个变量只影响当前 PowerShell 会话，不修改 PATH、配置或已安装的软件。如果找不到 `codex.exe`，或选中的程序仍不支持插件命令，按前面的官方安装说明选择兼容 CLI，再重新检查；不要继续执行安装命令。

`service_tier = "default"` 的上述错误也可能来自旧 CLI 无法解析同一份新版配置。若选定的新版本能够正常读取配置，保留原设置即可；无需为安装插件切换服务档位。

## 从旧安装迁移

如果你安装过改名前的插件，先保留原来的研究目录，再按上面的命令安装 `big-research@big-research-marketplace`。新安装不会搬动或删除已有项目。需要继续旧项目时，在客户端 MCP 环境配置 `BIG_RESEARCH_HOME` 指向原来的保存目录；新项目默认保存在 `~/Big-Research`。确认项目可访问后，可以在客户端插件管理页卸载旧插件，避免重复入口。

## 选择保存位置 / Research home

MCP 默认在 `~/Big-Research` 下保存项目，项目名例如 `my-study`。在客户端的 MCP 环境配置 `BIG_RESEARCH_HOME` 可以更改这个目录。工具只能访问该目录下明确命名的项目。需要使用其他位置的项目，可以通过 CLI 指定路径，或自行更改研究目录设置。

只问一个问题无需建立项目。持续研究可以要求：“创建一个项目，保存我的材料、研究地图和重要决定。” 交互界面由 MCP Apps 支持情况决定；没有界面也可正常处理任务。

## 本地 CLI / Shared CLI

从仓库目录运行：

```text
uv run --frozen big-research doctor
uv run --frozen big-research start PATH_TO_NEW_STUDY --title "My question" --field "History" --paradigm "Interpretive" --method interpretive
uv run --frozen big-research status PATH_TO_STUDY
uv run --frozen big-research export PATH_TO_STUDY
```

`PATH_TO_*` 是你选择的实际路径，不要原样复制占位符。导出的 HTML 可以筛选和浏览；更改记录请回到对话或 CLI。导出不会覆盖已有文件。详细 JSON 输入见[操作参考](../skills/big-research/references/workspace.md)。

## 迁移已有项目

```text
uv run --frozen big-research migrate PATH_TO_V1_PROJECT PATH_TO_NEW_V2_PROJECT
```

支持已知的 v1.0.0/v1.1.0 数据。目标目录必须不存在；源项目不被修改。工具核对文件完整性、复制材料并导入证据；旧完成状态和投稿判断不会直接视为新版已通过。请在迁移后选择方法、检查导入记录，再继续研究。未知或损坏数据停止迁移，不运行旧执行器。

## 你始终掌握决定 / Your judgment remains central

AI 可以推进已授权的日常工作。研究方向、重大方法变化、伦理取舍和最终结论由你决定。评议会区分实际问题、材料缺失和解释分歧；没有证据时不会把结论写成已经成立。
