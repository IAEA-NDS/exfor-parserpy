from pathlib import Path


def pytest_addoption(parser):
    parser.addoption("--exfordir", action="store", default="testdata")
    parser.addoption("--exforfile", action="store", default=None)


def pytest_generate_tests(metafunc):
    exfor_dir = Path(__file__).parent / metafunc.config.option.exfordir
    if "entry_file" in metafunc.fixturenames:
        file_opt = metafunc.config.option.exforfile
        if file_opt is not None:
            entry_files = [exfor_dir / file_opt]
        else:
            entry_files = exfor_dir.glob("*.txt")
        metafunc.parametrize("entry_file", entry_files)
