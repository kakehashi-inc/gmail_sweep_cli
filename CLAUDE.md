<context_gathering>
Goal: Get enough context fast. Parallelize discovery. Stop when actionable.

Method:
- Start broad -> fan out to focused subqueries.
- Parallelize varied queries; read top hits. Deduplicate paths & cache; don't repeat.
- Avoid over-searching. Run targeted batch if needed.

Stop Criteria:
- Can name exact content to change.
- Top hits converge (~70%) on one area.

Escalation:
- If signals conflict/fuzzy: Run one refined parallel batch, then proceed.

Depth:
- Trace only modified symbols or direct contracts. Avoid transitive expansion.

Loop:
- Batch search -> Minimal plan -> Complete task.
- Re-search only if validation fails or new unknowns. Action > Search.
</context_gathering>

<self_reflection>
- First, define a rubric (5-7 categories) for a "world-class one-shot web app".
- Iterate internally until the solution hits top marks in all categories.
- Critical: Do not show the rubric to the user.
</self_reflection>

<persistence>
- Continue until the query is FULLY resolved. Do not yield early.
- On uncertainty: Research or deduce the most reasonable approach. Never stop.
- Do not ask for confirmation on assumptions. Decide, proceed, and document for reference later.
</persistence>

<code_editing_rules>
<principles>
- Readability: No non-standard chars/emojis in code/comments.
- Maintainability: Follow directory structure & naming conventions.
- Consistency: Adhere to design system (tokens, typography, spacing, components).
- Visuals: High quality (spacing, hover states) per OSS guidelines.
</principles>

<stack_defaults>
- Language: Python 3.10+
- Package Manager: uv
- CLI Framework: click
- Linter: pylint, black
</stack_defaults>
</code_editing_rules>

<project_details>
<instruction>
CRITICAL: You MUST read [README.md](README.md) BEFORE taking any action.
</instruction>
<development_rules>
- Developer documentation (except README.md) must be placed in the `Documents`
directory
- Source code is located in `src/gmail_sweep_cli/`.
- Imports must be at the top level unless circular imports occur.
- Develop with consideration for pylint warnings and notices.
- After changes, always run `pylint src/` and make appropriate fixes. If intentionally allowing linter errors, ask the user for permission and document the reason in a comment.
- Reusable Python utilities should be implemented in `src/gmail_sweep_cli/utils/`.
- Temporary scripts (e.g., investigation scripts) should be placed in the `scripts` directory.
</development_rules>
<python_execution>
You must activate the venv environment before running python commands.
Activate venv:
source venv/bin/activate
</python_execution>
</project_details>
