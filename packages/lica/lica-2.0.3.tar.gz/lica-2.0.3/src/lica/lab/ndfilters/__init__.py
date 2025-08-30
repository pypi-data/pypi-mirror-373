# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) 2021
#
# See the LICENSE file for details
# see the AUTHORS file for authors
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
from importlib.resources import files

# ---------------------
# Thrid-party libraries
# ---------------------

import numpy as np
import astropy.io.ascii
import astropy.units as u
from astropy.table import Table

# ------------------------
# Own modules and packages
# ------------------------

from ..types import BENCH, COL
from ... import StrEnum

# ----------------
# Module constants
# ----------------


class NDFilter(StrEnum):
    """Neutral Density filter labels"""

    ND05 = "ND-0.5"  # 30% Transmittance
    ND1 = "ND-1.0"  # 10% Transmittance
    ND15 = "ND-1.5"  # 3% Transmittance
    ND2 = "ND-2.0"  # 1% Transmittance
    ND25 = "ND-2.5"  # 0.3% Transmittance
    ND3 = "ND-3.0"  # 0.1% Transmittance


# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger(__name__)

# ------------------
# Auxiliary fnctions
# ------------------


def _load(
    model: NDFilter,
    resolution: int,
    beg_wave: float,
    end_wave: float,
) -> Table:
    name = f"{model}-{COL.TRANS}@1nm.ecsv"
    log.info("Loading Transmittance from %s", name)
    in_path = files("lica.lab.ndfilters").joinpath(name)
    table = astropy.io.ascii.read(in_path, format="ecsv")
    if (beg_wave > BENCH.WAVE_START) and (end_wave < BENCH.WAVE_END):
        history = {
            "Description": "Trimmed both ends",
            "Start wavelength": beg_wave * u.nm,
            "End wavelength": end_wave * u.nm,
        }
        table.meta["History"].append(history)
    elif beg_wave == BENCH.WAVE_START and end_wave < BENCH.WAVE_END:
        history = {
            "Description": "Trimmed higher end",
            "Start wavelength": beg_wave * u.nm,
            "End wavelength": end_wave * u.nm,
        }
        table.meta["History"].append(history)
    elif beg_wave > BENCH.WAVE_START and end_wave == BENCH.WAVE_END:
        history = {
            "Description": "Trimmed lower end",
            "Start wavelength": beg_wave * u.nm,
            "End wavelength": end_wave * u.nm,
        }
        table.meta["History"].append(history)
    else:
        pass
    table = table[(table[COL.WAVE] >= beg_wave) & (table[COL.WAVE] <= end_wave)]
    if resolution > 1:
        table = table[::resolution]
        history = {
            "Description": f"Subsampled calibration from {name}",
            "Resolution": resolution * u.nm,
            "Start wavelength": np.min(table[COL.WAVE]) * u.nm,
            "End wavelength": np.max(table[COL.WAVE]) * u.nm,
        }
        table.meta["History"].append(history)
    return table


def export(
    path: str,
    model: NDFilter,
    resolution: int,
    beg_wave: float = BENCH.WAVE_START,
    end_wave: float = BENCH.WAVE_END,
) -> None:
    """Make a copy of the proper ECSV Astropy Table"""
    table = _load(model, resolution, beg_wave, end_wave)
    table.write(path, delimiter=",", overwrite=True)


def load(
    model: NDFilter,
    resolution: int,
    beg_wave: float = BENCH.WAVE_START,
    end_wave: float = BENCH.WAVE_END,
) -> Table:
    """Return a ECSV as as Astropy Table"""
    return _load(model, resolution, beg_wave, end_wave)


__all__ = ["load", "export"]
