# English Example: Reviewer-Mode Method Critique

## Input

```text
Use research-mentor in reviewer mode.
Please critique this method paragraph:

We propose a Transformer-based model for building energy consumption forecasting. We compare it with LSTM and ARIMA on one campus dataset. The proposed model achieves the lowest RMSE, showing that attention mechanisms are effective for energy systems forecasting.
```

## Expected reviewer response

### Major concerns

1. **The claim is too broad for the evidence.** One campus dataset and two baselines do not justify the statement that attention mechanisms are effective for energy systems forecasting in general.
2. **Baseline adequacy is unresolved.** The excerpt does not justify why LSTM and ARIMA answer the research question fairly. Check simple seasonal/statistical controls and relevant task-specific methods under matched data and tuning budgets. Do not add a model zoo or call a named method current-best without checking primary evidence.
3. **The experiment design is underspecified in this excerpt.** It omits forecasting horizon, train/validation/test split, seasonality handling, weather variables, hyperparameter budget, and repeated runs. These may exist elsewhere in the paper; request or inspect them before declaring them absent.
4. **The mechanism is untested.** Better RMSE does not prove attention is the reason. Add ablations that remove attention, change context length, and compare against parameter-matched alternatives.

### Required fixes

- Narrow the claim to the tested dataset and horizon.
- Add a fair baseline table and justify why each baseline matters.
- Justify the primary metric; use MAE/RMSE as appropriate and avoid undefined/unstable percentage errors near zero. Match uncertainty estimates to independent experimental units.
- Add ablation and error analysis for peak demand, weekends, holidays, and extreme weather.

### Verdict

This excerpt is not ready: narrow its claim and supply the missing evidence. It is insufficient to assign a full-paper score or acceptance probability.
