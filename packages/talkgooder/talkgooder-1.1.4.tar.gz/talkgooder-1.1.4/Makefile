clean:
	rm -rf \
	__pycache__ \
	src/talkgooder/__pycache__ \
	tests/__pycache__ \
	.pytest_cache \
	dist \
	_version.py \
	src/*.egg-info \
	docsrc/_doctrees \
	docs

lint:
	flake8 src/ tests/ --count --max-complexity=10 --max-line-length=100 --statistics --exit-zero
	black src/ tests/ --check --diff

format:
	black src/ tests/

test:
	pytest

build: clean lint test
	python3 -m build

html: build
	sphinx-build -b html docsrc docs -E -d "docsrc/_doctrees"
	touch docs/.nojekyll