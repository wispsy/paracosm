import unittest

from thoughtform import Action, Being
from paracosm import Habitat, Resident, Snapshot, World


class Policy:
    def __init__(self, decide):
        self.decide = decide


def world(mind=False):
    return World(Snapshot('test', (Habitat('woods', 'The Woods', mind=Being('forest', 'Forest', role='environment') if mind else None),
                                   Habitat('village', 'Village')),
        (Resident(Being('bob', 'Bob'), 'woods'), Resident(Being('alice', 'Alice'), 'woods'))))


class WorldTests(unittest.TestCase):
    def test_deterministic_order_snapshot_observations_and_step(self):
        def episode():
            value = world()
            observed = []
            def alice(observation):
                observed.append(observation)
                return Action('alice', 'move', 'village')
            def bob(observation):
                observed.append(observation)
                return Action('bob', 'say', value='hello')
            result = value.step({'bob': Policy(bob), 'alice': Policy(alice)})
            self.assertEqual([o.actor_id for o in observed], ['alice', 'bob'])
            self.assertTrue(all(o.habitat == 'woods' and 'alice' in o.visible for o in observed))
            self.assertEqual(value.snapshot.tick, 1)
            return result
        self.assertEqual(episode(), episode())

    def test_invalid_later_action_preserves_entire_step(self):
        for action in (Action('bob', 'move', 'unknown'), Action('alice', 'wait'),
                       Action('bob', 'condition', 'woods', 'storm'), Action('bob', 'invent')):
            value = world()
            before = value.snapshot
            with self.assertRaises(ValueError):
                value.step({'alice': Policy(lambda o: Action('alice', 'move', 'village')),
                            'bob': Policy(lambda o: action)})
            self.assertIs(value.snapshot, before)
        with self.assertRaises(ValueError):
            world().step({'unknown': Policy(lambda o: Action('unknown', 'wait'))})

    def test_optional_environment_policy_is_bounded_by_world_rules(self):
        value = world(mind=True)
        result = value.step({'forest': Policy(lambda o: Action('forest', 'condition', o.habitat, 'rain'))})
        self.assertEqual(result.snapshot.habitats[0].condition, 'rain')
        before = value.snapshot
        with self.assertRaises(ValueError):
            value.step({'forest': Policy(lambda o: Action('forest', 'condition', 'village', 'rain'))})
        self.assertIs(value.snapshot, before)
        self.assertEqual(world().step({}).snapshot.tick, 1)

    def test_duplicate_actor_unknown_habitat_and_reentrant_policy_are_refused(self):
        with self.assertRaises(ValueError):
            Snapshot('x', (Habitat('woods', 'W'),), (Resident(Being('a', 'A'), 'missing'),))
        with self.assertRaises(ValueError):
            Snapshot('x', (Habitat('woods', 'W', mind=Being('a', 'Mind')),), (Resident(Being('a', 'A'), 'woods'),))
        value = world()
        before = value.snapshot
        with self.assertRaises(RuntimeError):
            value.step({'alice': Policy(lambda o: value.step({}))})
        self.assertIs(value.snapshot, before)
