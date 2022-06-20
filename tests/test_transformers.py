from pathlib import Path
import pytest
from exfor_parserpy import read_exfor
from exfor_parserpy.trafos import unitfy


TEST_DATA_DIR = Path(__file__).parent / "testdata"


@pytest.mark.parametrize("file", TEST_DATA_DIR.glob("*.txt"))
def test_unitfy_never_fails(file):
    content = read_exfor(file)
    try:
        unitfy(content)
    except Exception as exc:
        assert False, f"unitfy failed on file {file} with exception {exc}"
