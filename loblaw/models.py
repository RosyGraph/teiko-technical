from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()


class Project(Base):
    __tablename__ = "project"
    id: Mapped[str] = mapped_column(primary_key=True)

    subjects: "Mapped[list[Subject]]" = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Subject(Base):
    __tablename__ = "subject"
    id: Mapped[str] = mapped_column(primary_key=True)
    condition: Mapped[str]
    age: Mapped[int]
    sex: Mapped[str]
    treatment: Mapped[str]
    response: Mapped[bool | None]

    project_id: Mapped[str] = mapped_column(ForeignKey("project.id"))
    project: Mapped[Project] = relationship(back_populates="subjects")

    samples: "Mapped[list[Sample]]" = relationship(
        back_populates="subject", cascade="all, delete-orphan"
    )


class Sample(Base):
    __tablename__ = "sample"
    id: Mapped[str] = mapped_column(primary_key=True)
    sample_type: Mapped[str]
    time_from_treatment_start: Mapped[int]

    subject_id: Mapped[str] = mapped_column(ForeignKey("subject.id"))
    subject: Mapped[Subject] = relationship(back_populates="samples")

    cell_counts: "Mapped[list[CellCount]]" = relationship(
        back_populates="sample", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "subject_id",
            "time_from_treatment_start",
            "sample_type",
            name="uq_sample_type_time",
        ),
    )


class CellCount(Base):
    __tablename__ = "cell_count"
    id: Mapped[int] = mapped_column(primary_key=True)
    population: Mapped[str]
    count: Mapped[int]

    sample_id: Mapped[str] = mapped_column(ForeignKey("sample.id"))
    sample: Mapped[Sample] = relationship(back_populates="cell_counts")

    __table_args__ = (
        UniqueConstraint(
            "sample_id",
            "population",
            name="uq_sample_id_population",
        ),
    )
