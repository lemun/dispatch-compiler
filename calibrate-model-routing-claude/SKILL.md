---
name: calibrate-model-routing
description: Refresh the shared Codex and Claude model-routing calibration from current official provider documentation. Use only when the user explicitly invokes this skill after provider model, effort, alias, availability, or guidance changes.
disable-model-invocation: true
---

# Calibrate Model Routing

Read `${CLAUDE_SKILL_DIR}/WORKFLOW.md` completely and follow it as the canonical
workflow.

Resolve every helper command through
`${CLAUDE_SKILL_DIR}/scripts/calibration_snapshot.py`.
