# providers/ollama_provider.py
from __future__ import annotations

import os
import requests
from typing import Optional, List, Dict, Any


class OllamaProvider:
    """
    Ollama provider with:
      • Endpoint fallback: tries /api/chat, falls back to /api/generate on 404
      • Provider-level defaults: temperature, seed, timeout, multi-shot preference
      • Scenario-level overrides: `seed` can override provider default

    Env vars:
      OLLAMA_BASE_URL      (default: http://host.docker.internal:11434)
      OLLAMA_API_STYLE     (auto|"" [default], "chat", "generate", "openai")
      OLLAMA_TIMEOUT_S     (default: 120)
      LLM_DEFAULT_SEED     (optional int; overrides ctor seed if provided)
    """

    def __init__(
        self,
        model: str = "mistral",
        base_url: Optional[str] = None,
        temperature: float = 0.0,
        seed: Optional[int] = None,
        timeout_s: Optional[float] = None,
        default_multi_shot: bool = True,
        multi_shot: Optional[bool] = None,  # alias for default_multi_shot
    ):
        self.model = model
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")).rstrip("/")
        self.temperature = temperature

        # provider-level default seed (scenario can override)
        env_seed = os.getenv("LLM_DEFAULT_SEED")
        self.seed: Optional[int] = int(env_seed) if (env_seed is not None and env_seed != "") else seed

        # timeout
        self.timeout_s = float(os.getenv("OLLAMA_TIMEOUT_S", str(timeout_s if timeout_s is not None else 120)))

        # style: "", "chat", "generate", "openai" (auto by default)
        self.api_style = os.getenv("OLLAMA_API_STYLE", "").strip().lower()

        # scenarios can read this to decide their default
        if multi_shot is not None:
            self.default_multi_shot = bool(multi_shot)
        else:
            self.default_multi_shot = bool(default_multi_shot)

    # --------------------------------------------------------------------- utils
    def _make_options(self, eff_seed: Optional[int], **kwargs: Any) -> Dict[str, Any]:
        """Merge temperature/seed with any extra sampler options."""
        opts: Dict[str, Any] = {"temperature": kwargs.get("temperature", self.temperature)}
        if eff_seed is not None:
            opts["seed"] = int(eff_seed)
        # Allow pass-through of some common sampler controls if provided
        for k in ("top_p", "top_k", "repeat_penalty", "mirostat", "mirostat_eta", "mirostat_tau"):
            if k in kwargs and kwargs[k] is not None:
                opts[k] = kwargs[k]
        # Allow arbitrary extra options via `options_extra` dict
        if "options_extra" in kwargs and isinstance(kwargs["options_extra"], dict):
            opts.update(kwargs["options_extra"])
        return opts

    def _post(self, path: str, json_body: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url}{path}"
        return requests.post(url, json=json_body, timeout=self.timeout_s)

    def _flatten_chat_to_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str],
        history: Optional[List[Dict[str, str]]],
    ) -> str:
        """Create a single prompt suitable for /api/generate from chat turns."""
        parts: List[str] = []
        if system_prompt:
            parts.append(f"System: {system_prompt}\n")
        if history:
            for m in history:
                role = m.get("role", "user")
                content = m.get("content", "")
                role_title = "Assistant" if role == "assistant" else "User"
                parts.append(f"{role_title}: {content}\n")
        parts.append(f"User: {prompt}\nAssistant:")
        return "\n".join(parts)

    # ------------------------------------------------------------- API endpoints
    def _call_chat(
        self,
        prompt: str,
        system_prompt: Optional[str],
        history: Optional[List[Dict[str, str]]],
        eff_seed: Optional[int],
        **kwargs: Any,
    ) -> Optional[str]:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": self._make_options(eff_seed, **kwargs),
        }
        fmt = kwargs.get("format") or kwargs.get("response_format")
        if fmt:
            payload["format"] = fmt

        r = self._post("/api/chat", payload)
        if r.status_code == 404:
            return None  # endpoint not supported; signal fallback
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and isinstance(data.get("message"), dict):
            return str(data["message"].get("content", "")).strip()
        return str(data).strip()

    def _call_generate(
        self,
        prompt: str,
        system_prompt: Optional[str],
        history: Optional[List[Dict[str, str]]],
        eff_seed: Optional[int],
        **kwargs: Any,
    ) -> str:
        flat_prompt = self._flatten_chat_to_prompt(prompt, system_prompt, history)
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": flat_prompt,
            "stream": False,
            "options": self._make_options(eff_seed, **kwargs),
        }
        fmt = kwargs.get("format") or kwargs.get("response_format")
        if fmt:
            payload["format"] = fmt

        r = self._post("/api/generate", payload)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "response" in data:
            return str(data["response"]).strip()
        return str(data).strip()

    # ----------------------------------------------------------------- public IO
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        seed: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate text from Ollama.
          - If `seed` is provided, it overrides the provider default seed.
          - `history` should be a list of {"role": "...", "content": "..."} messages
            (use None for a fresh single-shot call).
          - Extra sampler options may be provided via kwargs (e.g., top_p, top_k, options_extra dict, format="json").
        """
        eff_seed = seed if seed is not None else self.seed
        style = self.api_style

        if style == "chat":
            res = self._call_chat(prompt, system_prompt, history, eff_seed, **kwargs)
            if res is None:
                raise RuntimeError("OLLAMA_API_STYLE=chat set, but /api/chat is not available on this Ollama (404).")
            return res

        if style == "generate":
            return self._call_generate(prompt, system_prompt, history, eff_seed, **kwargs)

        if style == "openai":
            res = self._call_chat(prompt, system_prompt, history, eff_seed, **kwargs)
            if res is not None:
                return res
            return self._call_generate(prompt, system_prompt, history, eff_seed, **kwargs)

        # Auto: try chat; if missing, fallback to generate
        res = self._call_chat(prompt, system_prompt, history, eff_seed, **kwargs)
        if res is not None:
            return res
        return self._call_generate(prompt, system_prompt, history, eff_seed, **kwargs)
