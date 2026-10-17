> This project uses AI tools to assist human scientists in scientific research; it is not an AI Scientist project. Human scientific taste and ethical judgment are irreplaceable. We hope researchers will work toward ideals that benefit all humanity and explore the boundaries of the unknown together.

# Big Research

**A human-led research workspace. Develop ideas into work you can pursue, inspect and improve.**

An independent, third-party open-source plugin for Codex and Claude Code. It is not affiliated with or certified as an official OpenAI plugin.

[简体中文](README.md) · [Get started](docs/quickstart.md) · [Methods and review](docs/methods.md) · [Contribute](CONTRIBUTING.md)

Bring an idea, source material, a draft or a question that has stalled. Explain the result you need. Big Research helps you find and carry out the next useful step.

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

Run these commands in the **Claude Code conversation input**:

```text
/plugin marketplace add HaoYangJin/Big-Research
/plugin install big-research@big-research-marketplace
```

Start a new session and send:

```text
/big-research:big-research
Help me organize my materials, compare feasible research directions and identify the next step.
```

### Codex CLI

Run these commands in your **system terminal**, such as Windows PowerShell:

```shell
codex plugin marketplace add HaoYangJin/Big-Research
codex plugin add big-research@big-research-marketplace
codex
```

In the new **Codex conversation**, send:

```text
$big-research
Help me organize my materials, compare feasible research directions and identify the next step.
```

See the [quickstart](docs/quickstart.md) for prerequisites, installation checks, desktop use and updates. The [usage guide](docs/quickstart.md#3-开启新会话并开始使用) explains the optional setup skill and the everyday entry point. Download the latest package from [Latest](https://github.com/HaoYangJin/Big-Research/releases/latest).

## Trace the reasoning

Explore a research map, evidence browser, candidate comparison and decisions/revision panel. MCP Apps compatible clients offer interaction; other environments use equivalent text, tables and read-only local snapshots.

Review combines general research quality, method-specific checks and optional venue or reporting guidance, including ICLR, NeurIPS, APA JARS and humanities review. Without a formal scale, use transparent working criteria and evidence-based reasons. Reporting completeness is different from scientific validity. No uncalibrated cross-field total or acceptance probability is produced.

This project does not replace researchers, ethics review or formal peer review. File integrity checks do not establish that research claims are true.

See the [methods](docs/methods.md) and [contribution guide](CONTRIBUTING.md). Import existing project data using the [quickstart](docs/quickstart.md#迁移已有项目).

[References and acknowledgments](docs/research-basis.md) · [MIT](LICENSE)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=HaoYangJin/Big-Research&type=Date)](https://www.star-history.com/#HaoYangJin/Big-Research&Date)
