from models import Sample, CellCount, Project, Subject
from load_data import _fill_projects, _fill_subjects, _fill_samples


def test_fill_samples_creates_samples_and_cell_counts(session, tmp_path):
    csv_path = tmp_path / "cell-count.csv"
    csv_path.write_text(
        "project,subject,condition,age,sex,treatment,response,sample,sample_type,time_from_treatment_start,b_cell,cd8_t_cell,cd4_t_cell,nk_cell,monocyte\n"
        "prj1,sbj001,melanoma,55,M,miraclib,yes,sample00001,PBMC,0,10,20,30,40,50\n"
    )

    _fill_projects(session, csv_path)
    _fill_subjects(session, csv_path)
    _fill_samples(session, csv_path)

    projects = session.query(Project).all()
    subjects = session.query(Subject).all()
    samples = session.query(Sample).all()
    counts = session.query(CellCount).all()

    assert len(projects) == 1
    assert len(subjects) == 1
    assert len(samples) == 1
    assert len(counts) == 5
    assert sum(c.count for c in counts) == 150


def test_fill_samples_creates_normalized_records(session, tmp_path):
    csv_path = tmp_path / "cell-count.csv"
    csv_path.write_text(
        "project,subject,condition,age,sex,treatment,response,sample,sample_type,time_from_treatment_start,b_cell,cd8_t_cell,cd4_t_cell,nk_cell,monocyte\n"
        "prj1,sbj001,melanoma,55,M,miraclib,yes,sample00001,PBMC,0,10,20,30,40,50\n"
        "prj1,sbj001,melanoma,55,M,miraclib,yes,sample00002,PBMC,7,11,21,31,41,51\n"
        "prj1,sbj002,melanoma,61,F,miraclib,no,sample00003,PBMC,0,5,15,25,35,45\n"
        "prj2,sbj003,carcinoma,44,F,none,,sample00004,WB,0,1,2,3,4,5\n"
    )

    _fill_projects(session, csv_path)
    _fill_subjects(session, csv_path)
    _fill_samples(session, csv_path)

    projects = session.query(Project).all()
    subjects = session.query(Subject).all()
    samples = session.query(Sample).all()
    counts = session.query(CellCount).all()

    assert len(projects) == 2
    assert len(subjects) == 3
    assert len(samples) == 4
    assert len(counts) == 20

    s1 = session.get(Subject, "sbj001")
    assert s1 is not None
    assert s1.response is True
    assert len(s1.samples) == 2

    s2 = session.get(Subject, "sbj002")
    assert s2 is not None
    assert s2.response is False

    s3 = session.get(Subject, "sbj003")
    assert s3 is not None
    assert s3.response is None

    sample = session.get(Sample, "sample00001")
    assert sample is not None
    assert sample.subject_id == "sbj001"
    assert sample.sample_type == "PBMC"
    assert sample.time_from_treatment_start == 0
    assert len(sample.cell_counts) == 5

    counts_by_population = {c.population: c.count for c in sample.cell_counts}
    assert counts_by_population == {
        "b_cell": 10,
        "cd8_t_cell": 20,
        "cd4_t_cell": 30,
        "nk_cell": 40,
        "monocyte": 50,
    }
