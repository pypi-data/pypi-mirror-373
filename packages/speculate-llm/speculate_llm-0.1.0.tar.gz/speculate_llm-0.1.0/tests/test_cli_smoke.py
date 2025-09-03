from speculate.cli import main as cli_main

def test_cli_runs_simple_scenario(tmp_path):
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir(parents=True, exist_ok=True)

    scenario_code = '''from speculate import Scenario
class P:
    default_multi_shot = True
    def generate(self, prompt, system_prompt=None, history=None, seed=None, **kwargs):
        return "ok"
provider = P()
Scenario("cli_smoke", provider).prompt("hi").expect_contains("ok").run()
'''
    f = scenarios_dir / "cli_smoke_test.py"
    f.write_text(scenario_code, encoding="utf-8")

    try:
        cli_main([str(scenarios_dir), "--no-summary"])
    except SystemExit as se:
        assert int(se.code or 0) == 0
