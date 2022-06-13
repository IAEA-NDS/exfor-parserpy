from pathlib import Path
import pytest
from exfor_parserpy import read, write, readfile, writefile
from exfor_parserpy.utils.convenience import compare_dictionaries


TEST_DATA_DIR = Path(__file__).parent / "testdata"


@pytest.mark.parametrize("file", TEST_DATA_DIR.glob("*.txt"))
def test_exforbaseparser_write_and_read_roundtrip_leaves_content_unchanged(file):
    content = readfile(file)
    written = write(content)
    assert compare_dictionaries(content, read(written), rtol=1e-4)


@pytest.mark.parametrize("file", TEST_DATA_DIR.glob("*.txt"))
def test_exforbaseparser_file_writing_and_reading_leaves_content_unchanged(
    file, tmp_path
):
    content = readfile(file)
    written_file = tmp_path / "file.txt"
    writefile(written_file, content)
    assert compare_dictionaries(content, readfile(written_file), rtol=1e-4)
