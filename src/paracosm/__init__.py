"""Deterministic worlds with optional model-neutral habitat minds."""
from .world import Habitat, Resident, Snapshot, Step, World

__all__ = ['Habitat', 'Resident', 'Snapshot', 'Step', 'World']


def main():
    from dataclasses import asdict
    import json
    from thoughtform import Being
    world = World(Snapshot('pluralopia', (Habitat('woods', 'The Woods'),),
        (Resident(Being('alice', 'Alice'), 'woods'), Resident(Being('bob', 'Bob'), 'woods'))))
    print(json.dumps(asdict(world.step({})), ensure_ascii=True, allow_nan=False))
