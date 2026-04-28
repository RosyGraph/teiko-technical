.PHONY: setup pipeline dashboard test clean

setup:
	uv sync

pipeline:
	uv run python load_data.py

test:
	uv run pytest

clean:
	rm -f teiko.db
