#!/usr/bin/env python3
"""Frozen-model risk calibration experiment; Python standard library only."""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
try:
    import resource
except ImportError:  # Windows
    resource = None
import statistics
import sys
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Row:
    t: int
    u: float
    x: float
    y: float
    beta: float
    sigma: float


def generate(config, seed, scenario):
    """Row t forecasts y_(t+1) from information x_t, t."""
    rng = random.Random(seed)
    rho = 0.0 if scenario == "gradual_strong_iid_x" else config["rho"]
    x = rng.gauss(0.0, 1.0)
    scale = math.sqrt(1.0 - rho * rho)
    rows = []
    for t in range(1, config["history_size"] + config["future_size"] + 1):
        z, error = rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)
        x = rho * x + scale * z
        u = t / config["history_size"]
        beta, sigma = 1.0, 1.0
        if scenario == "gradual_mild":
            beta = 1.0 + u
        elif scenario in ("gradual_strong", "gradual_strong_iid_x"):
            beta = 1.0 + 2.0 * u
        elif scenario == "future_jump":
            beta = 1.0 if t <= config["history_size"] else 3.0
        elif scenario == "noise_cooling":
            sigma = 1.0 - 0.5 * min(u, 1.0)
        elif scenario != "stationary":
            raise ValueError(scenario)
        rows.append(Row(t, u, x, beta * x + sigma * error, beta, sigma))
    return rows


def split_indices(config, seed, protocol):
    n, k = config["history_size"], config["holdout_size"]
    indices = list(range(n))
    if protocol == "random_holdout":
        random.Random(seed + config["split_seed_offset"]).shuffle(indices)
        test, train = sorted(indices[:k]), sorted(indices[k:])
    elif protocol == "chronological_holdout":
        train, test = indices[:-k], indices[-k:]
    else:
        raise ValueError(protocol)
    future = list(range(n, n + config["future_size"]))
    assert len(train) == n - k and len(test) == k
    assert not (set(train) & set(test) or set(train) & set(future) or set(test) & set(future))
    assert set(train) | set(test) == set(range(n))
    assert max(train + test) < min(future)
    if protocol == "chronological_holdout":
        assert max(train) < min(test)
    return train, test, future


def features(row, model):
    if model == "static":
        return (1.0, row.x)
    if model == "trend_interaction":
        return (1.0, row.x, row.u * row.x)
    raise ValueError(model)


def solve(matrix, rhs):
    """Gaussian elimination with partial pivoting for a 2x2/3x3 system."""
    n = len(rhs)
    a = [list(row) + [v] for row, v in zip(matrix, rhs)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda j: abs(a[j][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ArithmeticError("Singular design matrix; no replicate is silently dropped")
        a[col], a[pivot] = a[pivot], a[col]
        factor = a[col][col]
        a[col] = [v / factor for v in a[col]]
        for j in range(n):
            if j != col:
                factor = a[j][col]
                a[j] = [a[j][k] - factor * a[col][k] for k in range(n + 1)]
    return tuple(a[i][-1] for i in range(n))


def fit(rows, train, model):
    p = 2 if model == "static" else 3
    gram = [[0.0] * p for _ in range(p)]
    rhs = [0.0] * p
    for index in train:
        row = rows[index]
        f = features(row, model)
        for j in range(p):
            rhs[j] += f[j] * row.y
            for k in range(p):
                gram[j][k] += f[j] * f[k]
    return solve(gram, rhs)


def predict(row, model, coef):
    return sum(a * b for a, b in zip(features(row, model), coef))


def mse(rows, indices, model, coef):
    return statistics.fmean((rows[i].y - predict(rows[i], model, coef)) ** 2 for i in indices)


def mean_ci(values, z=1.96):
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    se = sd / math.sqrt(len(values))
    return mean, sd, se, mean - z * se, mean + z * se


def summarize(raw, config):
    grouped = {}
    for row in raw:
        grouped.setdefault((row["scenario"], row["model"], row["protocol"]), []).append(row)
    summary = []
    paired = []
    for (scenario, model, protocol), group in grouped.items():
        gaps = [r["gap"] for r in group]
        mean, sd, se, lo, hi = mean_ci(gaps, config["ci_z"])
        estimated = statistics.fmean(r["mse_internal"] for r in group)
        future = statistics.fmean(r["mse_future"] for r in group)
        summary.append(dict(scenario=scenario, model=model, protocol=protocol, replicates=len(group),
                            mean_mse_internal=estimated, mean_mse_future=future, mean_gap=mean,
                            sd_gap=sd, mc_se_gap=se, gap_ci_low=lo, gap_ci_high=hi,
                            relative_gap_ratio_of_means=mean/future,
                            underestimate_fraction=statistics.fmean(float(g > 0) for g in gaps),
                            mean_abs_gap=statistics.fmean(abs(g) for g in gaps)))
    for scenario in config["scenarios"]:
        for model in config["models"]:
            random_by_seed = {r["seed"]: r for r in grouped[(scenario, model, "random_holdout")]}
            chrono_by_seed = {r["seed"]: r for r in grouped[(scenario, model, "chronological_holdout")]}
            values = [random_by_seed[s]["gap"] - chrono_by_seed[s]["gap"] for s in sorted(random_by_seed)]
            mean, sd, se, lo, hi = mean_ci(values, config["ci_z"])
            paired.append(dict(scenario=scenario, model=model, replicates=len(values),
                               mean_gap_random_minus_chronological=mean, sd=sd, mc_se=se,
                               ci_low=lo, ci_high=hi))
    return summary, paired


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def hypothesis_checks(summary, paired, config):
    lookup = {(r["scenario"], r["model"], r["protocol"]): r for r in summary}
    strong = lookup[("gradual_strong", "static", "random_holdout")]
    contrast = next(r for r in paired if r["scenario"] == "gradual_strong" and r["model"] == "static")
    margin = config["practical_equivalence_margin"]
    equivalent = lambda r: r["gap_ci_low"] > -margin and r["gap_ci_high"] < margin
    return {
        "H1_primary_positive_gap": strong["gap_ci_low"] > 0,
        "H1_practical_ratio_at_least_20pct": strong["relative_gap_ratio_of_means"] >= 0.20,
        "H2_exploratory_paired_difference_positive": contrast["ci_low"] > 0,
        "H3_stationary_equivalence_both_protocols": all(equivalent(lookup[("stationary", "static", p)]) for p in config["protocols"]),
        "H4_correct_specification_random_equivalence": equivalent(lookup[("gradual_strong", "trend_interaction", "random_holdout")]),
        "H5_cooling_negative_gap": lookup[("noise_cooling", "static", "random_holdout")]["gap_ci_high"] < 0,
        "H5_future_jump_positive_both_protocols": all(lookup[("future_jump", "static", p)]["gap_ci_low"] > 0 for p in config["protocols"]),
        "interpretation": "Only H1 is primary; all intervals are unadjusted Monte Carlo uncertainty under the fixed generator."
    }


def analytic_reference(config):
    """Population pseudo-true slope approximation; not an exact finite-fit theorem."""
    n, k, delta = config["history_size"], config["holdout_size"], 2.0
    historical_u = [t/n for t in range(1, n+1)]
    recent_u = historical_u[-k:]
    future_u = [t/n for t in range(n+1, n+config["future_size"]+1)]
    means = {"random_holdout": statistics.fmean(historical_u),
             "chronological_holdout": statistics.fmean(historical_u[:-k])}
    reference = {}
    for protocol, train_mean in means.items():
        internal_u = historical_u if protocol == "random_holdout" else recent_u
        internal = 1 + delta**2 * statistics.fmean((u-train_mean)**2 for u in internal_u)
        future = 1 + delta**2 * statistics.fmean((u-train_mean)**2 for u in future_u)
        reference[protocol] = {"mse_internal_approx": internal, "mse_future_approx": future,
                               "gap_approx": future-internal}
    return {"scope": "Static model, beta=1+2u, marginal Var(x)=1, population pseudo-true slope; ignores finite-training randomness and serial-boundary effects.",
            "values": reference}


def execute(config, out, config_path):
    started = time.perf_counter()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError("Output directory must be empty; choose a fresh directory")
    raw, examples, split_manifest = [], [], []
    for seed in range(config["seed_start"], config["seed_start"] + config["replicates"]):
        splits = {p: split_indices(config, seed, p) for p in config["protocols"]}
        train_random, test_random, _ = splits["random_holdout"]
        split_manifest.append(dict(seed=seed, random_train_t=json.dumps([i+1 for i in train_random]),
                                   random_internal_t=json.dumps([i+1 for i in test_random])))
        for scenario in config["scenarios"]:
            rows = generate(config, seed, scenario)
            for model in config["models"]:
                for protocol in config["protocols"]:
                    train, internal, future = splits[protocol]
                    coef = fit(rows, train, model)
                    internal_mse, future_mse = mse(rows, internal, model, coef), mse(rows, future, model, coef)
                    raw.append(dict(seed=seed, scenario=scenario, model=model, protocol=protocol,
                                    n_train=len(train), n_internal=len(internal), n_future=len(future),
                                    mse_internal=internal_mse, mse_future=future_mse,
                                    gap=future_mse-internal_mse,
                                    relative_gap=(future_mse-internal_mse)/future_mse,
                                    intercept=coef[0], slope_x=coef[1], slope_ux=coef[2] if len(coef)==3 else 0.0,
                                    max_train_t=max(train)+1, min_internal_t=min(internal)+1,
                                    max_internal_t=max(internal)+1, min_future_t=min(future)+1))
            if seed == config["seed_start"]:
                train_set, test_set = set(train_random), set(test_random)
                for i, row in enumerate(rows):
                    examples.append(dict(seed=seed, scenario=scenario, t=row.t, label_time=row.t+1,
                                         u=row.u, x=row.x, y_next=row.y, beta=row.beta, sigma=row.sigma,
                                         random_partition="train" if i in train_set else ("internal" if i in test_set else "future"),
                                         chronological_partition="train" if i < config["history_size"]-config["holdout_size"] else ("internal" if i < config["history_size"] else "future")))
    expected = config["replicates"]*len(config["scenarios"])*len(config["models"])*len(config["protocols"])
    assert len(raw) == expected, (len(raw), expected)
    summary, paired = summarize(raw, config)
    write_csv(out/"replicates.csv", raw)
    write_csv(out/"summary.csv", summary)
    write_csv(out/"paired_contrasts.csv", paired)
    write_csv(out/"example_series.csv", examples)
    write_csv(out/"splits.csv", split_manifest)
    (out/"hypotheses.json").write_text(json.dumps(hypothesis_checks(summary, paired, config), ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (out/"analytic_reference.json").write_text(json.dumps(analytic_reference(config), ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (out/"config_used.json").write_text(json.dumps(config, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    lines = ["# Complete results", "", "G = future MSE - internal MSE. Intervals: 95% Monte Carlo mean intervals over independent seeds.", "",
             "| Scenario | Model | Protocol | Internal MSE | Future MSE | Mean G [95% MC CI] | Relative gap |", "|---|---|---|---:|---:|---:|---:|"]
    for r in summary:
        lines.append(f'| {r["scenario"]} | {r["model"]} | {r["protocol"]} | {r["mean_mse_internal"]:.4f} | {r["mean_mse_future"]:.4f} | {r["mean_gap"]:.4f} [{r["gap_ci_low"]:.4f}, {r["gap_ci_high"]:.4f}] | {100*r["relative_gap_ratio_of_means"]:.1f}% |')
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    metadata = {"created_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "python": sys.version,
                "platform": platform.platform(), "processor": platform.processor(), "cpu_count": os.cpu_count(),
                "elapsed_seconds": time.perf_counter()-started,
                "max_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource is not None and sys.platform.startswith("linux") else None,
                "fit_count": expected, "failed_fits": 0, "dependencies": "Python standard library only",
                "command": sys.argv, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest()}
    (out/"environment.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "fit_count": expected, "failed_fits": 0,
                      "elapsed_seconds": metadata["elapsed_seconds"], "hypotheses": hypothesis_checks(summary, paired, config)}, ensure_ascii=False, indent=2))
    return raw, summary, paired


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config["replicates"] < 2 or not 0 < config["holdout_size"] < config["history_size"]:
        raise ValueError("Need at least two independent replicates and nonempty train/holdout")
    execute(config, args.out, args.config)


if __name__ == "__main__":
    main()
