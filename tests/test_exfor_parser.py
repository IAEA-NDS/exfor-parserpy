from pathlib import Path
import pytest
from exfor_parserpy import from_exfor, to_exfor, read_exfor, write_exfor
from exfor_parserpy.utils.comparison_utils import compare_dictionaries


def test_exforbaseparser_write_and_read_roundtrip_leaves_content_unchanged(entry_file):
    content = read_exfor(entry_file)
    written = to_exfor(content)
    assert compare_dictionaries(content, from_exfor(written), rtol=1e-4)


def test_exforbaseparser_file_writing_and_reading_leaves_content_unchanged(
    entry_file, tmp_path
):
    content = read_exfor(entry_file)
    written_file = tmp_path / "file.txt"
    write_exfor(written_file, content)
    assert compare_dictionaries(content, read_exfor(written_file), rtol=1e-4)
