from pathlib import Path
import pytest
from exfor_parserpy import read_exfor
from exfor_parserpy.trafos import (
    unitfy,
    depointerfy,
    uncommonfy,
    detextify,
    tablify,
    reactify,
)


def test_unitfy_never_fails(entry_file):
    content = read_exfor(entry_file)
    try:
        unitfy(content)
    except Exception as exc:
        assert False, f"unitfy failed on file {entry_file} with exception {exc}"


def test_depointerfy_never_fails(entry_file):
    content = read_exfor(entry_file)
    try:
        depointerfy(content)
    except Exception as exc:
        assert False, f"depointerfy failed on file {entry_file} with exception {exc}"


def test_detextify_never_fails(entry_file):
    content = read_exfor(entry_file)
    try:
        detextify(content)
    except Exception as exc:
        assert False, f"detextify failed on file {entry_file} with exception {exc}"


def test_uncommonfy_never_fails(entry_file):
    content = read_exfor(entry_file)
    try:
        uncommonfy(content)
    except Exception as exc:
        assert False, f"uncommonfy failed on file {entry_file} with exception {exc}"


def test_tablify_never_fails(entry_file):
    content = read_exfor(entry_file)
    entryid = tuple(content.keys())[0]
    if len(content[entryid]) == 1 and tuple(content[entryid].keys())[0].endswith("001"):
        # if there is only the first subentry present,
        # tablify is expected to fail
        assert True
        return
    try:
        tablify(content)
    except Exception as exc:
        assert False, f"tablify failed on file {entry_file} with exception {exc}"


def test_reactify_never_fails(entry_file):
    content = read_exfor(entry_file)
    try:
        reactify(content)
    except Exception as exc:
        assert False, f"reactify failed on file {entry_file} with exception {exc}"
