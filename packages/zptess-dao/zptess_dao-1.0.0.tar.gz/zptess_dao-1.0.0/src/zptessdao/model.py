# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


# --------------------
# System wide imports
# -------------------

from __future__ import annotations

import sys
import logging

from typing import Optional, List, Set, Type
from datetime import datetime

# =====================
# Third party libraries
# =====================

if sys.version_info[1] < 11:
    from typing_extensions import Self
else:
    from typing import Self


from sqlalchemy import (
    select,
    func,
    Enum,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, aliased

from lica.sqlalchemy.metadata import metadata
from lica.sqlalchemy.view import view
from lica.asyncio.photometer import Model as PhotModel, Role, Sensor

from .constants import CentralTendency, Calibration

# ================
# Module constants
# ================

# =======================
# Module global variables
# =======================

# get the module logger
log = logging.getLogger(__name__)


def datestr(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f") if dt is not None else None


# =================================
# Data Model, declarative ORM style
# =================================

# ---------------------------------------------
# Additional conveniente types for enumerations
# ---------------------------------------------

RoleType: Enum = Enum(
    Role,
    name="role_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.name.lower() for e in x],
)

PhotModelType: Enum = Enum(
    PhotModel,
    name="model_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)


SensorType: Enum = Enum(
    Sensor,
    name="sensor_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)

CentralTendencyType: Enum = Enum(
    CentralTendency,
    name="central_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)

CalibrationType: Enum = Enum(
    Calibration,
    name="calibration_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)

# --------
# Entities
# --------


def make_Config(declarative_base: Type) -> Type:
    class Config(declarative_base):
        __tablename__ = "config_t"

        section: Mapped[str] = mapped_column(String(32), primary_key=True)
        prop: Mapped[str] = mapped_column("property", String(255), primary_key=True)
        value: Mapped[str] = mapped_column(String(255))

        def __repr__(self) -> str:
            return f"Config(section={self.section!r}, prop={self.prop!r}, value={self.value!r})"

    return Config


def make_Batch(declarative_base: Type) -> Type:
    class Batch(declarative_base):
        __tablename__ = "batch_t"

        id: Mapped[int] = mapped_column(primary_key=True)
        begin_tstamp: Mapped[datetime] = mapped_column(DateTime, unique=True)
        end_tstamp: Mapped[Optional[datetime]] = mapped_column(DateTime)
        email_sent: Mapped[Optional[bool]]
        calibrations: Mapped[Optional[int]]
        comment: Mapped[Optional[str]] = mapped_column(String(255))

        # This is not a real column, it s meant for the ORM
        summaries: Mapped[List["Summary"]] = relationship(back_populates="batch")  # noqa: F821

        def __repr__(self) -> str:
            return f"Batch(begin={datestr(self.begin_tstamp)}, end={datestr(self.end_tstamp)})"

    return Batch


def make_Photometer(declarative_base: Type) -> Type:
    class Photometer(declarative_base):
        __tablename__ = "photometer_t"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(10))
        mac: Mapped[str] = mapped_column(String(17))
        sensor: Mapped[SensorType] = mapped_column(SensorType, default=Sensor.TSL237)
        freq_offset: Mapped[float]
        model: Mapped[PhotModelType] = mapped_column(PhotModelType)
        firmware: Mapped[Optional[str]] = mapped_column(String(17))
        filter: Mapped[Optional[str]] = mapped_column(String(32), default="UV/IR-740")
        plug: Mapped[Optional[str]] = mapped_column(String(16), default="USB-A")
        box: Mapped[Optional[str]] = mapped_column(String(16), default="FSH714")
        collector: Mapped[Optional[str]] = mapped_column(
            String(16), default="standard"
        )  #  Collector model
        comment: Mapped[Optional[str]] = mapped_column(String(255))  # Photometer level comment

        # This is not a real column, it s meant for the ORM
        calibrations: Mapped[List["Summary"]] = relationship(back_populates="photometer")  # noqa: F821

        def __repr__(self) -> str:
            return f"Photom(id={self.id!r}, name={self.name!r}, mac={self.mac!r})"

        __table_args__ = (
            UniqueConstraint(name, mac),
            {},
        )

    return Photometer


def make_Summary(declarative_base: Type) -> Type:
    class Summary(declarative_base):
        __tablename__ = "summary_t"

        id: Mapped[int] = mapped_column(primary_key=True)
        phot_id: Mapped[int] = mapped_column(ForeignKey("photometer_t.id"), index=True)
        batch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("batch_t.id"))
        session: Mapped[datetime] = mapped_column(DateTime)  # calibration session identifier
        role: Mapped[RoleType] = mapped_column(RoleType)
        calibration: Mapped[CalibrationType] = mapped_column(CalibrationType, nullable=True)
        calversion: Mapped[Optional[str]] = mapped_column(
            String(64)
        )  # calibration software version
        author: Mapped[Optional[str]]  # who run the calibration
        nrounds: Mapped[Optional[int]]  # Number of rounds passed
        zp_offset: Mapped[
            Optional[float]
        ]  # Additional offset that was summed to the computed zero_point
        upd_flag: Mapped[
            Optional[bool]
        ]  # 1 => TESS-W ZP was updated, 0 => TESS-W ZP was not updated
        prev_zp: Mapped[Optional[float]]
        zero_point: Mapped[Optional[float]]  #  calibrated zero point
        zero_point_method: Mapped[CentralTendencyType] = mapped_column(
            CentralTendencyType, nullable=True
        )
        freq: Mapped[Optional[float]]  # final chosen frequency
        freq_method: Mapped[CentralTendencyType] = mapped_column(CentralTendencyType, nullable=True)
        mag: Mapped[Optional[float]]
        comment: Mapped[Optional[str]] = mapped_column(
            String(512)
        )  #  Additional comment for the calibration process

        # These are not a real columns, it is meant for the ORM
        batch: Mapped[Optional["Batch"]] = relationship(back_populates="summaries")  # noqa: F821
        photometer: Mapped["Photometer"] = relationship(back_populates="calibrations")  # noqa: F821
        rounds: Mapped[List["Round"]] = relationship(back_populates="summary")  # noqa: F821
        samples: Mapped[Set["Sample"]] = relationship(back_populates="summary")  # noqa: F821

        def __repr__(self) -> str:
            return f"Summary(session={datestr(self.session)}, role={self.role!r}, phot_id={self.phot_id!r})"

        __table_args__ = (UniqueConstraint(session, role), {})

    return Summary


SamplesRounds = Table(
    "samples_rounds_t",
    metadata,
    Column("round_id", ForeignKey("rounds_t.id"), nullable=False, primary_key=True),
    Column("sample_id", ForeignKey("samples_t.id"), nullable=False, primary_key=True),
)


def make_Round(declarative_base: Type) -> Type:
    class Round(declarative_base):
        __tablename__ = "rounds_t"

        id: Mapped[int] = mapped_column(primary_key=True)
        summ_id: Mapped[int] = mapped_column(ForeignKey("summary_t.id"), index=True)
        seq: Mapped[int] = mapped_column("round", Integer)  # Round number form 1..NRounds
        role: Mapped[RoleType] = mapped_column(RoleType)
        # session:    Mapped[datetime] = mapped_column(DateTime)
        freq: Mapped[Optional[float]]
        # Either average or median of samples for this frequencies round
        central: Mapped[CentralTendencyType] = mapped_column(CentralTendencyType, nullable=True)
        stddev: Mapped[Optional[float]]  # Standard deviation for frequency central estimate
        mag: Mapped[
            Optional[float]
        ]  # magnitiude corresponding to central frequency and summing ficticious zero point
        zp_fict: Mapped[
            Optional[float]
        ]  # Ficticious ZP to estimate instrumental magnitudes (=20.50)
        zero_point: Mapped[
            Optional[float]
        ]  # Estimated Zero Point for this round ('test' photometer round only, else NULL)
        nsamples: Mapped[Optional[int]]  # Number of samples for this round
        duration: Mapped[Optional[float]]  # Approximate duration, in seconds
        begin_tstamp: Mapped[Optional[datetime]] = mapped_column(DateTime)
        end_tstamp: Mapped[Optional[datetime]] = mapped_column(DateTime)

        # This is not a real column, it s meant for the ORM
        summary: Mapped["Summary"] = relationship(back_populates="rounds")  # noqa: F821
        # samples per round. Shoudl match the window size
        # This is not a real column, it s meant for the ORM
        samples: Mapped[List["Sample"]] = relationship(  # noqa: F821
            secondary=SamplesRounds, back_populates="rounds"
        )

        def __repr__(self) -> str:
            return f"Round(id={self.id!r}, #{self.seq!r} [{self.nsamples!r}] {self.role!r}, zp={self.zero_point} f={self.freq}, m={self.mag:.2f}@{self.zp_fict} Ts={datestr(self.begin_tstamp)}, Te={datestr(self.end_tstamp)})"

        __table_args__ = (UniqueConstraint(summ_id, seq, role), {})

    return Round


def make_Sample(declarative_base: Type) -> Type:
    class Sample(declarative_base):
        __tablename__ = "samples_t"

        id: Mapped[int] = mapped_column(primary_key=True)
        summ_id: Mapped[int] = mapped_column(ForeignKey("summary_t.id"), index=True)
        tstamp: Mapped[datetime] = mapped_column(DateTime)
        role: Mapped[RoleType] = mapped_column(RoleType)
        seq: Mapped[Optional[int]]
        freq: Mapped[float]
        temp_box: Mapped[Optional[float]]

        # rounds per sample (at least 1...)
        # This is not a real column, it s meant for the ORM
        rounds: Mapped[List["Round"]] = relationship(  # noqa: F821
            secondary=SamplesRounds, back_populates="samples"
        )

        # This is not a real column, it s meant for the ORM
        summary: Mapped["Summary"] = relationship(back_populates="samples")  # noqa: F821

        def __repr__(self) -> str:
            return (
                f"Sample(id={self.id!r}, role={self.role!r} freq={self.freq!r},  seq={self.seq!r})"
            )

        def __lt__(self, other: Self) -> bool:
            return self.tstamp < other.tstamp

        def __le__(self, other: Self) -> bool:
            return self.tstamp <= other.tstamp

        def __eq__(self, other: Self) -> bool:
            return self.tstamp == other.tstamp

        def __ne__(self, other: Self) -> bool:
            return self.tstamp != other.tstamp

        def __gt__(self, other: Self) -> bool:
            return self.tstamp > other.tstamp

        def __ge__(self, other: Self) -> bool:
            return self.tstamp >= other.tstamp

        def __hash__(self):
            return hash(self.tstamp)

        __table_args__ = (UniqueConstraint(tstamp, role), {})

    return Sample


# Create the view for barebones SQL statements from console
def make_SummaryView(declarative_base: Type, Photometer: Type, Summary: Type) -> Type:
    AliasSummary = aliased(Summary)

    summary_view = view(
        name="summary_v",
        metadata=metadata,
        selectable=select(
            Summary.id.label("id"),
            Photometer.model.label("model"),
            Photometer.name.label("name"),
            Photometer.mac.label("mac"),
            Photometer.firmware.label("firmware"),
            Photometer.sensor.label("sensor"),
            Summary.session.label("session"),
            Summary.role.label("role"),
            Summary.nrounds.label("nrounds"),
            Summary.upd_flag.label("upd_flag"),
            func.round(Summary.zero_point, 2).label("zero_point"),
            func.round(Summary.zp_offset, 2).label("zp_offset"),
            func.round((Summary.zero_point - Summary.zp_offset), 2).label("raw_zero_point"),
            Summary.calibration.label("calibration"),
            func.round(Summary.prev_zp, 2).label("prev_zp"),
            func.round(AliasSummary.mag, 2).label("ref_mag"),
            func.round(AliasSummary.freq, 3).label("ref_freq"),
            func.round(Summary.mag, 2).label("test_mag"),
            func.round(Summary.freq, 3).label("test_freq"),
            func.round((AliasSummary.mag - Summary.mag), 2).label("mag_diff"),
            Photometer.freq_offset.label("freq_offset"),
            Summary.zero_point_method.label("zero_point_method"),
            Summary.freq_method.label("freq_method"),
            Summary.calversion.label("calversion"),
            Photometer.filter.label("filter"),
            Photometer.plug.label("plug"),
            Photometer.box.label("box"),
            Photometer.collector.label("collector"),
            Summary.author.label("author"),
            Summary.comment.label("comment"),
        )
        .join(AliasSummary, AliasSummary.session == Summary.session)
        .join(Photometer, Photometer.id == Summary.phot_id)
        .where(AliasSummary.role == Role.REF, Summary.role == Role.TEST),
    )

    class SummaryView(declarative_base):
        __table__ = summary_view

        def __repr__(self) -> str:
            return f"SummaryView(name={self.name}, mac={self.mac}, session={datestr(self.session)}, role={self.role!r}, nrounds={self.nrounds!r}, zp={self.zero_point!r}, calib={self.calibration!r}, freq={self.freq!r})"

    return SummaryView


def make_RoundsView(declarative_base: Type, Photometer: Type, Summary: Type, Round: Type) -> Type:
    # Another view for exporting data
    rounds_view = view(
        name="rounds_v",
        metadata=metadata,
        selectable=select(
            Round.id.label("id"),
            Photometer.name.label("name"),
            Photometer.mac.label("mac"),
            Photometer.model.label("model"),
            Summary.session.label("session"),
            Round.__table__.c.round.label("round"),  # Problems with the 'round' attribute name'
            Round.role.label("role"),
            func.round(Round.freq, 3).label("freq"),
            Round.central.label("central"),
            func.round(Round.stddev, 4).label("stddev"),
            func.round(Round.mag, 3).label("mag"),
            Round.zp_fict.label("zp_fict"),
            Round.zero_point.label("zero_point"),
            Round.nsamples.label("nsamples"),
            func.round(Round.duration, 3).label("duration"),
            Round.begin_tstamp.label("begin_tstamp"),
            Round.end_tstamp.label("end_tstamp"),
            Summary.upd_flag.label("upd_flag"),
            Summary.nrounds.label("nrounds"),
            Summary.freq.label("mean_freq"),
            Summary.freq_method.label("freq_method"),
        )
        .join(Summary, Round.summ_id == Summary.id)
        .join(Photometer, Photometer.id == Summary.phot_id),
    )

    class RoundView(declarative_base):
        __table__ = rounds_view

        def __repr__(self) -> str:
            return f"RoundsView(name={self.name}, mac={self.mac}, session={datestr(self.session)}, role={self.role!r}, freq={self.freq!r}, method={self.central!r})"

    return RoundView


def make_SampleView(
    declarative_base: Type,
    Photometer: Type,
    Summary: Type,
    Round: Type,
    Sample: Type,
) -> Type:
    # Another view for exporting data
    samples_view = view(
        name="samples_v",
        metadata=metadata,
        selectable=select(
            Sample.id.label("id"),
            Photometer.name.label("name"),
            Photometer.mac.label("mac"),
            Photometer.model.label("model"),
            Summary.session.label("session"),
            Summary.upd_flag.label("upd_flag"),
            Round.__table__.c.round.label("round"),  # Problems with the 'round' attribute name'
            Sample.role.label("role"),
            Sample.tstamp.label("tstamp"),
            func.round(Sample.freq, 3).label("freq"),
            Sample.temp_box.label("temp_box"),
            Sample.seq.label("seq"),
        )
        .select_from(SamplesRounds)
        .join(Sample, SamplesRounds.c.sample_id == Sample.id)
        .join(Round, SamplesRounds.c.round_id == Round.id)
        .join(Summary, Sample.summ_id == Summary.id)
        .join(Photometer, Photometer.id == Summary.phot_id),
    )

    class SampleView(declarative_base):
        __table__ = samples_view

        def __repr__(self) -> str:
            return f"SampleView(name={self.name}, mac={self.mac}, session={datestr(self.session)}, role={self.role!r}, freq={self.freq!r}, sequence={self.sequence!r})"

    return SampleView
