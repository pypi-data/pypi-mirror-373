from __future__ import annotations

import argparse
import os
import pathlib
import sys
import types
from typing import List, Optional, Tuple

# --- import from package
from .core import RESULTS, print_summary  # ensures package import works

UTF32_BOMS = (b"\x00\x00\xfe\xff", b"\xff\xfe\x00\x00")
UTF16_BOMS = (b"\xff\xfe", b"\xfe\xff")

def _read_source_text(path: pathlib.Path) -> str:
    data = path.read_bytes()
    if data.startswith(UTF32_BOMS):
        return data.decode("utf-32")
    if data.startswith(UTF16_BOMS):
        return data.decode("utf-16")
    if b"\x00" in data:
        try:
            return data.decode("utf-16")
        except Exception:
            return data.decode("utf-32")
    return data.decode("utf-8-sig")

def _exec_scenario_file(module_path: pathlib.Path, module_name: str) -> None:
    src = _read_source_text(module_path)
    code = compile(src, str(module_path), "exec")
    mod = types.ModuleType(module_name)
    mod.__file__ = str(module_path)
    sys.modules[module_name] = mod
    exec(code, mod.__dict__)

def _iter_scenario_files(base: pathlib.Path, pattern: str) -> List[pathlib.Path]:
    if base.is_file():
        return [base]
    return [f for f in sorted(base.glob(pattern)) if f.is_file() and f.name != "__init__.py" and not f.name.startswith(".")]

def _apply_env_overrides(args: argparse.Namespace) -> None:
    if args.runs is not None:
        os.environ["LLM_RUNS_PER_TEST"] = str(args.runs)
    if args.accuracy is not None:
        os.environ["LLM_ACCURACY_THRESHOLD"] = str(args.accuracy)
    if args.raw_dump is not None:
        os.environ["LLM_RAW_DUMP"] = args.raw_dump
    if args.raw_dir is not None:
        os.environ["LLM_RAW_DUMP_DIR"] = str(args.raw_dir)
    if args.base_url is not None:
        os.environ["OLLAMA_BASE_URL"] = args.base_url
    if args.api_style is not None:
        os.environ["OLLAMA_API_STYLE"] = args.api_style
    if args.timeout is not None:
        os.environ["OLLAMA_TIMEOUT_S"] = str(args.timeout)
    if args.default_seed is not None:
        os.environ["LLM_DEFAULT_SEED"] = str(args.default_seed)

def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="speculate", description="Run BDD-style LLM scenarios")
    p.add_argument("path", help="Path to a scenario .py file or a directory of scenarios")
    p.add_argument("--pattern", default="**/*.py", help="Glob when PATH is a directory (default: **/*.py)")
    # suite defaults
    p.add_argument("--runs", type=int, help="Override runs per test for the suite")
    p.add_argument("--accuracy", type=float, help="Required accuracy threshold (0..1)")
    p.add_argument("--raw-dump", choices=["never","fail","always"], help="Dump raw LLM output")
    p.add_argument("--raw-dir", help="Directory to write raw outputs")
    # provider env
    p.add_argument("--base-url", help="OLLAMA_BASE_URL")
    p.add_argument("--api-style", choices=["","chat","generate","openai"], help="OLLAMA_API_STYLE")
    p.add_argument("--timeout", type=float, help="OLLAMA_TIMEOUT_S")
    p.add_argument("--default-seed", type=int, help="LLM_DEFAULT_SEED")
    # behavior
    p.add_argument("--no-summary", action="store_true", help="Do not print suite summary")
    p.add_argument("--fail-fast", action="store_true", help="Stop on first import error")
    return p.parse_args(argv)

def _run(files: List[pathlib.Path], fail_fast: bool) -> Tuple[int, int]:
    failures = 0
    count = 0
    for idx, f in enumerate(files, 1):
        name = f"speculate_user_scenarios_{idx}"
        try:
            _exec_scenario_file(f, name)
            count += 1
        except SystemExit as se:
            if int(se.code or 0) != 0:
                failures += 1
                print(f"[FAIL] {f}: exited with code {se.code}", file=sys.stderr)
                if fail_fast: break
        except Exception as e:
            failures += 1
            print(f"[FAIL] {f}: {e}", file=sys.stderr)
            if fail_fast: break
    return failures, count

def main(argv: Optional[List[str]] = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    base = pathlib.Path(args.path).resolve()
    files = _iter_scenario_files(base, args.pattern)
    _apply_env_overrides(args)

    import_failures, files_run = _run(files, args.fail_fast)

    failed_scenarios = sum(1 for r in RESULTS if r.get("failed"))
    total_scenarios = len(RESULTS)

    if not args.no_summary:
        print()
        print_summary()

    if import_failures or failed_scenarios:
        print(
            f"\n[speculate] status: FAIL  | imports_failed={import_failures}  "
            f"scenarios_failed={failed_scenarios}  scenarios_total={total_scenarios}  files_run={files_run}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"\n[speculate] status: PASS  | imports_failed=0  scenarios_failed=0  "
        f"scenarios_total={total_scenarios}  files_run={files_run}"
    )
    sys.exit(0)
