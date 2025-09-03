class FakeProvider:
    def __init__(self, default_multi_shot: bool = True):
        self.default_multi_shot = default_multi_shot
        self.calls = []
        self.seeds = []

    def generate(self, prompt, system_prompt=None, history=None, seed=None, **kwargs):
        self.calls.append({"prompt": prompt, "system_prompt": system_prompt, "history": history, "seed": seed})
        self.seeds.append(seed)
        if "Return greeting='Hello' and name='Donavan'." in prompt:
            return '```json\n{"greeting":"Hello","name":"Donavan"}\n```'
        if "Say hello to Donavan" in prompt:
            return "Hello Donavan!"
        if "Explain why the sky is blue." in prompt:
            return "Short: Rayleigh scattering dominates."
        if "Is that wavelength-dependent?" in prompt:
            if history and any(m.get("role")=="assistant" and "Rayleigh" in m.get("content","") for m in history):
                return "yes"
            return "no"
        if "THIS runs" in prompt:
            return "THIS indeed runs"
        if "THIS will be ignored" in prompt:
            return "ignored"
        if "alpha number please" in prompt:
            return "alpha 123"
        if "raw dump fail" in prompt:
            return "some output that will not match"
        return "ok"

class FlakyProvider(FakeProvider):
    def __init__(self, fail_on_call: int = 3, **kwargs):
        super().__init__(**kwargs)
        self._counter = 0
        self._fail_on = fail_on_call

    def generate(self, *args, **kwargs):
        self._counter += 1
        return "pass" if self._counter != self._fail_on else "fail"
