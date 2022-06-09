import os
from exfor_parserpy import ExforBaseParser
from exfor_parserpy.utils.convenience import compare_dictionaries


def test_bijection():
    """Test parsed equals parsed/written/parsed entries."""
    exfor_path = 'testdata/alldata'
    #exfor_path = "testdata"
    exfor_files = os.listdir(exfor_path)
    exfor_files = [f for f in exfor_files if f.endswith(".txt")]
    exfor_paths = [os.path.join(exfor_path, f) for f in exfor_files]
    parser = ExforBaseParser()
    problem_files = []
    for curpath in exfor_paths:
        exfor_dic1 = parser.readfile(curpath)
        exfor_text = parser.write(exfor_dic1)
        exfor_dic2 = parser.read(exfor_text)
        if not compare_dictionaries(exfor_dic1, exfor_dic2, rtol=1e-4):
            problem_files.append(curpath)
            if len(problem_files) > 5:
                break
    assert len(problem_files) == 0, "errors for:\n{}".format("\n".join(problem_files))
