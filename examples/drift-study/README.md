# 合成时序研究示例 / Synthetic drift study

这个可复现的合成实验展示协议冻结、对照、阴性结果及结论边界。它不是新的预测方法，也不是现实数据上的性能证明。可使用当前研究工作台记录实验和评议；旧验证记录保存在[历史版本](../../docs/history.md)中。

## Run

From the repository root / 从仓库根目录运行：

```bash
python -m unittest discover -s examples/drift-study -p test_experiment.py -v
python examples/drift-study/experiment.py --out ./outputs/drift-run-1
python examples/drift-study/experiment.py --out ./outputs/drift-run-2
```

Python 3.10+，标准库；默认 300 个独立种子 × 6 种情形 × 2 个模型 × 2 种协议，共 7,200 次拟合。在当前 Linux 环境约数秒到十余秒；耗时不是性能承诺。输出目录必须为空。代码默认读取旁边的 `config.json`，也可传 `--config`，改变配置后需重新说明假设与判断规则。

输出包括逐种子 `replicates.csv`、完整 `summary.csv`、配对比较、划分记录、环境与事前假设检查。两次重跑的数值产物应一致；`environment.json` 中时间、路径和运行时长自然不同。浮点最后几位可能随 Python/平台变化。

## Interpretation

协议见 [protocol.md](protocol.md)，已核验的一手文献与边界见 [sources.md](sources.md)。

定义 G = 未来 MSE − 内部留出 MSE。统计单位是独立生成序列；区间衡量固定生成器下的 Monte Carlo 均值不确定性，不是现实总体的置信保证。

原始默认运行中：

| 情形 / 模型 / 协议 | 内部 MSE | 未来 MSE | 平均 G [95% MC 区间] |
| --- | ---: | ---: | ---: |
| 平稳 / 静态 / 随机 | 1.009 | 1.006 | −0.003 [−0.022, 0.016] |
| 强线性漂移 / 静态 / 随机 | 1.337 | 2.497 | 1.160 [1.114, 1.207] |
| 强线性漂移 / 正确指定交互 / 随机 | 1.010 | 1.013 | 0.003 [−0.016, 0.022] |
| 噪声下降 / 静态 / 随机 | 0.587 | 0.253 | −0.335 [−0.344, −0.326] |

方向依赖生成机制和模型；不支持“随机划分总是低估未来风险”。随机与时间协议分别拟合不同模型，不能把它们的误差差异解释为固定同一模型的纯评价方法效应。正确指定交互模型已利用生成机制知识，不代表它能预测未知漂移。未完成真实数据验证、新颖性查证、具体 venue 匹配、独立外审或实际投稿。

This synthetic example demonstrates protocol freezing, controlled comparisons, negative results and bounded claims. It does not establish new methodology, real-world generalization or submission readiness. Use the current research workspace to record its evidence and build a complete research project.
