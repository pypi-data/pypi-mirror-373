# project-name

_______________________________________________________________________________

Project description...

### Create and activate virtual environment.

```commandline
pip install --upgrade pip virtualenv
virtualenv --python=python3.11 .venv
source .venv/bin/activate
```

### Install required libraries.

```commandline
pip install '.[test]'
```

### Check tests and coverage...

```commandline
python manager.py run-tests
python manager.py run-coverage
```
