# LLM Test Framework — Extended Examples & Explanations

This document provides **in-depth examples** for using the framework, covering both **provider-level options** and **scenario-level options**.

---

## 🔌 Provider: `OllamaProvider`

The `OllamaProvider` handles communication with Ollama. It supports **/api/chat** with fallback to **/api/generate**.

### Constructor

```python
provider = OllamaProvider(
    model="mistral",
    base_url="http://host.docker.internal:11434",  # default if omitted
    temperature=0.7,            # sampling temperature (0 = deterministic)
    seed=42,                    # provider default seed (overridable in scenarios)
    timeout_s=60.0,             # request timeout (default 120)
    default_multi_shot=True,    # default conversation chaining behavior
    # alias: multi_shot=False    # disables chaining by default for all scenarios
)
```

### Notes

- **model**: Must be pulled in Ollama (`ollama run modelname`) before use.
- **temperature**: Set 0 for reproducible completions. Higher = more randomness.
- **seed**: Fix provider-level seed; scenarios can override or randomize.
- **multi_shot**: Provider-wide default for whether runs carry conversation history.

### Extra Options

You can pass additional sampling parameters when calling `generate`:

```python
provider.generate(
    "Some prompt",
    top_p=0.9,
    top_k=40,
    repeat_penalty=1.1,
    options_extra={"stop": ["END"]}
)
```

---

## 🧪 Scenario: `Scenario`

A `Scenario` defines one or more **steps**. Each step is a `.prompt()` + `.expect_*()` pair.

### Basic Example

```python
from core import Scenario
from providers.ollama_provider import OllamaProvider

provider = OllamaProvider(model="mistral")

Scenario("simple_test", provider)\
    .set_system_prompt("You are a helpful assistant.")\
    .prompt("Say hello to Donavan")\
    .expect_contains("Donavan")\
    .run()
```

### Multi-Step Example

```python
Scenario("multi_step_example", provider)\
    .set_system_prompt("Answer concisely.")\
    .prompt("Summarize: The Earth orbits the Sun.")\
    .expect_contains("Sun")\
    .prompt("Is this heliocentric?")\
    .expect_contains("yes")\
    .runs(2)\
    .run()
```

- With `multi_shot(True)` (default): both steps chain in one run.
- With `multi_shot(False)`: only the first step executes per run.

### Control Methods

- `.runs(N)` → repeat scenario N times.  
- `.require_accuracy(0.8)` → require ≥ 80% passes.  
- `.multi_shot(False)` → disable conversation chaining.  
- `.seed(1234)` → fix seed for all runs in this scenario.  
- `.randomize_seed(True)` → new random seed each run.  
- `.dump_raw(mode="fail", to_dir="raw_outputs", file_format="json")` → capture raw LLM outputs.

### Expectation Types

- `.expect_exact("Hello")` → strict match.  
- `.expect_contains("Donavan")` → substring.  
- `.expect_regex(r"Hello, .*!")` → regex.  
- `.expect_schema(Model, field=value)` → parse/validate JSON with Pydantic.

### Example with Schema Validation

```python
from models.greeting import GreetingResponse

Scenario("json_schema_example", provider)\
    .set_system_prompt("Always output valid JSON.")\
    .prompt("Output greeting='Hi' and name='Alice'.")\
    .expect_schema(GreetingResponse, greeting="Hi", name="Alice")\
    .runs(3)\
    .require_accuracy(1.0)\
    .dump_raw("fail", "outputs", "json")\
    .run()
```

---

## 🎛 Combining Options

```python
Scenario("combined_options", provider)\
    .randomize_seed(True)\
    .multi_shot(False)\
    .runs(5)\
    .require_accuracy(0.6)\
    .prompt("Say hi")\
    .expect_contains("hi")\
    .run()
```

- Each run uses a fresh random seed.  
- Single-shot (no history).  
- Passes if ≥ 60% of runs contain `"hi"`.

---

## 📊 Example Output

```
Scenario: json_schema_example
Mode: multi-shot
Seed: random per-run

┏━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Run ┃ Result┃ Seed   ┃ Details                     ┃
┡━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
┃ 1   ┃ PASS  ┃  98765 ┃ OK (1 step)                 ┃
┃ 2   ┃ FAIL  ┃ 123456 ┃ Step 1 failed: Expected Hi  ┃
└─────┴───────┴────────┴─────────────────────────────┘

Summary: 1/2 passes ██████████░░░░░░░░  50.0%  (threshold 1.00)
✖ Some runs failed.
```

---

## 📝 Tips

- For **deterministic tests**: use `.seed(N)` and `temperature=0`.  
- For **stability checks**: use `.randomize_seed(True)` + `.runs(N)`.  
- Use `.given("context")` to seed history before the first prompt.  
- Chain multiple `.prompt().expect_*()` for scenario flows.  
- Export suite results from `RESULTS` in `core.py` for CI/CD.

---

## 📜 License

MIT License © 2025
