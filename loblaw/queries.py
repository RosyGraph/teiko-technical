from sqlalchemy import Select, func, select

from loblaw.models import CellCount, Project, Sample, Subject


def all_sample_cell_population_frequencies_stmt() -> Select:
    total_count_ann = (
        func.sum(CellCount.count)
        .over(partition_by=CellCount.sample_id)
        .label("total_count")
    )
    return select(
        CellCount.sample_id.label("sample"),
        total_count_ann,
        CellCount.population,
        CellCount.count,
        (100.0 * CellCount.count / total_count_ann).label("percentage"),
    ).order_by(CellCount.sample_id, CellCount.population)


def miraclib_melanoma_pbmc_response_cell_frequencies_stmt() -> Select:
    freqs = all_sample_cell_population_frequencies_stmt().subquery()
    return (
        select(
            freqs.c.sample,
            freqs.c.total_count,
            freqs.c.population,
            freqs.c.count,
            freqs.c.percentage,
            Subject.response,
            Sample.subject_id,
            Sample.time_from_treatment_start,
        )
        .join(Sample, Sample.id == freqs.c.sample)
        .join(Subject, Subject.id == Sample.subject_id)
        .where(
            Sample.sample_type == "PBMC",
            Subject.condition == "melanoma",
            Subject.treatment == "miraclib",
            Subject.response.is_not(None),
        )
    )


def baseline_miraclib_melanoma_pbmc_samples_stmt() -> Select:
    return (
        select(
            Sample.id.label("sample"),
            Subject.id.label("subject"),
            Project.id.label("project"),
            Subject.response.label("response"),
            Subject.sex.label("sex"),
            Sample.time_from_treatment_start,
            Sample.sample_type,
            Subject.condition,
            Subject.treatment,
        )
        .join(Subject, Sample.subject_id == Subject.id)
        .join(Project, Subject.project_id == Project.id)
        .where(
            Subject.condition == "melanoma",
            Sample.sample_type == "PBMC",
            Sample.time_from_treatment_start == 0,
            Subject.treatment == "miraclib",
        )
        .order_by(Project.id, Subject.id, Sample.id)
    )


def baseline_miraclib_melanoma_pbmc_samples_by_project_stmt() -> Select:
    subset = baseline_miraclib_melanoma_pbmc_samples_stmt().subquery()
    return (
        select(subset.c.project, func.count(subset.c.sample).label("sample_count"))
        .group_by(subset.c.project)
        .order_by(subset.c.project)
    )


def baseline_miraclib_melanoma_pbmc_subjects_by_response_stmt() -> Select:
    subset = baseline_miraclib_melanoma_pbmc_samples_stmt().subquery()
    subject_count = func.count(func.distinct(subset.c.subject)).label("subject_count")
    return (
        select(subset.c.response, subject_count)
        .group_by(subset.c.response)
        .order_by(subject_count.desc())
    )


def baseline_miraclib_melanoma_pbmc_subjects_by_sex_stmt() -> Select:
    subset = baseline_miraclib_melanoma_pbmc_samples_stmt().subquery()
    subject_count = func.count(func.distinct(subset.c.subject)).label("subject_count")
    return (
        select(subset.c.sex, subject_count)
        .group_by(subset.c.sex)
        .order_by(subject_count.desc())
    )


def baseline_melanoma_male_responders_avg_b_cells_stmt() -> Select:
    return (
        select(
            func.avg(CellCount.count).label("average_count"),
            func.count(CellCount.count).label("n_samples"),
        )
        .join(Sample, CellCount.sample_id == Sample.id)
        .join(Subject, Sample.subject_id == Subject.id)
        .where(
            Subject.condition == "melanoma",
            Subject.sex == "M",
            Subject.response.is_(True),
            Sample.time_from_treatment_start == 0,
            CellCount.population == "b_cell",
        )
    )
