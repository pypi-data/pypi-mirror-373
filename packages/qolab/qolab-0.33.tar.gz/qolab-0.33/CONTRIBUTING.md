# Developers guide

Contributions are welcome.

## Running automatic checks

Make sure that `tox` command reports no issues after code
modification.

If you want to run some checks manually see below.

## Formatting

Adhere to [black](https://pypi.org/project/black/)
formatting style and run modified files via `black`. 
I.e. do `black fname` or even more extreme
~~~~~
black .
~~~~~
to reformat the whole project.

## Linting

I find [flake8](https://github.com/PyCQA/flake8/tree/main)
to be quite good linter.

Make sure that you check for linting errors all the files
and review the messages.
Before committing and especially pushing, run
~~~~~
flake8 --max-line-length=88
~~~~~
here we set maximum line length to `black` default, which
is a bit longer `python` recommended 79.

## Test instructions

Make sure that you run the test suite and no errors are triggered.

If you have `tox` installed, just run

~~~~~
# mostlikely qolab_pytest is the default tox enviroment so just tox is sufficient
tox
# if you want fine grained contrlo
tox -e qolab_pytest
~~~~~

There is a way to do it manually, but all `qolab` dependencies must
be already installed either globally or in a virtual environment.

~~~~~
export PYTHONPATH=.
python -m pytest 
~~~~~

Note that we cannot just run `pytest` since I see no way to set the module search path.

