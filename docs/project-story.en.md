# The Big-Research story

[Home](../README.en.md) · [简体中文](project-story.md) · [Get started](quickstart.md)

<!-- big-repo:showcase:start -->
## From research stages to work you can resume

Big-Research asks more than what a single conversation can answer. When researchers return to a project, can they see which materials they used, what they tried, why they changed methods and which questions remain open?

The early Research Workflow organized research stages through mentor, reviewer and mixed modes. Its v1.0.0 implementation already saved progress, linked evidence and offered resumable checkpoints. v1.1.0 improved recovery and conversational guidance. By v2.1.0, the project had moved toward a research workspace: tasks and dependencies, claims and materials, candidate approaches, decisions and revisions could be inspected separately and in relation to one another.

You can trace this through the [early implementation](https://github.com/HaoYangJin/Big-Research/commit/6bda93f), [checkpoint improvements](https://github.com/HaoYangJin/Big-Research/commit/2cebfe6) and [workspace implementation](https://github.com/HaoYangJin/Big-Research/commit/6a96ec3). This is a history of software changes, not an evaluation of research outcomes.

## Three choices behind the current design

### Keep research judgment with the researcher

The homepage defines the project as a tool to assist human scientists. Research questions, major method changes, ethical choices and final conclusions remain the researcher's responsibility. Recording the source of a claim helps someone inspect it. Complete files or a completed workflow cannot establish that the claim is true.

### Match methods to questions

Quantitative experiments, qualitative inquiry, interpretive and humanities research, formal arguments, synthesis and mixed methods need different materials and standards of judgment. The current implementation offers composable method modules and distinguishes reporting completeness from scientific judgment. Competing interpretations, negative findings and revisiting earlier choices all need room. See [methods and review](methods.md) for the boundaries.

### Leave records that support the next step

The research map, evidence browser, candidate comparison and decisions/revision panel provide different views of one project. MCP Apps compatible clients can offer interactive views; other environments use text, tables or local read-only snapshots. These help researchers inspect existing work and decide what to do next. See [compatibility](compatibility.md) for client support.

## Milestones with a public record

Dates below are GitHub Release publication dates in UTC, rather than local commit dates. Early versions used the Research Workflow name. Always follow the [current guide](quickstart.md) for installation.

| Published (UTC) | Version | What changed |
| --- | --- | --- |
| 2026-05-16 | [v0.1.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v.0.1.0) | Early release of Research Workflow Skill |
| 2026-10-16 | [v1.0.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v1.0.0) | Research stages packaged as a plugin, evidence links and resumable checkpoints |
| 2026-10-16 | [v1.1.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v1.1.0) | Improved checkpoint recovery, mode selection and research guidance |
| 2026-10-17 | [v2.1.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v2.1.0) | Human-led research workspace with method modules and review views |
| 2026-10-17 | [v2.1.1](https://github.com/HaoYangJin/Big-Research/releases/tag/v2.1.1) | Unified Big Research naming and simplified the independent plugin and documentation |
| 2026-10-21 | [v2.2.0](https://github.com/HaoYangJin/Big-Research/releases/tag/v2.2.0) | Consistent Big-Research display name, Codex command support checks and Windows troubleshooting |

[All releases](https://github.com/HaoYangJin/Big-Research/releases) · [Source history](https://github.com/HaoYangJin/Big-Research/commits/main/) · [Recent changes](https://github.com/HaoYangJin/Big-Research/blob/main/.github/maintainers/CHANGELOG.md)

## Help with a research task that needs better support

A contribution can begin with a specific research difficulty; it need not begin with code.

| What you encounter | A useful contribution |
| --- | --- |
| A method check does not fit your research tradition | Explain the question and scope; provide primary method guidance and the criteria that need changing |
| Installation or project recovery fails | Share client/version, minimal reproduction steps, expected and actual results |
| Guidance or translation is hard to follow | Identify the passage and suggest wording readers can act on |
| Review feedback lacks support | Point to the evidence, reasoning gap and a way to verify the assessment |

Use the [contribution guide](../CONTRIBUTING.md) and [existing issue forms](https://github.com/HaoYangJin/Big-Research/issues/new/choose). Remove private research materials, participant information and credentials before posting. These are invitations to discuss improvements, not a committed development schedule.

## Sources and maintenance

This page draws on repository history, current method documentation and public Releases. Release records were checked on 2026-10-22. See [references and acknowledgments](research-basis.md) for design sources and their limits. References imply neither endorsement nor reproduction of those systems' results.

For each new version, check the actual Release date, tag and changes before updating both story pages. GitHub supplies the README CI badge. The existing Star History chart uses a third-party service; if it fails, use the [Star History text link](https://www.star-history.com/#HaoYangJin/Big-Research&Date). Neither measures research quality.

New showcase content sits between `big-repo:showcase` markers. Remove the corresponding marked block to remove that content. Before deleting a story page, remove references from the READMEs and history index.
<!-- big-repo:showcase:end -->
