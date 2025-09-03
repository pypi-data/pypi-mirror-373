from speculate import Scenario
from .helpers import FakeProvider

def test_dump_raw_on_fail_creates_file(tmp_path):
    outdir = tmp_path / "raws"
    provider = FakeProvider()
    Scenario("raw dump fail scenario", provider)\
        .prompt("raw dump fail")\
        .expect_exact("this will not match")\
        .dump_raw(mode="fail", to_dir=str(outdir), file_format="txt")\
        .run()
    files = list(outdir.glob("raw_dump_fail_scenario__run*.txt"))
    assert files
