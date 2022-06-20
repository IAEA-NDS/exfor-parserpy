from pathlib import Path
import pytest
from exfor_parserpy import read_exfor
from exfor_parserpy.trafos import unitfy, depointerfy, uncommonfy, detextify


def test_unitfy_never_fails(entry_file):
    content = read_exfor(entry_file)
    try:
        unitfy(content)
    except Exception as exc:
        assert False, f"unitfy failed on file {file} with exception {exc}"


def test_depointerfy_never_fails(entry_file):
    content = read_exfor(entry_file)
    try:
        depointerfy(content)
    except Exception as exc:
        assert False, f"depointerfy failed on file {file} with exception {exc}"


def test_detextify_never_fails(entry_file):
    content = read_exfor(entry_file)
    try:
        detextify(content)
    except Exception as exc:
        assert False, f"detextify failed on file {file} with exception {exc}"


def test_uncommonfy_never_fails(entry_file):
    content = read_exfor(entry_file)
    try:
        uncommonfy(content)
    except Exception as exc:
        assert False, f"uncommonfy failed on file {file} with exception {exc}"
