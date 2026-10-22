# Big-Research 的项目故事

[返回首页](../README.md) · [English](project-story.en.md) · [开始使用](quickstart.md)

<!-- big-repo:showcase:start -->
## 从研究阶段到可以继续的研究

Big-Research 关心的不只是一次对话能给出什么答案，还关心下一次回来时，研究者能不能看懂工作走到了哪里：用了哪些材料、做过哪些尝试、为什么改变方法，还有什么问题没有解决。

早期的 Research Workflow 以导师、审稿和混合模式组织科研阶段。v1.0.0 的实现已经保存进度、关联证据，并提供可恢复检查点。v1.1.0 继续改进恢复过程和对话引导。到 v2.1.0，组织方式转向研究工作台：任务与依赖、论断与材料、候选方案、决定和修订可以分别检查，也可以联系起来看。

这段演进可以在[早期实现](https://github.com/HaoYangJin/Big-Research/commit/6bda93f)、[检查点改进](https://github.com/HaoYangJin/Big-Research/commit/2cebfe6)和[工作台实现](https://github.com/HaoYangJin/Big-Research/commit/6a96ec3)中追溯。它描述的是软件如何变化，不是科研成效的评测。

## 三个贯穿当前设计的选择

### 把研究判断留给研究者

项目首页明确把自身定位为辅助人类科学家的工具。研究问题、方法上的重大变化、伦理取舍与最终结论仍由研究者决定。保存一条论断的来源，可以帮助检查它；文件齐全或流程完成，并不能证明论断成立。

### 让方法跟着问题走

定量实验、质性研究、解释与人文研究、形式化推导、文献综合和混合方法，需要不同的材料与判断标准。当前实现提供可组合的方法模块，并将报告完整性与科学判断区分开。比较解释、保留阴性结果、回到早先的选择，都应该有位置。[方法与评议说明](methods.md)介绍了这些边界。

### 留下能接着工作的记录

研究地图、证据浏览、方案比较和决定与修订面板，是同一项目的不同入口。支持 MCP Apps 的客户端可以提供交互视图；其他环境使用文本、表格或本地只读快照。它们帮助研究者检查已有工作，再决定下一步。具体支持情况见[兼容性说明](compatibility.md)。

## 有记录可查的里程碑

下表使用 GitHub Release 的 UTC 发布日期，避免与本地提交日期混用。早期版本沿用当时的 Research Workflow 名称；安装请始终以[当前指南](quickstart.md)为准。

| 发布日期（UTC） | 版本 | 这一步带来的变化 |
| --- | --- | --- |
| 2026-05-16 | [v0.1.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v.0.1.0) | Research Workflow Skill 的早期发布 |
| 2026-10-16 | [v1.0.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v1.0.0) | 插件化研究阶段、证据关联与可恢复检查点 |
| 2026-10-16 | [v1.1.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v1.1.0) | 改进检查点恢复、模式选择与研究引导 |
| 2026-10-17 | [v2.1.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v2.1.0) | 转向人类主导的研究工作台，加入方法模块与评议视图 |
| 2026-10-17 | [v2.1.1](https://github.com/HaoYangJin/Big-Research/releases/tag/v2.1.1) | 统一 Big Research 命名，简化独立插件与文档结构 |
| 2026-10-21 | [v2.2.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v2.2.0) | 统一 Big-Research 显示名，补充 Codex 安装支持与 Windows 排查说明 |

[完整发布记录](https://github.com/HaoYangJin/Big-Research/releases) · [源代码历史](https://github.com/HaoYangJin/Big-Research/commits/main/) · [近期变更](https://github.com/HaoYangJin/Big-Research/blob/main/.github/maintainers/CHANGELOG.md)

## 一起补上尚未支持好的环节

贡献可以从一项具体的研究困难开始，不必先改代码。

| 你遇到的情况 | 有帮助的贡献 |
| --- | --- |
| 某种方法的检查不适合你的研究传统 | 说明问题、适用范围，提供一手方法资料和需要调整的判断标准 |
| 安装或恢复项目时卡住 | 提供客户端与版本、最小复现步骤、预期和实际结果 |
| 指引看不懂，或翻译不自然 | 指出具体段落，给出读者能直接采用的改写 |
| 某条评议缺少依据 | 指出证据位置、推理缺口，以及怎样才能复核 |

通过[贡献指南](../CONTRIBUTING.md)和[现有 Issue 表单](https://github.com/HaoYangJin/Big-Research/issues/new/choose)参与。提交前移除私人研究材料、参与者信息和凭据。这里列的是欢迎讨论的方向，不是已承诺的开发排期。

## 来源与维护

本页根据仓库 Git 历史、现有方法说明与公开 Release 整理，发布记录核对于 2026-10-22。设计参考及各自适用边界见[参考与致谢](research-basis.md)；参考不代表原作者背书，也不代表复现了相关系统的结果。

新增版本时应核对 Release 的实际日期、标签和变更，再更新本页及英文版。README 中的 CI 徽章由 GitHub 提供；已有 Star History 图依赖第三方服务，图不可用时可访问 [Star History 文字入口](https://www.star-history.com/#HaoYangJin/Big-Research&Date)。它们都不衡量科研质量。

本次新增内容位于 `big-repo:showcase` 标记之间；删除相应标记区块即可移除展示内容。删除故事页前先移除 README 和历史索引中的引用。
<!-- big-repo:showcase:end -->
