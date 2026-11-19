"""Authoritative deterministic world steps; policies only propose actions."""
from dataclasses import dataclass, replace

from thoughtform import Action, Being, Observation
from thoughtform.contracts import identifier, text


@dataclass(frozen=True)
class Habitat:
    habitat_id: str
    name: str
    condition: str = 'calm'
    mind: Being | None = None

    def __post_init__(self):
        identifier(self.habitat_id, 'Habitat ID')
        text(self.name, 'Habitat name', 256)
        text(self.condition, 'Condition')
        if self.mind is not None and type(self.mind) is not Being:
            raise TypeError('Habitat mind requires a Being')


@dataclass(frozen=True)
class Resident:
    being: Being
    habitat_id: str

    def __post_init__(self):
        if type(self.being) is not Being:
            raise TypeError('Resident requires a Being')
        identifier(self.habitat_id, 'Habitat ID')


@dataclass(frozen=True)
class Snapshot:
    world_id: str
    habitats: tuple[Habitat, ...]
    residents: tuple[Resident, ...]
    tick: int = 0

    def __post_init__(self):
        identifier(self.world_id, 'World ID')
        if type(self.tick) is not int or not 0 <= self.tick < 2**53 - 1:
            raise ValueError('Tick is outside its portable range')
        if type(self.habitats) is not tuple or not 1 <= len(self.habitats) <= 32 or any(type(h) is not Habitat for h in self.habitats):
            raise ValueError('World requires 1–32 immutable habitats')
        if type(self.residents) is not tuple or len(self.residents) > 128 or any(type(r) is not Resident for r in self.residents):
            raise ValueError('World requires at most 128 immutable residents')
        habitat_ids = {h.habitat_id for h in self.habitats}
        if len(habitat_ids) != len(self.habitats):
            raise ValueError('Habitat IDs must be unique')
        actors = [r.being.being_id for r in self.residents] + [h.mind.being_id for h in self.habitats if h.mind is not None]
        if len(actors) != len(set(actors)) or len(actors) > 128:
            raise ValueError('Actor IDs must be unique and bounded')
        if any(r.habitat_id not in habitat_ids for r in self.residents):
            raise ValueError('Residents require known habitats')


@dataclass(frozen=True)
class Step:
    snapshot: Snapshot
    actions: tuple[Action, ...]


class World:
    """A single owner; policy code is trusted but proposals have no authority."""
    def __init__(self, snapshot):
        if type(snapshot) is not Snapshot:
            raise TypeError('World requires Snapshot')
        self._snapshot = snapshot
        self._stepping = False

    @property
    def snapshot(self):
        return self._snapshot

    def step(self, policies):
        if self._stepping:
            raise RuntimeError('World steps cannot be reentered')
        self._stepping = True
        try:
            result = self._step(dict(policies))
            self._snapshot = result.snapshot
            return result
        finally:
            self._stepping = False

    def _step(self, policies):
        before = self.snapshot
        locations = {r.being.being_id: r.habitat_id for r in before.residents}
        minds = {h.mind.being_id: h.habitat_id for h in before.habitats if h.mind is not None}
        locations.update(minds)
        if set(policies) - set(locations):
            raise ValueError('Policies contain unknown actors')
        habitats = {h.habitat_id: h for h in before.habitats}
        actions = []
        for actor_id in sorted(locations):
            habitat_id = locations[actor_id]
            visible = (f'condition:{habitats[habitat_id].condition}',) + tuple(sorted(
                r.being.being_id for r in before.residents if r.habitat_id == habitat_id))
            observation = Observation(actor_id, before.tick, habitat_id, visible)
            action = policies[actor_id].decide(observation) if actor_id in policies else Action(actor_id, 'wait')
            if type(action) is not Action or action.actor_id != actor_id:
                raise ValueError('Policy must propose an action for its own actor')
            if action.kind == 'wait':
                if action.target is not None or action.value is not None:
                    raise ValueError('Wait takes no target or value')
            elif action.kind == 'move':
                if actor_id in minds or action.target not in habitats or action.value is not None:
                    raise ValueError('Move requires a resident and known destination')
            elif action.kind == 'say':
                if action.target is not None or action.value is None:
                    raise ValueError('Say requires text and no target')
            elif action.kind == 'condition':
                if minds.get(actor_id) != action.target or action.value is None:
                    raise ValueError('Only a habitat mind can propose its own condition')
            else:
                raise ValueError('Unsupported world action')
            actions.append(action)
        # Validate every proposal against the same snapshot before committing.
        residents = {r.being.being_id: r for r in before.residents}
        for action in actions:
            if action.kind == 'move':
                residents[action.actor_id] = replace(residents[action.actor_id], habitat_id=action.target)
            elif action.kind == 'condition':
                habitats[action.target] = replace(habitats[action.target], condition=action.value)
        after = replace(before, tick=before.tick + 1,
                        habitats=tuple(habitats[h.habitat_id] for h in before.habitats),
                        residents=tuple(residents[r.being.being_id] for r in before.residents))
        return Step(after, tuple(actions))
