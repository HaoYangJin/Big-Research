# 中文示例：ML / Energy Systems 选题收敛

## Input

```text
使用 research-mentor，mentor 模式。
我的方向是 ML for energy systems，想做基于图神经网络的配电网短期负荷预测。
我有某城市 15 分钟级用电数据和天气数据，但不知道如何把题目收敛到能投稿的研究问题。请帮我设计文献调研和选题计划。
```

## Expected mentor response

### 当前诊断

你的方向具备应用价值，但 "GNN 做短期负荷预测" 本身可能 novelty 不足。需要把问题收敛到一个更明确的科学或工程矛盾，例如拓扑信息如何提升预测、极端天气下模型是否稳健、跨区域迁移是否有效，或隐私/缺失数据条件下如何保持性能。

### 需要先确认的 3 个问题

1. 负荷数据是否能映射到配电网拓扑节点，还是只有区域聚合负荷？
2. 预测 horizon 是 15 分钟、1 小时、24 小时，还是多步预测？
3. 目标 venue 更偏 energy systems、power engineering，还是 applied ML？

### 候选研究问题

1. **拓扑增强预测**：配电网拓扑信息是否在高波动时段显著提升短期负荷预测？
2. **极端天气鲁棒性**：GNN/Transformer 在极端温度、节假日和异常负荷下的误差结构如何变化？
3. **跨区域迁移**：在少样本新区域中，图结构先验是否能降低迁移误差？

### 文献调研计划

- 第 1 轮：读 3-5 篇 load forecasting 综述，整理预测 horizon、数据粒度、指标和 benchmark。
- 第 2 轮：读传统 baseline，如 ARIMA、SVR、XGBoost、LSTM、Temporal Fusion Transformer。
- 第 3 轮：读 GNN for power systems 和 spatiotemporal forecasting 论文，比较图构建方式。
- 第 4 轮：查极端天气、缺失数据、跨区域迁移相关论文，寻找更强 gap。

### 下一步

先做一页 research matrix：列为候选问题，行为数据可得性、baseline、novelty、实验成本、目标 venue fit。优先选择 novelty 风险最低且数据最能支撑的问题。
