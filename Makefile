all: run

venv:
	python3 -m venv venv
	./venv/bin/pip install -e .
	@echo "Setup complete"

run: venv
	./venv/bin/search-engine-cli

clean:
	rm -rf venv
	rm -rf src/*.egg-info
	rm -rf src/search_engine/__pycache__
	@echo "The datasets still have to be removed manually. Check nltk and kagglehub default directories"

.PHONY: setup run clean