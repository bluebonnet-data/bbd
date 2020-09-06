.PHONY = clean test

test:
	tox

clean:
	# On Windows, may need to add %git home%\usr\bin to path
	rm -rf build dist .egg src/bbd.egg-info

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*
