import sys
import pathlib
import pytest

@pytest.fixture(autouse=True, scope="session")
def _add_repo_root_to_syspath():
    tests_path = pathlib.Path(__file__).resolve().parent
    repo_root = tests_path.parent
    sys.path.insert(0, str(repo_root))
    yield

@pytest.fixture(autouse=True)
def _reset_results():
    try:
        from speculate import RESULTS
        RESULTS.clear()
    except Exception:
        pass
    yield
    try:
        from speculate import RESULTS
        RESULTS.clear()
    except Exception:
        pass
