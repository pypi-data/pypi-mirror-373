# Say Hello!

<p align="center">
  <img src="https://cdn.charly-ginevra.fr/say-hello-sample-library/logo.png" width="250" alt="Say Hello! Logo" />
</p>
<p align="center">Python Package Template using UV</p>
<p align="center">
  <a href="https://www.python.org/" target="_blank"><img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff" alt="Python" /></a>
  <a href="https://pypi.org/" target="_blank"><img src="https://img.shields.io/badge/PyPI-3775A9?logo=pypi&logoColor=fff" alt="PyPi" /></a>
  <a href="https://docs.astral.sh/uv/" target="_blank"><img src="https://img.shields.io/badge/UV-25122f?logo=uv&logoColor=DE5FE9" alt="UV" /></a>
  <a href="https://docs.pytest.org/en/stable/" target="_blank"><img src="https://img.shields.io/badge/pytest-000000?logo=pytest&logoColor=0A9EDC" alt="PyTest" /></a>
</p>

## Getting Started

1. You need to have UV installed. You can find instructions [here](https://docs.astral.sh/uv/getting-started/installation/).

2. Create the virtual environment
```bash
uv venv # create env .venv
uv sync # install dependencies
```

3. Start developping :
  + Add your library code in the `src/` directory
  + Write tests in the `tests/` directory
  + Add your license
  + Update `pyproject.toml` with your package information

4. In order to commit you need to :
    + Have no error from linter ([ruff](https://docs.astral.sh/ruff/))
    + Pass all tests ([pytest](https://docs.pytest.org/en/stable/))

## Development Workflows

### Code Quality

To ensure a certain level of code quality, [Ruff](https://docs.astral.sh/ruff/) is used.

Configuration can be found in `pyproject.toml`.

### Test

Tests must be write in `tests` and follow the convention of [pytest](https://docs.pytest.org/en/stable/)

### Scripts

All automation scripts are defined in `noxfile.py` file.

To run them use the following commands :
```bash
nox                   # Run all scripts
nox -s <script_name>  # Run a scpecific script
```

#### Available scripts :

+ `lint` : Check the codebase respect all linting and format rules
+ `clean` : Delete build directory `dist`
+ `tests` : Run tests from `tests` folder with python version from 3.9 to 3.13 

You can list them with `nox --list`.

See [Nox documentation](https://nox.thea.codes/en/stable/) if you want to know more.

## Publishing your package

### Automatic Publishing

Your package is automatically published when you push to:
- `main` branch → Published to [PyPI](https://pypi.org/)
- `dev` branch → Published to [TestPyPI](https://test.pypi.org/)

### Manual Publishing

You can also publish it manually with the following commands :
```bash
uv publish --token YOUR_PYPI_TOKEN
# OR
uv publish --index testpypi --token YOUR_TEST_PYPI_TOKEN
```

## Installing your package

Once published, your package can be installed with:

```sh
uv add your-package-name
uv add --default-index https://test.pypi.org/simple/ your-package-name # For testing
```

Or use pip :

```sh
pip install your-package-name
pip install --index-url https://test.pypi.org/simple/ your-package-name # For testing
```

## Links

- [UV Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/en/stable/)
- [Nox Documentation](https://nox.thea.codes/en/stable/)
- [Python Packaging Guide](https://packaging.python.org/)