all: run

setup:
	python3 -m venv venv
	./venv/bin/pip install -e .

run: setup
	./venv/bin/search-engine-cli

clean:
	rm -rf venv
	rm -rf src/*.egg-info
	rm -rf src/search_engine/__pycache__
	rm -rf nltk_data

.PHONY: setup run clean