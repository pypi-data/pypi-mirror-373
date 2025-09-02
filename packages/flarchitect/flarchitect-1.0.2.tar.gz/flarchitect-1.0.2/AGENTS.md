# Agent Workflow and Contribution Guidelines

This repository uses an always-fresh suggestions backlog to drive quality improvements. Every change must keep suggestions and tests in sync.

On every change, do all of the following:

- Update `SUGGESTIONS.md` to reflect the change.
  - Tick done items by changing `[ ]` to `[x]` and move them to the `Complete` section at the bottom; remove completed items from open sections so only open items remain there.
  - Sections: `Security`, `Developer Experience`, `Architecture & Extensibility`, `API & Spec`, `Performance`, `Features`, `Testing & Quality`, `Documentation`, and `Complete`.
  - Maintain at least 2 open suggestions per non-`Complete` section. When you complete an item in a section, immediately add a new one in its place to keep the section at or above the minimum.
  - Reassess and move items between sections as needed; add new suggestions when gaps are discovered. Use a unique numeric ID `S###`, a short type/title, and a concise description.
  - Formatting rules: use a double newline between entries and one leading space so items render as a checklist. Line format for open sections: `[ ] S{###} - {Type} : {Description}.`

- Add or update unit tests for each functional change.
  - Prefer property/contract tests where appropriate.
  - Keep coverage at or above the configured threshold.

- Documentation updates: Adjust README/docs and CHANGELOG when behavior, configuration, or public APIs change.

- Pull requests: Reference suggestion IDs affected (e.g., `S065`, `S072`) and tick them in `SUGGESTIONS.md` as part of the PR; ensure each non-`Complete` section still contains at least 2 open items after your changes.

- Prioritisation cadence: Reassess `SUGGESTIONS.md` regularly; promote newly critical work and ensure completed items are moved under `Complete`, keeping all sections at or above the 2-item minimum.
