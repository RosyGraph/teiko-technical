FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY cell-count.csv load_data.py ./
COPY loblaw ./loblaw
COPY reports ./reports

RUN pip install --no-cache-dir .

# Populate the SQLite database at image build time.
RUN python load_data.py

CMD streamlit run loblaw/dashboard/app.py \
    --server.address=0.0.0.0 \
    --server.port=${PORT:-8501}
