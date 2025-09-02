# Arkindex CLI

Documentation for users is available in the [docs](./docs) folder, and online as [cli.arkindex.org](https://cli.arkindex.org).

## Dev setup

Requirements:
- Python 3.7+

```console
mkvirtualenv cli
pip install -e .
arkindex -h
```

### Unit tests

Tox is used on this project to run all unit tests:

```console
pip install tox
tox
```

### Linting

We use [pre-commit](https://pre-commit.com/) to check the Python source code syntax of this project.

To avoid superfluous commits, always run pre-commit before committing.

To do that, run once :

```
pip install pre-commit
pre-commit install
```

The linting workflow will now run on modified files before committing, and may fix issues for you.

If you want to run the full workflow on all the files: `pre-commit run -a`.

### Documentation

Please keep the documentation updated when modifying or adding commands.

It's pretty easy to do:

```
npm install
npm antora antora-playbook.yml
```

You can then write in Asciidoc in the relevant `docs/*.adoc` files, and see output on the specified html file.
