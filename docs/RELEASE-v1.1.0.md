# Research Workflow v1.1.0

本版围绕可恢复进度、自动模式与清晰指导改进。仓库 URL 和插件标识保持兼容。

| v1.0.0 报告项 | 本版处理 |
| --- | --- |
| §1 强制退出留下锁 | 改用 OS advisory lock，进程退出释放；保留含 PID/机器/时间的锁文件 |
| §2 模式未同步项目 | mode 命令、auto/manual 策略、切换历史、阶段自动路由 |
| §4 同名 Skill 重复发现 | 移除根 SKILL.md，保留正式 skills 入口和迁移文档 |
| §7 版本升级和包内指南 | migrate 验证/备份/升级；插件 ZIP 增加指南与示例 |

三档模式不再依赖用户主动输入：AI 依据当前意图、项目偏好与阶段选择。平台有选择工具时可展示三选一，否则显示文本条；没有伪装成原生 UI。默认简短任务卡，明确输入、操作、产出和验收；仅凭有证据的关键错误提出阻断。严格审查按用户要求覆盖全流程，缺复现材料时具体询问。

README 新增中英文独立入口、使用流程 SVG、Mermaid 教程与在线 Star History 图。保留 skills 作为插件实现，避免不必要的更名迁移。

## 升级

更新插件；独立 Skill 用户备份后重装，避免同时启用两份。旧项目停止所有写入后：

```bash
python skills/research-mentor/scripts/workflow.py migrate /path/to/project
```

验证通过后保存 project.v1.0.0.backup.json，模式继承为 manual。回滚说明见 [状态协议](../skills/research-mentor/references/project-state.md)。不要删除新版锁文件，也不要与旧 CLI 同时写入。

## 验证与边界

见 [验证记录](validation-v1.1.0.md)。科研语义认证、跨领域效果评估、工具自动适配和跨机器共享写入仍未实现。文本交互规则需要真实客户端行为验收；结构测试不能证明 AI 永远遵循提示词。Release 不等于官方插件目录收录。

## 发布过程更正

本次发布过程中，原流水线在 Windows CI 完成前生成过初始下载包。随后发现 Windows 缓冲文件偏移导致锁操作失败，已改为无缓冲、非追加文件句柄，并增加发布前 Linux/Windows × Python 3.10/3.12 的全部测试门槛。本次 v1.1.0 标签和包在检查全部成功后更正；早于更正下载的副本请重新下载并核对 SHA256SUMS。v1.0.0 和其他历史发布保持原样。
