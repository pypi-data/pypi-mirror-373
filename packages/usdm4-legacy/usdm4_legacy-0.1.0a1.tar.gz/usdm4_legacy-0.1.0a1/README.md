# USDM4 Legacy

Package for processing legacy PDF protocols into USDM

# Build Package

Build steps for deployment to pypi.org

- Run `pytest`, ensure coverage and all tests pass
- Run `ruff format`
- Run `ruff check`, ensure no errors
- Build with `python3 -m build --sdist --wheel`
- Upload to pypi.org using `twine upload dist/*`