# Paracosm

Deterministic simulated worlds with optional model-neutral habitat minds.
Python 3.14+. Uses Thoughtform contracts without a mandatory model or harness.

```python
from thoughtform import Being
from paracosm import Habitat, Resident, Snapshot, World

world = World(Snapshot('pluralopia', (Habitat('woods', 'The Woods'),),
    (Resident(Being('alice', 'Alice'), 'woods'),
     Resident(Being('bob', 'Bob'), 'woods'))))
result = world.step({})  # Missing policies propose wait; one deterministic tick.
assert result.snapshot.tick == 1
```

A policy implements `decide(Observation) -> Action`. Actor IDs determine call
order, and every observation comes from the same immutable pre-step snapshot.
Validate all proposals before committing any state. Unknown actors, identity
spoofing, unsupported actions and invalid targets preserve the entire step.
Trusted policy code is ordinary Python, not a sandbox. Reentrant steps fail.

Initial actions are `wait`, resident `move`, text `say`, and habitat-mind
`condition`. A mind is an explicit `Habitat(..., mind=Being(...))`; its policy
can propose condition changes only for that habitat. Role labels alone do not
grant authority. A model's text cannot rewrite the authoritative world.

`Step` returns the next immutable snapshot and accepted actions. This initial
in-memory foundation does not persist history or claim model inference replay.
Backpack snapshot/event storage, rule/version compatibility, learned minds and
experience exports have separate owning tasks. There are at most 32 habitats
and 128 total actors; observation/action text is explicitly bounded.

Run `uv sync`, `uv run paracosm` for the offline two-being example, and
`PYTHONPATH=src python -m unittest discover -s tests` for deterministic/atomicity
checks. CI qualifies wheel/source installations on Linux, macOS and Windows.

[Repository plan](IMPLEMENTATION_PLAN.md),
[complete family plan](https://github.com/wispsy/wispsy/blob/main/docs/cohesion-block-b/IMPLEMENTATION_PLAN.md),
and [Project](https://github.com/orgs/wispsy/projects/28).
