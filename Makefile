.PHONY: doctor setup load-data pipeline dashboard test clean

PYTHON := python3
MIN_PYTHON := 3.12
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest
VENV_STREAMLIT := $(VENV)/bin/streamlit

doctor:
	@$(PYTHON) -c 'import sys; exit(0 if sys.version_info >= (3,12) else 1)' || { \
		echo "Python >= $(MIN_PYTHON) is required."; \
		echo "Found: $$($(PYTHON) --version 2>/dev/null || echo missing)"; \
		exit 1; \
	}
	@echo "Python: $$($(PYTHON) --version)"

setup: doctor
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e .

load-data: setup
	$(VENV_PYTHON) load_data.py

pipeline: load-data
	$(VENV_PYTHON) loblaw/reports.py

dashboard: load-data
	PYTHONPATH=$(PWD) $(VENV_STREAMLIT) run loblaw/dashboard/app.py

test: setup
	$(PYTEST)

clean:
	rm -rf $(VENV)
	rm -f teiko.db
	rm -rf reports/
