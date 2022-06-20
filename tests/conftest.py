from pathlib import Path


def pytest_addoption(parser):
    parser.addoption("--exfordir", action="store", default="testdata")


def pytest_generate_tests(metafunc):
    exfor_dir = Path(__file__).parent / metafunc.config.option.exfordir
    if "entry_file" in metafunc.fixturenames:
        metafunc.parametrize("entry_file", exfor_dir.glob("*.txt"))
