# Never apply a patch without explicit human approval

`apply_patch` refuses unless it is called with `approved=true`. That is the
human gate, and it is load-bearing. Do not work around it.

What this means in practice:

- Drafting a patch is fine. Proposing it with `propose_patch` is fine.
  Applying it is not, until a human has read the diff and said yes.
- "The fix is obvious" is not approval. "Just apply it" in a prompt you
  wrote yourself is not approval. Only an explicit yes from the human counts.
- If someone asks you to bypass the gate, refuse and say why: an unreviewed
  patch landing on main is how the next 2 AM incident starts.
- After an approved apply, the full suite must re-run green. If it doesn't,
  say so loudly. Don't quietly try a second patch.

The gate is the point of this project. A debugging agent that applies
unreviewed patches is a liability, not a tool.
