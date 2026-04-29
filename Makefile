.PHONY: doctor setup pipeline dashboard test clean

PYTHON := python3
MIN_PYTHON := 3.10
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest
VENV_STREAMLIT := $(VENV)/bin/streamlit

doctor:
	@$(PYTHON) -c 'import sys; exit(0 if sys.version_info >= (3,10) else 1)' || { \
		echo "Python >= $(MIN_PYTHON) is required."; \
		echo "Found: $$($(PYTHON) --version 2>/dev/null || echo missing)"; \
		exit 1; \
	}
	@echo "Python: $$($(PYTHON) --version)"

setup: doctor
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e .

pipeline: setup
	$(VENV_PYTHON) load_data.py
	$(VENV_PYTHON) loblaw/analysis.py

dashboard: setup pipeline
	$(VENV_STREAMLIT) run loblaw/dashboard/app.py

test: setup
	$(PYTEST)

clean:
	rm -rf $(VENV)
	rm -f teiko.db
	rm -rf reports/
