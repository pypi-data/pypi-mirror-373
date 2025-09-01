# Arkindex worker configuration

Scripts for Arkindex worker configuration

### Development

For development and tests purpose it may be useful to install the project as a editable package with pip.

* Use a virtualenv (e.g. with virtualenvwrapper `mkvirtualenv -a . worker_configuration`)
* Install worker-configuration as a package (e.g. `pip install -e .`)

### Linter

Code syntax is analyzed before submitting the code.\
To run the linter tools suite you may use pre-commit.

```shell
pip install pre-commit
pre-commit run -a
```

### Run tests

Tests are executed with `tox` using [pytest](https://pytest.org).

```shell
pip install tox
tox
```

To recreate tox virtual environment (e.g. a dependencies update), you may run `tox -r`.

Run a single test module: `tox -- <test_path>`
Run a single test: `tox -- <test_path>::<test_function>`
