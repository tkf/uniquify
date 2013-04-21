## Testing
test: cog
	tox

clean: clean-pycache
	rm -rf *.egg-info .tox MANIFEST

clean-pycache:
	rm -rf *.pyc __pycache__

## Update files using cog.py
cog: uniquify.py
uniquify.py: README.rst
	cog.py -r uniquify.py

## Upload to PyPI
upload: cog
	python setup.py register sdist upload
