from pathlib import Path
import pytest
from exfor_parserpy import ExforBaseParser
from exfor_parserpy.utils.convenience import compare_dictionaries


TEST_DATA_DIR = Path(__file__).parent / "testdata"


@pytest.mark.parametrize("file", TEST_DATA_DIR.glob("*.txt"))
def test_exforbaseparser_write_and_read_roundtrip_leaves_content_unchanged(file):
    parser = ExforBaseParser()
    content = parser.readfile(file)
    written = parser.write(content)
    assert compare_dictionaries(content, parser.read(written), rtol=1e-4)
