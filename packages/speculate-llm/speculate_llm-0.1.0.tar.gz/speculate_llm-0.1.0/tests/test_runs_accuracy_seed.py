import random
from speculate import Scenario, RESULTS
from .helpers import FakeProvider, FlakyProvider

def test_runs_and_accuracy_threshold_fails_below_required():
    provider = FlakyProvider(fail_on_call=3)
    Scenario("threshold", provider)\
        .prompt("any")\
        .expect_exact("pass")\
        .runs(3)\
        .require_accuracy(1.0)\
        .run()
    r = next((x for x in RESULTS if x["name"] == "threshold"), None)
    assert r and r["passes"] == 2 and r["failed"]

def test_randomize_seed_uses_different_seeds(monkeypatch):
    provider = FakeProvider()
    seq = iter([111, 222, 333])
    monkeypatch.setattr(random, "randint", lambda a, b: next(seq))

    Scenario("random_seeds", provider)\
        .randomize_seed(True)\
        .prompt("any")\
        .expect_contains("ok")\
        .runs(3)\
        .run()

    assert provider.seeds == [111, 222, 333]

def test_fixed_seed_overrides_provider_default():
    provider = FakeProvider()
    Scenario("fixed_seed", provider)\
        .seed(42)\
        .prompt("any")\
        .expect_contains("ok")\
        .run()
    assert provider.seeds == [42]
