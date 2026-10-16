# 仓库整理依据

v1.1.0 保留仓库 URL 和已发布插件标识；展示名统一为 Research Workflow。Skill 是插件的行为实现，删除 skills 会让插件失去核心功能。删除的只是根目录重复兼容入口；迁移说明转为普通文档。

参考来源（2026-10-16 阅读）：

| 仓库 | 采用的组织思路 |
| --- | --- |
| [Anthropic 官方插件目录](https://github.com/anthropics/claude-plugins-official) | 插件清单、skills 与文档分工，稳定插件标识 |
| [Superpowers](https://github.com/obra/superpowers) | 清晰安装入口，技能与支持文件集中组织 |
| [Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 科研技能按主题组织，明确能力范围 |
| [Star History](https://github.com/star-history/star-history) | README 使用在线历史星标图 |

未复制第三方实现；没有宣称已被这些目录收录。没有添加与本项目无关的 agents、MCP 服务或空目录。README 保留最短安装路径，完整教程独立，多语言通过独立 README 跳转。插件 ZIP 包含文档；独立 Skill ZIP 只携带运行所需文件。
