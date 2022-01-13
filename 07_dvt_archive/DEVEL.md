# Development of the Distant Viewing Toolkit

To build the documentation, run the following:

```
pdoc --html --output-dir docs --template-dir docs/pdoc_template/ --force dvt
```

To test the toolkit, use:

```
pytest --disable-warnings .
```

And to package and send the PyPI, use (needs password):

```
python setup.py sdist
twine upload dist/*
```
