# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


# --------------------
# System wide imports
# -------------------

from typing import Type

# ---------------------
# Third party libraries
# ---------------------

from lica.sqlalchemy.asyncio.model import Model

# -------------------
# Own package imports
# -------------------

from .model import (
    make_Config,
    make_Batch,
    make_Photometer,
    make_Summary,
    make_Round,
    make_Sample,
    make_SummaryView,
    make_RoundsView,
    make_SampleView,
)

# Tables creation with the asyncio Model behaviour built-in

Config: Type = make_Config(Model)
Batch: Type = make_Batch(Model)
Photometer: Type = make_Photometer(Model)
Summary: Type = make_Summary(Model)
Round: Type = make_Round(Model)
Sample: Type = make_Sample(Model)

SummaryView: Type = make_SummaryView(Model, Photometer, Summary)
RoundsView: Type = make_RoundsView(Model, Photometer, Summary, Round)
SampleView: Type = make_SampleView(Model, Photometer, Summary, Round, Sample)

__all__ = [
    "Config",
    "Batch",
    "Photometer",
    "Summary",
    "Round",
    "Sample",
    "SummaryView",
    "RoundsView",
    "SampleView",
]
