# Build & upload djimporter package to pypi

Steps to build and upload new djimporter package to [pypi](https://pypi.org/project/djimporter/)

## Create new package
Reference: https://packaging.python.org/en/latest/tutorials/packaging-projects/

1. Install required packages:
```bash
python3 -m pip install --upgrade build twine
```

2. Build & upload package
```bash
# build package (see dist/)
python3 -m build

# upload to test.pypi.org
python3 -m twine upload --repository test-djimporter dist/*

# upload to pypi.org
python3 -m twine upload --repository djimporter dist/*
```

## Test that package works properly:

```bash
deactivate
export VENV_DIR=/tmp/zxc
rm -r $VENV_DIR

python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# a) install from test.pypi.org (testing env)
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps djimporter==0.6

# b) install from pypi.org
python3 -m pip install djimporter==0.6

python3 -c "import djimporter; print(djimporter.get_version())"
```
