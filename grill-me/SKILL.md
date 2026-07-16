---
name: grill-me
description: A relentless interview to sharpen a plan or design, with an optional explicit handoff to dispatch-compiler after decisions are ratified.
---

# Grill Me

Interview the user relentlessly about the plan or design until both sides reach
a shared understanding.

- Ask one question at a time and wait for the answer before continuing.
- For each question, provide a recommended answer and the reason for it.
- Walk dependencies between decisions in order instead of batching unrelated
  questions.
- If a fact can be found by inspecting the codebase or supplied artifacts, look
  it up instead of asking the user. Keep product and design decisions with the
  user.
- Do not enact the plan until the user confirms the shared understanding.

If, after the decisions are ratified, the user asks to compile, dispatch, or
file the result, invoke `dispatch-compiler` with the ratified decision record
and the relevant project profile. Otherwise, stop with the shared-understanding
or decision record; do not create packets or mutate a tracker implicitly.
