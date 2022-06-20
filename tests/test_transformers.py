from pathlib import Path
import pytest
from exfor_parserpy import read_exfor
from exfor_parserpy.trafos import unitfy, depointerfy, uncommonfy, detextify


TEST_DATA_DIR = Path(__file__).parent / "testdata"


@pytest.mark.parametrize("file", TEST_DATA_DIR.glob("*.txt"))
def test_unitfy_never_fails(file):
    content = read_exfor(file)
    try:
        unitfy(content)
    except Exception as exc:
        assert False, f"unitfy failed on file {file} with exception {exc}"


@pytest.mark.parametrize("file", TEST_DATA_DIR.glob("*.txt"))
def test_depointerfy_never_fails(file):
    content = read_exfor(file)
    try:
        depointerfy(content)
    except Exception as exc:
        assert False, f"depointerfy failed on file {file} with exception {exc}"


@pytest.mark.parametrize("file", TEST_DATA_DIR.glob("*.txt"))
def test_detextify_never_fails(file):
    content = read_exfor(file)
    try:
        detextify(content)
    except Exception as exc:
        assert False, f"detextify failed on file {file} with exception {exc}"


@pytest.mark.parametrize("file", TEST_DATA_DIR.glob("*.txt"))
def test_uncommonfy_never_fails(file):
    content = read_exfor(file)
    try:
        uncommonfy(content)
    except Exception as exc:
        assert False, f"uncommonfy failed on file {file} with exception {exc}"
