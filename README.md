# Teiko Technical

Solution repository for Teiko take home coding assignment

This project loads immune-cell samples into a normalized SQLite database, computes relative cell-population frequencies, performs treatment-response analysis, and exposes the results through generated report artifacts and an interactive Streamlit dashboard.

## Quickstart

This project requires Python 3.12+.

```bash
make setup
make pipeline
make dashboard
```

The dashboard will be served locally. Open the URL printed by `make dashboard` (typically http://localhost:8501/).

## Makefile targets

### `make setup`

Creates a virtual environment and installs project dependencies.

### `make pipeline`

Runs the full, reproducible data pipeline:
1. Initializes the SQLite database
2. Loads `cell-count.csv`
3. Generates report artifacts under `reports/`.

### `make dashboard`

Starts the interactive Streamlit dashboard.

### `make test`

Runs the test suite.

### `make clean`

Removes generated reports, virtual environment, and the SQLite database.

## Project structure

```
.
├── cell-count.csv
├── flake.lock
├── flake.nix
├── load_data.py
├── loblaw/
│   ├── analysis.py
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── data_overview.py
│   │   ├── splash.py
│   │   ├── treatment_response.py
│   │   └── treatment_subset_analysis.py
│   ├── db.py
│   ├── figures.py
│   ├── loader.py
│   ├── logging_config.py
│   ├── models.py
│   ├── queries.py
│   ├── reports.py
│   └── tests/
├── Makefile
├── pyproject.toml
├── README.md
├── reports/
└── uv.lock
```

Key modules:
- `load_data.py` is the required root-level script for initializing and loading the database
- `loblaw/models.py` defines the relational schema
- `loblaw/loader.py` parses `cell-count.csv` and migrates the data to the SQLite database
- `loblaw/queries.py` contains the SQLAlchemy `Select` statements for querying the database
- `loblaw/analysis.py` materializes query results as pandas DataFrames and performs statistical analysis
- `loblaw/figures.py` builds Plotly figures
- `loblaw/reports.py` persists generated CSV, HTML, and text artifacts to `reports/`
- `loblaw/dashboard/` contains the Streamlit dashboard pages

## Database schema

The input `cell-count.csv` contains sample-level immune-cell counts and associated metadata. I modeled this as a normalized relational schema with four main entities.

### `Project`

Represents a source project. Contains only the `id` as it appears in the input.

### `Subject`

Represents a patient/subject.

- `id`
- `age`
- `project_id`
- `condition`
- `treatment`
- `response`
- `sex`

### `Sample`

Represents a biological sample from a subject.

- `id`
- `subject_id`
- `sample_type`
- `time_from_treatment_start`

### `CellCount`

Represents one immune-cell population count for a given sample.

- `sample_id`
- `population`
- `count`

This design avoids storing the five populations as hard-coded columns in the wide CSV. Instead, each population count is represented as a row, which allows later extension given datasets with additional immune populations.

### Schema rationale and scalability

The schema separates project metadata, subject metadata, biological samples, and cell-population measurements. This has several advantages:

1. Avoids denormalization -- subject-level fields such as condition, treatment, response, and sex are stored once per subject instead of repeated across each sample measurement
2. Enforces data integrity -- foreign keys preserve the project -> subject -> sample -> cell-count hierarchy, while uniqueness constraints prevent duplicate measurements for the same sample/population pair and duplicate samples for the same subject, timepoint, and sample type
3. Supports longitudinal analysis -- subjects can have multiple linked samples at different `time_from_treatment_start` values, allowing repeated measurements over treatment time without duplicating subject-level metadata
4. Supports additional cell populations -- immune-cell populations are stored as rows in `cell_count` rather than hard-coded as columns, so new populations can be added without changing the schema
5. Scales along the analytical dimensions -- the relevant scaling factors are projects, subjects, samples, timepoints, and cell populations. The existing indices support the queries in the dashboard, and additional indices could be added for new analytical access patterns

## Assumptions

- `response = yes` is represented as `True`, `response = no` is represented as `False`, and missing response values are represented as `NULL`.
- Part 3 excludes samples with missing response values and includes only PBMC samples from melanoma patients treated with miraclib.
- Part 3 reports Mann-Whitney U tests for responder vs non-responder relative-frequency distributions, with Benjamini-Hochberg FDR correction across the five tested cell populations.
- The boxed scalar question is interpreted literally using the filters stated in the question: melanoma, male, responder, `time_from_treatment_start = 0`, and `b_cell`. I did not apply the Part 4 PBMC/miraclib filters to that standalone scalar answer.
- The default Part 3 report pools PBMC samples across treatment timepoints, so rows should be interpreted as sample-level observations rather than fully independent subject-level observations. The dashboard includes a timepoint selector to inspect individual timepoints separately.
- The schema assumes `(subject_id, time_from_treatment_start, sample_type)` identifies a unique sample in this dataset.

## Generated outputs

`make pipeline` generates the required output tables and plots under `reports/`, including:

```
reports/
├── melanoma_male_responder_baseline_b_cell_average.txt
├── part2_all_cell_population_frequencies.csv
├── part2_metadata.csv
├── part3_all_cell_populations_boxplot.html
├── part3_miraclib_pbmc_response_cell_frequencies.csv
├── part3_population_response_statistics.csv
├── part4_baseline_miraclib_melanoma_pbmc_samples.csv
├── part4_samples_by_project.csv
├── part4_samples_by_project.html
├── part4_subjects_by_response.csv
├── part4_subjects_by_response.html
├── part4_subjects_by_sex.csv
└── part4_subjects_by_sex.html
```

The boxed scalar question is answered in:

```
reports/melanoma_male_responder_baseline_b_cell_average.txt
```

It is computed using the filters stated in the question: `melanoma`, `male`, `responder`, `time_from_treatment_start = 0`, and `b_cell`.
