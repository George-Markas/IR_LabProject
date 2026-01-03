setup:
	python3 -m venv $(VENV)
	./venv/bin/pip install -e .
	@echo "Setup complete! Run the search engine using 'make run'"

run:
	./venv/bin/search-engine-cli

clean:
	rm -rf venv
	rm -rf src/*.egg-info
	rm -rf src/search_engine/__pycache__

.PHONY: setup run clean