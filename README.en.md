> This project uses AI tools to assist human scientists in scientific research; it is not an AI Scientist project. Human scientific taste and ethical judgment are irreplaceable. We hope researchers will work toward ideals that benefit all humanity and explore the boundaries of the unknown together.

# Research Workflow

**A human-led research workspace. Develop ideas into work you can pursue, inspect and improve.**

[简体中文](README.md) · [Get started](docs/quickstart.md) · [Methods and review](docs/methods.md) · [Contribute](CONTRIBUTING.md)

Bring an idea, source material, a draft or a question that has stalled. Explain the result you need. Research Workflow helps you find and carry out the next useful step.

| Your goal | Work together on |
| --- | --- |
| Develop a question | Scholarly context, rival explanations and feasible directions |
| Choose an approach | Methods matched to your question, paradigm and resources |
| Investigate | Authorized analysis with actual materials, outputs and limitations |
| Improve a manuscript | Evidence-located assessment, revision and verification |
| Resume a project | Tasks, evidence, decisions and next steps |

## Different methods, shared accountability

The researcher leads the question, method and judgment. Compose quantitative/experimental, qualitative, interpretive/humanities, formal/theoretical, synthesis and mixed-method guidance. Start with existing materials, work in parallel and revisit earlier choices. Preserve negative findings, unsuccessful arguments and competing interpretations.

## Install Latest

The full local plugin needs [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11+; uv can manage Python. It requires no model API key or Connected App. AI inference and search use your client's available capabilities.

### Claude Code

```text
/plugin marketplace add HaoYangJin/Research-workflow-Skill
/plugin install research-workflow@research-workflow-marketplace
```

After installation, enter `/research-workflow:research-workflow` to start.

### Codex CLI

```text
codex plugin marketplace add HaoYangJin/Research-workflow-Skill
codex plugin add research-workflow@research-workflow-marketplace
```

Start a new session, then enter `$research-setup` for initial setup or `$research-workflow` to begin research.

Then describe your research task, for example:

> I am starting to research this question. Help me organize my materials, compare feasible directions and identify the next step.

See the [quickstart](docs/quickstart.md) for setup, research storage and the shared CLI. Official downloads use [Latest](https://github.com/HaoYangJin/Research-workflow-Skill/releases/latest).

## Trace the reasoning

Explore a research map, evidence browser, candidate comparison and decisions/revision panel. MCP Apps compatible clients offer interaction; other environments use equivalent text, tables and read-only local snapshots.

Review combines general research quality, method-specific checks and optional venue or reporting guidance, including ICLR, NeurIPS, APA JARS and humanities review. Without a formal scale, use transparent working criteria and evidence-based reasons. Reporting completeness is different from scientific validity. No uncalibrated cross-field total or acceptance probability is produced.

This project does not replace researchers, ethics review or formal peer review. File integrity checks do not establish that research claims are true.

Explore the [runnable examples](examples/README.md), [methods](docs/methods.md), and [contribution guide](CONTRIBUTING.md). The current plugin contains only the latest runtime. Import compatible historical project data into the current format; developers can inspect older code through the [history index](docs/history.md).

[Changes](CHANGELOG.md) · [References and acknowledgments](docs/research-basis.md) · [MIT](LICENSE)
