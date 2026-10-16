# 开始使用 / Get started

带来你的研究问题和已有材料即可。第一次可输入：

> 我是刚入门的研究者，正在探索……。我手里有……，希望先完成……。请解释必要概念，并帮助我做出一个具体成果。

For a concise experience: “Use concise guidance. My question is …, my materials are …, and I need …”. Guided and concise explanations share the same evidence standards.

## 安装 / Installation

完整本地体验需要 uv，及其管理的 Python 3.11+。先按 [uv 官方安装说明](https://docs.astral.sh/uv/getting-started/installation/)配置 uv。首次启动可能下载锁定的依赖；本地 MCP 不上传研究材料，也不包含检索服务或模型账户。

Claude Code 的安装命令见首页。Codex CLI：

```text
codex plugin marketplace add HaoYangJin/Research-workflow-Skill
codex plugin add research-workflow@research-workflow-marketplace
```

新会话输入 `$research-setup` 或 `$research-workflow`。安装方式随客户端版本变化，发布验收状态见[兼容性说明](compatibility.md)。不要同时启用另行复制的历史 research-mentor Skill。

The repository marketplace exposes one current plugin. Official release packages are available from [Latest](https://github.com/HaoYangJin/Research-workflow-Skill/releases/latest). Development branches are for testing, not an alternate user version selector.

## 选择保存位置 / Research home

MCP 默认在 `~/Research-Workflow` 下保存项目，项目名例如 `my-study`。在客户端的 MCP 环境配置 `RESEARCH_WORKFLOW_HOME` 可以更改这个目录。工具只能访问该目录下明确命名的项目。需要使用其他位置的项目，可以通过 CLI 指定路径，或自行更改研究目录设置。

只问一个问题无需建立项目。持续研究可以要求：“创建一个项目，保存我的材料、研究地图和重要决定。” 交互界面由 MCP Apps 支持情况决定；没有界面也可正常处理任务。

## 本地 CLI / Shared CLI

从仓库目录运行：

```text
uv run --frozen research-workflow doctor
uv run --frozen research-workflow start PATH_TO_NEW_STUDY --title "My question" --field "History" --paradigm "Interpretive" --method interpretive
uv run --frozen research-workflow status PATH_TO_STUDY
uv run --frozen research-workflow export PATH_TO_STUDY
```

`PATH_TO_*` 是你选择的实际路径，不要原样复制占位符。导出的 HTML 可以筛选和浏览；更改记录请回到对话或 CLI。导出不会覆盖已有文件。详细 JSON 输入见[操作参考](../skills/research-workflow/references/workspace.md)。

## 迁移已有项目

```text
uv run --frozen research-workflow migrate PATH_TO_V1_PROJECT PATH_TO_NEW_V2_PROJECT
```

支持已知的 v1.0.0/v1.1.0 数据。目标目录必须不存在；源项目不被修改。工具核对文件完整性、复制材料并导入证据；旧完成状态和投稿判断不会直接视为新版已通过。请在迁移后选择方法、检查导入记录，再继续研究。未知或损坏数据停止迁移，不运行旧执行器。

## 你始终掌握决定 / Your judgment remains central

AI 可以推进已授权的日常工作。研究方向、重大方法变化、伦理取舍和最终结论由你决定。评议会区分实际问题、材料缺失和解释分歧；没有证据时不会把结论写成已经成立。
