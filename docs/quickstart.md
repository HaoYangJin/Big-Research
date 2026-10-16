# 从一句任务到清晰行动

[中文介绍](../README.md) · [English](../README.en.md) · [完整安装说明](../USAGE.md)

```mermaid
flowchart LR
  A[安装插件] --> B[说出任务与材料]
  B --> C[自动判断模式]
  C --> D[简短行动卡]
  D --> E[执行并检查结果]
  E --> F[保存进度并继续]
```

## 1. 安装一次

按 README 的 Claude 或 Codex 两条安装命令操作，新会话中调用技能。无需再单独安装 Skill。

## 2. 直接说任务

```text
使用 research-mentor。我想用强化学习做储能调度。
已有：每小时负荷、电价、一个规则策略。
预算：CPU，一天内先判断是否值得继续。
请沿这个方向设计最小实验，先给三步操作。
```

你将看到模式提示和任务卡：

```text
① 导师 | ② 混合 | ③ 审稿 · 当前：导师（自动）
目标：在统一测试区间评估 RL 相对规则策略的收益。
行动：固定划分 → 跑两种策略 → 检查成本和约束违反。
验收：相同输入、预算与指标，保留所有运行结果。
下一步：提供数据字段和规则策略代码。
```

## 3. 按进度切换

| 你说 | 系统做 |
| --- | --- |
| “先导师模式，帮我跑通” | 保存导师偏好，指导具体操作 |
| “混合模式，改进并检查这个结果” | 共享行动表，兼顾推进和方法检查 |
| “审稿模式，检查这段方法” | 聚焦材料中的关键错误 |
| “严格审查并尝试复现整个流程” | 检查链路，请求缺失的具体复现材料 |
| “自动” | 恢复按任务与阶段自动选择 |

选择条在普通 Markdown 中只是文字；不用等待控件即可继续。

## 4. 保存并恢复

持续研究时指定一个空项目目录；AI 使用 CLI 保存。下次说“继续这个目录的项目”，先读取 status，再接续当前阶段。只问一个问题不创建目录。

```bash
python skills/research-mentor/scripts/workflow.py init /tmp/study --title "储能调度"
python skills/research-mentor/scripts/workflow.py mode /tmp/study --select auto --task revise
python skills/research-mentor/scripts/workflow.py status /tmp/study
```

旧项目升级、模式策略与回滚见 [状态协议](../skills/research-mentor/references/project-state.md)。异常退出后新版锁自动释放，无需删除锁文件。没有本地执行工具时，AI 在对话中给出记录并说明未持久化。

## 5. 不装插件也能看实验结果

按 [合成数据示例](../examples/drift-study/README.md) 重跑；它展示本地实验产物，不代表 AI 客户端的完整安装验收。
