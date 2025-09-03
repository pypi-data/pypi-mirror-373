# scenarios/greeting_test.py
from speculate import Scenario
from speculate.providers.ollama_provider import OllamaProvider
from models.example_model import GreetingResponse

# Provider with a default seed (all scenarios inherit unless overridden)
provider = OllamaProvider(model="gpt-oss:20b", temperature=0.5, default_multi_shot=True)

# JSON schema validation
Scenario("test_json_greeting", provider)\
    .set_system_prompt("Always respond in JSON.")\
    .prompt("Return greeting='Hello' and name='Donavan'.")\
    .expect_schema(GreetingResponse, greeting="Hello", name="Donavan")\
    .runs(3)\
    .require_accuracy(0.9)\
    .dump_raw(mode="fail", to_dir="raw_outputs", file_format="json")\
    .run()

# Contains expectation, random seed per run
Scenario("test_contains_name", provider)\
    .randomize_seed(True)\
    .prompt("Say hello to Donavan in one short sentence.")\
    .expect_contains("Donavan")\
    .runs(5)\
    .run()

# Multi-step chained prompts
Scenario("test_multi_step", provider)\
    .set_system_prompt("Answer tersely.")\
    .prompt("Explain why the sky is blue.")\
    .expect_contains("Rayleigh")\
    .prompt("Is that wavelength-dependent?")\
    .expect_contains("yes")\
    .runs(2)\
    .run()

# Single-shot: ignores second step
Scenario("test_single_shot", provider)\
    .multi_shot(False)\
    .prompt("THIS runs")\
    .expect_contains("THIS")\
    .prompt("THIS will be ignored")\
    .expect_contains("ignored")\
    .runs(3)\
    .run()