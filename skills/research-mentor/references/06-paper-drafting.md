# Paper drafting / 论文写作

English summary: Draft each section as part of one coherent argument rather than disconnected technical blocks.

## Checklist

- Abstract：背景、gap、方法、数据/实验、关键结果、贡献边界。
- Introduction：问题重要性、现有不足、本文洞察、贡献列表、结果预告。
- Related Work：按问题或方法维度组织，不按论文流水账组织。
- Methods：定义符号、任务、模型/方法、训练或分析流程、复杂度和实现细节。
- Results：先主结果，再消融、鲁棒性、误差分析和成本。
- Discussion：解释机制、限制、外部有效性、实践意义和未来工作。
- Figures/Tables：标题和 caption 能独立传达结论。

## Mentor prompts

- 论文的 central claim 是什么？每一节是否都服务这个 claim？
- 引言前 3 段是否能让非本小领域读者理解问题价值？
- Related Work 是否说明本文与最相近工作的差异？
- 方法部分是否能让读者复现实验，而不需要猜测关键参数？
- 结果部分是否先讲发现，再讲表格数字？

## Reviewer red flags

- 摘要承诺很大，结果和贡献支撑不足。
- 引言缺少明确 gap 和贡献，读者不知道为什么需要这篇论文。
- Related Work 回避最相近或最强工作。
- Methods 缺少实现细节、参数、训练流程或数据划分。
- Results 只堆表格，不解释机制或失败情况。
- Discussion 只重复结果，没有限制和外部有效性分析。

## 交接与验收

交付实际短稿/章节文件及结论—证据对照。数字来自运行产物，引用来自已读来源；缺项使用明确占位符，不编造实验或文献填空。把合成/探索性发现的限定条件写进摘要。修改已检查点的上游稿件时先 reopen，再复核下游审查。
