# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

# ---------------------
# Third party libraries
# ---------------------

from sqlalchemy.orm import DeclarativeBase

# -------------
# local imports
# -------------

from ..metadata import metadata


class Model(DeclarativeBase):
    """The Base class all of our models must derive"""

    metadata = metadata


__all__ = ["metadata", "Model"]
