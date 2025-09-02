# IATI Sphinx Theme

## How do I use IATI Sphinx Theme?

See the [IATI Sphinx Theme Documentation](https://iati-sphinx-theme.readthedocs-hosted.com/en/latest/) for usage instructions.

If you are creating or editing an IATI documentation site, see the [IATI Docs Base](https://github.com/IATI/iati-docs-base) for relevant information.

## How do I contribute to IATI Sphinx Theme?

### Install dependencies

```
pip install -r requirements_dev.txt
```

### Update dependencies

```
python -m piptools compile --extra=dev -o requirements_dev.txt pyproject.toml
pip install -r requirements_dev.txt
```

### Run linting

```
black iati_sphinx_theme/ docs/
isort iati_sphinx_theme/ docs/
flake8 iati_sphinx_theme/ docs/
mypy iati_sphinx_theme/ docs/
```

### Documentation with live preview

1. In one terminal, build the CSS in watch mode

   ```
   npm run build:watch
   ```

2. In a separate terminal, install the Sphinx theme then start the docs development server:

   ```
   pip install -e .
   sphinx-autobuild -a docs docs/_build/html --watch iati_sphinx_theme/
   ```

### Testing a local version of the theme against another project

To run a local version of the theme with another project, e.g. `my-docs`, take the following steps:

1. Clone the `sphinx-theme` repository, and checkout the branch or tag you want to use.

2. Run the following command in the `sphinx-theme` directory, to build the CSS for the theme.

   ```
   npm run build
   ```

3. Go to `my-docs` directory, and install the Sphinx theme

   ```
   pip install -e /path/to/sphinx-theme
   ```

4. Set the `html_theme` option in your `conf.py`

   ```python
   html_theme = "iati_sphinx_theme"
   ```

5. Start the docs development server:

   ```
   pip install sphinx-autobuild
   sphinx-autobuild docs docs/_build/html
   ```

### Translation

The Sphinx theme itself contains both built-in strings that cannot be changed and strings that can be configured by the user via `conf.py`. To translate these, see [the sphinx-theme documentation](https://iati-sphinx-theme.readthedocs-hosted.com/en/latest/)

For instructions on translating an IATI documentation site that uses this theme, see the [iati-docs-base](https://github.com/IATI/iati-docs-base).  


### Release process

To publish a new version, raise a PR to `main`, updating the version in `pyproject.toml`. Once merged, create a git tag and GitHub release for the new version, with naming `vX.Y.Z`. This will trigger the package to be published to PyPI.
