---
name: grill-me
description: A relentless interview to sharpen a plan or design, with an optional explicit handoff to dispatch-compiler after decisions are ratified.
---

# Grill Me

Run a `/grilling` session and preserve its one-consequential-decision-at-a-time
discipline.

If, after the decisions are ratified, the user asks to compile, dispatch, or
file the result, invoke `dispatch-compiler` with the ratified decision record
and the relevant project profile. Otherwise, stop with the shared-understanding
or decision record; do not create packets or mutate a tracker implicitly.
