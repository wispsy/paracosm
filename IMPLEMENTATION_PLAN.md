# Paracosm implementation plan

Paracosm owns authoritative worlds, habitats, spatial membership, deterministic
time/steps, accepted events and rule validation. Thoughtform owns neutral beings
and proposed actions; Hypnosis owns execution/job policy; Thoughtformula owns
model mathematics. The
[complete Cohesion Block B plan](https://github.com/wispsy/wispsy/blob/main/docs/cohesion-block-b/IMPLEMENTATION_PLAN.md)
records all shared contracts, library reuse, milestones and task acceptance.
[Project 28](https://github.com/orgs/wispsy/projects/28) and owning issues are the
execution queue.

## Deterministic stepping — PARA-01

Create immutable bounded habitat/resident/world snapshots. Compute actions in
stable actor-ID order from one pre-step observation snapshot. Validate every
proposal before applying any state change. Rejected actions, unknown actors,
identity spoofing and reentrancy preserve the authoritative snapshot. The first
reference has one habitat and two beings; a second habitat exercises movement.

The initial finite action set is wait, move, say and habitat condition. Missing
policies wait. An optional habitat mind is an explicit Thoughtform being and
uses the same policy contract; only its own habitat is within its condition
scope. A role name or model response is never sufficient authority.

Verify deterministic repeat episodes, stable call/observation order, rejected
whole-step atomicity, optional/no-mind operation and actual installed examples.
No model provider or orchestration framework is required.

## Persistence and replay — PARA-SAVE-01

Use Backpack typed snapshots and accepted events. Record schema/rules/source
identity, seeds and clocks. Reopen/replay in separate processes with identical
accepted state, and refuse incompatible versions before applying data. Replay
recorded decisions rather than rerunning stochastic inference. Do not create a
new store or serialize executable callables.

## Habitat minds — PARA-MIND-01

After explicit model artifact resolution, add an optional configured policy
adapter for the habitat mind. One habitat and two beings remain the minimum
scenario. Share base models only through serialized/isolated access; identities,
context, memory and authority remain separate. Validate environmental proposals
through world rules exactly like inhabitant proposals.

## Experiences — PARA-EXPERIENCE-01

Export bounded versioned observations, proposals, accepted actions and outcomes
with source/data lineage for selected Hypnosis evaluations or training jobs.
Separate simulated narration from verified outcomes. Select retention, rights
and development/held-out splits explicitly. Experience export does not trigger
model training or promotion.

## Later composition and releases

Collective/whole-world policies may compose through Thoughtform and Hypnosis
without changing the world authority boundary. UI and hub integrations are
optional composition profiles. Keep core headless, Python 3.14+, and independent
of Carets/model packages. Build/install wheel and source on declared platforms.
Public source is authorized; dataset/weight publication, package releases and
service deployment require separately selected concrete operations.
