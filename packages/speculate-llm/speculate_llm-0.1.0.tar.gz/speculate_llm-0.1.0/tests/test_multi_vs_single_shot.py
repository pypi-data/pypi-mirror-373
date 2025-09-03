from speculate import Scenario
from .helpers import FakeProvider

def test_multi_step_chain_passes_when_history_carries():
    provider = FakeProvider(default_multi_shot=True)
    Scenario("multi_step", provider)\
        .set_system_prompt("Answer tersely.")\
        .prompt("Explain why the sky is blue.")\
        .expect_contains("Rayleigh")\
        .prompt("Is that wavelength-dependent?")\
        .expect_contains("yes")\
        .run()
    assert len(provider.calls) == 2
    assert any(m.get("role")=="assistant" and "Rayleigh" in m.get("content","") for m in provider.calls[-1]["history"])

def test_single_shot_ignores_second_step():
    provider = FakeProvider(default_multi_shot=True)
    Scenario("single_shot", provider)\
        .multi_shot(False)\
        .prompt("THIS runs")\
        .expect_contains("THIS")\
        .prompt("THIS will be ignored")\
        .expect_contains("ignored")\
        .run()
    assert len(provider.calls) == 1
