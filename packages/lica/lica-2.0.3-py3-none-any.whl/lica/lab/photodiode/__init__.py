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


# Photodiode record
class Hamamatsu:
    MANUF = "Hamamatsu"
    MODEL = "S2281-01"
    SERIAL = "01097"
    WINDOW = "Quartz Glass"
    PHS_SIZE = 11.3 * u.mm  # Photosensitive size (diameter)
    PHS_AREA = 100 * (u.mm**2)  # Photosensitive area
    DARK = {
        "typ": {
            "Value": 50 * (u.pA),
            "Temp": 25 * u.deg_C,
        },
        "max": {  # Dark current at given room Temp
            "Value": 500 * (u.pA),
            "Temp": 25 * u.deg_C,
        },
    }
    # responsivity peak
    PEAK = {
        "typ": {
            "Wave": 960 * (u.nm),
            "Resp": 0.5 * (u.A / u.W),
            "Temp": 25 * u.deg_C,
        }
    }


# Photodiode record
class OSI:
    MANUF = "OSI"
    MODEL = "PIN-10D"
    SERIAL = "OSI-11-01-004-10D"
    WINDOW = "Quartz Glass"
    PHS_SIZE = 11.28 * u.mm  # Photosensitive size (diameter)
    PHS_AREA = 100 * (u.mm**2)  # Photosensitive area
    DARK = {
        "typ": {
            "Value": 2 * (u.nA),
            "Temp": 23 * u.deg_C,
        },
        "max": {  # Dark current at given room Temp
            "Value": 25 * (u.nA),
            "Temp": 23 * u.deg_C,
        },
    }
    # responsivity peak
    PEAK = {
        "typ": {
            "Wave": 970 * (u.nm),
            "Resp": 0.6 * (u.A / u.W),
            "Temp": 25 * u.deg_C,
        },
        "max": {
            "Wave": 970 * (u.nm),
            "Resp": 0.65 * (u.A / u.W),
            "Temp": 25 * u.deg_C,
        },
    }



class PhotodiodeModel(StrEnum):
    HAMAMATSU = f"{Hamamatsu.MODEL}"
    OSI = f"{OSI.MODEL}"


# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger(__name__)

# ------------------
# Auxiliary fnctions
# ------------------


def _load(
    model: PhotodiodeModel,
    resolution: int,
    beg_wave: float,
    end_wave: float,
    cross_calibrated: bool,
) -> Table:
    if model == PhotodiodeModel.OSI and cross_calibrated:
        name = f"{model}-Responsivity-Cross-Calibrated@1nm.ecsv"
    else:
        name = f"{model}-Responsivity-Interpolated@1nm.ecsv"
    log.info("Loading Responsivity & QE data from %s", name)
    in_path = files("lica.lab.photodiode").joinpath(name)
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
    model: PhotodiodeModel,
    resolution: int,
    beg_wave: float = BENCH.WAVE_START,
    end_wave: float = BENCH.WAVE_END,
    cross_calibrated: bool = True,
) -> None:
    """Make a copy of the proper ECSV Astropy Table"""
    table = _load(model, resolution, beg_wave, end_wave, cross_calibrated)
    table.write(path, delimiter=",", overwrite=True)


def load(
    model: PhotodiodeModel,
    resolution: int,
    beg_wave: float = BENCH.WAVE_START,
    end_wave: float = BENCH.WAVE_END,
    cross_calibrated: bool = True,
) -> Table:
    """Return a ECSV as as Astropy Table"""
    return _load(model, resolution, beg_wave, end_wave, cross_calibrated)


__all__ = ["load", "export"]
