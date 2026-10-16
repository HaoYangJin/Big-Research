# Persistent research records

The CLI requires Python 3.10+ and no third-party packages. It stores files only in the chosen project, never executes the recorded commands, and never sends data or checks URLs. Source verification and scientific adequacy remain the researcher's/agent's responsibility. Do not let several agents edit a project at once; checkpoint mutations use a fail-fast local lock and atomic state replacement.

## Commands

Resolve `workflow.py` from this skill's `scripts/` directory; `PROJECT` below is the research output directory.

```bash
python workflow.py init PROJECT --title "Bounded research question" --mode mixed
python workflow.py status PROJECT
python workflow.py template --phase 1
python workflow.py checkpoint PROJECT --phase 1 --artifact artifacts/01-scope.json
python workflow.py checkpoint PROJECT --phase 2 --status blocked --reason "Required data unavailable"
python workflow.py reopen PROJECT --phase 2 --reason "Data arrived; revise hypothesis"
python workflow.py validate PROJECT
```

Use `--phase N` on `init` to start midway: earlier stages become `not_requested`. Use `--kind empirical|theoretical|review` to choose the results gate. Initialization requires an empty directory and refuses to overwrite files. `template` prints JSON to stdout: save it using the host's file tool or shell redirection, then replace every `TODO` with substantive content before checkpointing.

`checkpoint` accepts only the current phase. `done` advances; `blocked` stays at that phase; `skipped` advances with an explicit scope reason. Reopen the earliest changed phase to clear its checkpoint and all downstream checkpoints. Existing outputs stay on disk; inspect and reuse them deliberately. The history records checkpoint/reopen events but is not a tamper-proof audit log.

## Project files

- `project.json`: schema/version, title, research kind, mode, stage status, current phase, checkpoint hashes, and history.
- `evidence.json`: source, experiment, and claim records. Edit this ledger with normal file tools, then validate it before checkpointing.
- `artifacts/`: actual drafts, protocols, scripts, results, reviews, revisions, and stage JSON. All linked paths are relative to the project directory. Absolute paths, traversal, and escaping symlinks are rejected.

Every stage artifact has `phase`, `summary`, `criteria`, `evidence` (IDs), and `outputs` (paths). `template` supplies the required criteria names. Stages 7/8 add `blocking_concerns` / `resolved_concerns` lists of stable concern IDs. Stage 9 adds `decision: "ready" | "not_ready"`. Link actual draft files in phase 6; do not store only a promise to draft.

## Evidence ledger example

The values below illustrate the schema; replace them with records from actual work. The all-zero digest is not a valid experiment result.

```json
{
  "sources": [{
    "id": "S1", "title": "Actual source title", "url": "https://publisher.org/paper",
    "status": "verified", "accessed": "2026-10-16", "locator": "Section 3, evaluation protocol"
  }],
  "experiments": [{
    "id": "E1", "status": "executed", "command": "python artifacts/experiment.py",
    "seed": [11, 23, 37], "environment": "Python version, OS, dependency versions",
    "artifacts": [{"path": "artifacts/metrics.json", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}]
  }],
  "claims": [{
    "id": "C1", "text": "A bounded finding from the recorded experiment",
    "status": "supported", "evidence": ["E1"]
  }]
}
```

Use source status `unverified` until its actual contents have been inspected. An `accessed` date and locator record that inspection; the CLI does not perform it. For a local primary source or proof, use `path` and `sha256` instead of `url`, with the same title/status/accessed/locator fields. Use an experiment status of `planned` or `failed` when appropriate; neither supports a `supported` claim. An executed record needs a command, environment, seed (or `null` for deterministic work), and nonempty files with matching SHA-256 hashes. Include the script/config, raw metrics, and run log in the experiment artifacts, not only a handwritten summary. Hash using Python `hashlib.sha256(Path(path).read_bytes()).hexdigest()`.

Claim status is `supported`, `hypothesis`, or `unsupported`. A supported claim must link directly to verified sources or executed experiments; claim-to-claim references are prohibited. Semantic entailment is reviewed by the agent, not inferred from an ID link.

Keep checkpointed records immutable during normal progression. Give an experiment plan an ID such as `E-plan-1` and the actual run a new ID such as `E-run-1`; keep the frozen hypothesis separate from the supported result claim. Updating a plan in place from planned to executed also changes its earlier evidence snapshot and requires reopening the earliest affected phase. If a prior record was wrong, use that explicit reopen path rather than bypassing validation.

## Gates and limits

- All `done` stages need filled criteria and an unchanged stage artifact, outputs, and linked evidence records (including a claim's direct dependencies). Adding unrelated evidence does not invalidate previous checkpoints.
- Empirical phase 5 needs an executed experiment; theoretical phase 5 needs a derivation/proof artifact; review phase 5 needs a verified source.
- Phase 6 needs a draft and at least one supported claim. This is a minimum structural gate, not a full citation/claim audit.
- `ready` at phase 9 needs stages 1–8 done, no unresolved blocking concern IDs, and no unsupported claims. Mark `not_ready` if these fail. Skipped/midway stages cannot qualify for full submission readiness without revisiting them.
- `valid: true` / `structural_only` verifies shape, references, and recorded file integrity. It does not certify that commands were run, findings are true, a proof is correct, a venue is suitable, or the manuscript will be accepted. Keep the scientific review separate and explicit.


## v1.1.0：模式、锁与迁移

`init --mode auto` 是默认值；当前 mode 保持 mentor/reviewer/mixed，新增 mode_policy 为 auto/manual。自动阶段映射为 1–4/6 mentor、5/8 mixed、7/9 reviewer。明确任务可用 `mode <dir> --select auto --task plan|review|revise`；手动选择 `mode <dir> --select reviewer --reason "用户要求审稿"`，会保存历史但不修改证据和阶段。status 返回策略。

旧 v1.0.0 项目使用 `migrate <dir>` 显式升级：先验证所有记录与哈希，保存 project.v1.0.0.backup.json，再更新版本和历史。旧 mode 默认 manual，保留原偏好。重复迁移无副作用。回滚时停止写入、保留升级后的项目副本，再用备份替换 project.json 并运行 v1.0.0 CLI；升级后新建的检查点不会出现在旧备份中。未知版本拒绝迁移。

锁改为操作系统 advisory lock；进程退出自动释放，.workflow.lock 文件保留，不能按文件存在判断持锁，也不要手动删除。旧版 CLI 不能与新版同时写同一目录。只支持单机本地文件系统；共享磁盘/跨主机并发未验证。Windows 使用 msvcrt，POSIX 使用 flock。
