> 本项目旨在利用 AI 工具辅助人类科学家进行科学研究，而非一个 AI 科学家项目。人类科学家的科研品味以及伦理道德是科研过程中不可替代的东西。希望各位研究者为全人类的理想奋斗，一起突破未知边界。

# Big Research

**人类主导的 AI 辅助科研工作台。把想法变成可以推进、检查和持续完善的研究。**

独立第三方开源插件，支持 Codex 和 Claude Code，与 OpenAI 官方插件无隶属或认证关系。

[English](README.en.md) · [开始使用](docs/quickstart.md) · [研究方法与评议](docs/methods.md) · [参与贡献](CONTRIBUTING.md)

![Version](https://img.shields.io/badge/version-2.1.1-355b48) ![License](https://img.shields.io/badge/license-MIT-355b48)

你不必先掌握一套复杂命令。带来一个想法、一组材料、一份草稿，或者一个卡住的问题，说明你希望完成什么，Big Research 会帮助你找到下一步。

## 从你所在的位置开始

| 你想做什么 | 一起完成什么 |
| --- | --- |
| “这个想法值得研究吗？” | 梳理问题、已有工作、竞争解释与可行路径 |
| “我不知道该选什么方法。” | 根据问题和研究范式比较方法、资源与限制 |
| “请帮我推进这项研究。” | 开展已授权的分析，保留材料、过程和实际结果 |
| “这份稿件哪里还需要改进？” | 找到有依据的问题，形成修改与复核计划 |
| “继续上次的项目。” | 恢复研究地图、证据和待决定事项 |

## 为不同的研究方式留出空间

问题、方法和判断属于研究者。通用框架连接研究问题、资料、分析和论断，方法模块负责提供适用的检查：定量与实验、质性研究、解释与人文研究、形式化与理论、文献综合、混合方法。

你可以从已有材料进入，调整路线、并行探索，也可以回到早先的选择。一个阴性结果、一条未能成立的推导或尚有分歧的解释，都值得如实保存。

## 安装最新版本

完整本地体验需要 [uv](https://docs.astral.sh/uv/getting-started/installation/) 和 Python 3.11+，uv 可以管理 Python。无需为本插件配置模型 API 密钥；AI 与检索使用你当前客户端的能力。

### Claude Code

在 **Claude Code 的对话输入框**中依次执行：

```text
/plugin marketplace add HaoYangJin/Big-Research
/plugin install big-research@big-research-marketplace
```

开启新会话，发送以下内容开始研究：

```text
/big-research:big-research
我刚开始研究这个问题。请帮我梳理已有材料，比较可行方向，并给出下一步。
```

### Codex CLI

先运行 `codex plugin marketplace --help` 和 `codex plugin add --help`，确认两条都显示对应命令的帮助。Codex CLI 0.120.0 不支持这组命令；若出现命令不识别或 `service_tier` 配置错误，请先按[Windows 多版本排查](docs/quickstart.md#codex-windows)选择支持插件的 Codex。

在 **系统终端**（如 Windows PowerShell）依次执行：

```shell
codex plugin marketplace add HaoYangJin/Big-Research
codex plugin add big-research@big-research-marketplace
codex
```

进入新的 **Codex 对话**后发送：

```text
$big-research
我刚开始研究这个问题。请帮我梳理已有材料，比较可行方向，并给出下一步。
```

环境准备、安装验证、桌面应用和更新指令见[快速上手](docs/quickstart.md)。首次设置与日常入口的区别见[开始使用](docs/quickstart.md#3-开启新会话并开始使用)。正式发行包统一从 [Latest](https://github.com/HaoYangJin/Big-Research/releases/latest) 获取。

## 一份看得见来路的研究

研究地图连接任务与依赖；论据浏览器连接论断与材料；方案比较帮助你做选择；决定与修订面板保留重要判断及修改过程。支持 MCP Apps 的客户端提供交互视图，其他环境仍可使用文本、表格和本地快照。

评议结合通用研究质量、方法要求与可选的期刊或会议标准。ICLR、NeurIPS、APA JARS、健康研究报告规范和人文评议各有适用范围。没有统一量表的领域，也能获得明确标准、证据位置、理由和修改建议。[了解评议方式](docs/methods.md)

本项目不替代研究者、伦理审查或正式同行评审。记录完整性检查不认证科学结论；没有经过校准的跨学科总分，也不预测录用概率。

## 一起完善它

欢迎贡献方法模块、翻译和使用反馈。我们尤其希望听到：哪个科研环节没有被好好支持，哪些检查不适合你的研究传统。[贡献指南](CONTRIBUTING.md) · [问题反馈](https://github.com/HaoYangJin/Big-Research/issues)

已有项目可以按[数据导入说明](docs/quickstart.md#迁移已有项目)继续使用。

[参考与致谢](docs/research-basis.md) · [MIT](LICENSE)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=HaoYangJin/Big-Research&type=Date)](https://www.star-history.com/#HaoYangJin/Big-Research&Date)
