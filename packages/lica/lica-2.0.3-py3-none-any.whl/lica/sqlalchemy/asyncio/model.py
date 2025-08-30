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
from sqlalchemy.ext.asyncio import AsyncAttrs

# -------------
# local imports
# -------------

from ..metadata import metadata

class Model(AsyncAttrs, DeclarativeBase):
    metadata = metadata


__all__ = ["metadata", "Model"]
