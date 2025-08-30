# ----------------------------------------------------------------------
# Copyright (c) 2022
#
# See the LICENSE file for details
# see the AUTHORS file for authors
# ----------------------------------------------------------------------

import enum

class CentralTendency(enum.Enum):
    MEDIAN = "median"
    MODE = "mode"
    MEAN = "mean"

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value


class Calibration(enum.Enum):
    MANUAL = "MANUAL"
    AUTO = "AUTO"

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value
