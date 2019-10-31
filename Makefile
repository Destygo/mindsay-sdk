clean:
	git clean -xdf


publish:
	pip install --upgrade pip setuptools wheel
	pip install tqdm
	pip install --upgrade twine

	python setup.py bdist_wheel
	twine upload dist/*

release: clean publish
