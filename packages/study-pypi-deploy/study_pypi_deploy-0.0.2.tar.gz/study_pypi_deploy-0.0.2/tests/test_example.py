import sys

sys.path.append('./src')

def test_add_one():
    for p in sys.path:
        print(p)
    from study_pypi_deploy.example import add_one
    assert add_one(1) == 2