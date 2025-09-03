from pydantic import BaseModel
from speculate import Scenario
from .helpers import FakeProvider

class GreetingResponse(BaseModel):
    greeting: str
    name: str

def test_expectations_pass():
    provider = FakeProvider()
    Scenario("exact", provider).prompt("Say hello to Donavan in one short sentence.").expect_exact("Hello Donavan!").run()
    Scenario("contains", provider).prompt("Say hello to Donavan in one short sentence.").expect_contains("Donavan").run()
    Scenario("not_equal", provider).prompt("Say hello to Donavan in one short sentence.").expect_not_equal("Something else").run()
    Scenario("not_contains", provider).prompt("Say hello to Donavan in one short sentence.").expect_not_contains("error").run()
    Scenario("regex", provider).prompt("alpha number please").expect_regex(r"\d+").run()

def test_schema_validation_with_fenced_json():
    provider = FakeProvider()
    Scenario("schema", provider)\
        .set_system_prompt("Always respond in JSON.")\
        .prompt("Return greeting='Hello' and name='Donavan'.")\
        .expect_schema(GreetingResponse, greeting="Hello", name="Donavan")\
        .run()
