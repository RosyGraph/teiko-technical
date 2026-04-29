.PHONY: setup pipeline dashboard test clean

setup:
	uv sync

pipeline:
	uv run python load_data.py
	uv run python analysis.py

test:
	uv run pytest

clean:
	rm -f teiko.db
