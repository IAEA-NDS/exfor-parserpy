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


@pytest.mark.parametrize("file", TEST_DATA_DIR.glob("*.txt"))
def test_exforbaseparser_file_writing_and_reading_leaves_content_unchanged(
    file, tmp_path
):
    parser = ExforBaseParser()
    content = parser.readfile(file)
    written_file = tmp_path / "file.txt"
    parser.writefile(written_file, content)
    assert compare_dictionaries(content, parser.readfile(written_file), rtol=1e-4)
