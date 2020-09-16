.PHONY = clean test

init:
	pip install shapely pyshp folium branca requests us tox flake8 black pytest

test:
	tox

test-local:
	pip install -e .
	pytest

clean:
	# On Windows, may need to add %git home%\usr\bin to path
	rm -rf build dist .egg src/bbd.egg-info

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*
	rm -fr build dist .egg src/bbd.egg-info

flake8:
	# Ignoring...
	# E501: line too long
	# W503: line break before binary operator
	# E203: whitespace before :
	flake8 --extend-ignore=E501,W503,E203 src

black:
	black src tests
