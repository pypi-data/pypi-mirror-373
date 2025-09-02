"""EnFROSP functions needed within the retrieval."""

# EnFROSP, EnMAP Fast Retrieval Of Snow Properties
#
# Copyright (c) 2024–2025, GFZ Helmholtz Centre Potsdam, Daniel Scheffler (danschef@gfz.de)
#
# This software was developed within the context of the EnMAP project supported
# by the DLR Space Administration with funds of the German Federal Ministry of
# Economic Affairs and Energy (on the basis of a decision by the German Bundestag:
# 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Tuple

import numpy as np
from scipy.optimize import brentq

from ..io.reader_enmap import EnMAPL1CMetadata
from .constants import WMIC, ASTRAL


def get_transcendent_snow_albedo_equation(x: float, fe: float, c: float, alb: float):
    return x ** fe + c * alb * x - c


def atmos(wavelength_nm: float,
          im_meta: EnMAPL1CMetadata
          ) -> Tuple[float, float, float]:
    """Compute atmospheric contribution.

    This subroutine calculates the effects of the atmosphere on the reflectance (reflec), albedo (albedo),
    and transmittance (trans). It uses aerosol and molecular scattering parameters and integrates them with
    the phase function of the aerosol and atmospheric properties.

    Inputs: wavelength_um (wavelength in micrometers), reflec (reflectance), albedo, trans (transmittance).
    Common Variables: Several atmospheric properties such as AOT (Aerosol Optical Thickness), ANGST
    (Ångström exponent), and aerosol scattering parameters are used.
    Outputs: Path radiance, atmospheric spherical albedo, and transmittance at given conditions.

    ToDo: Check and revise this docstring.

    :param wavelength_nm:
    :param im_meta:
    :return:
    """
    tau550 = im_meta.aot
    wave = wavelength_nm / 1000.0

    # Aerosol Optical Thickness
    tauaer = tau550 * (wave / 0.55) ** (-im_meta.angst)

    # DOUBLE H-G phase function for aerosol
    g0 = 0.5263
    g1 = 0.4627
    gaer = g0 + g1 * np.exp(-wave / 0.4685)
    g11 = 0.80
    g22 = -0.45
    pa1 = (1 - g11 ** 2) / (1 - 2 * g11 * im_meta.co + g11 ** 2) ** 1.5
    pa2 = (1 - g22 ** 2) / (1 - 2 * g22 * im_meta.co + g22 ** 2) ** 1.5
    cp = (gaer - g11) / (g11 - g22)
    pa = cp * pa1 + (1 - cp) * pa2

    # Molecular Scattering Parameters
    pr = 0.75 * (1 + im_meta.co ** 2)
    taumol = 0.0053 / wave ** 4.0932

    # Aerosol-Molecular Scattering Parameters
    tau = tauaer + taumol
    p = (taumol * pr + tauaer * pa) / tau
    g = tauaer * gaer / tau

    # Path Radiance Calculation
    amu1 = im_meta.amu1
    amu2 = im_meta.amu2
    amf = 1.0 / amu1 + 1.0 / amu2
    astra = (1.0 - np.exp(-tau * amf)) / (amu1 + amu2) / 4.0
    oskar = 4.0 + 3.0 * (1 - g) * tau
    b1 = 1.0 + 1.5 * amu1 + (1 - 1.5 * amu1) * np.exp(-tau / amu1)
    b2 = 1.0 + 1.5 * amu2 + (1 - 1.5 * amu2) * np.exp(-tau / amu2)
    rss = p * astra
    rms = 1.0 - b1 * b2 / oskar + (3.0 * (1.0 + g) * amu1 * amu2 - 2.0 * (amu1 + amu2)) * astra
    reflec = rss + rms

    # Atmospheric Spherical Albedo Calculation
    gasa = 0.5772157
    y = (1.0 + tau) * tau * np.exp(-tau) / 4.0
    z3 = tau ** 2 * (-np.log(tau) - gasa)
    z4 = tau ** 2 * (tau - tau ** 2 / 4.0 + tau ** 3 / 18.0)
    z = z3 + z4
    f = (1.0 + 0.5 * tau) * z / 2.0 - y
    w1 = 1.0 + f
    w2 = 1.0 + 0.75 * tau * (1.0 - g)
    albedo = 1.0 - w1 / w2

    # Atmospheric Transmittance Calculation
    tz = 1.0 + gaer ** 2 + (1 - gaer ** 2) * np.sqrt(1 + gaer ** 2)
    baer = 0.5 + gaer * (gaer ** 2 - 3.0) / tz / 2.0
    if gaer >= 1.e-3:
        gt = (1.0 + gaer) / np.sqrt(1.0 + gaer ** 2) - 1.0
        baer = (1.0 - gaer) * gt / 2.0 / gaer
    b = (0.5 * taumol + baer * tauaer) / tau
    at1 = np.exp(-b * tau / amu1)
    at2 = np.exp(-b * tau / amu2)
    trans = at1 * at2

    return reflec, albedo, trans


def safe_brentq(fe, c, alb, a, b, xtol):
    """Find a root of a function in a bracketing interval using Brent's method."""
    try:
        return brentq(get_transcendent_snow_albedo_equation, a, b, args=(fe, c, alb), xtol=xtol)
    except ValueError:
        # occurs in case f(a) and f(b) do not have opposite signs
        return -999  # FIXME occurs for some pixels at the image edge (probably fixable via mask_baddata)


def vectorized_brentq(fe_arr: np.ndarray, c_arr: np.ndarray, alb: float, a=0.1, b=1.0, xtol=1e-3):
    vectorized_solver = np.vectorize(
        lambda fe, c: safe_brentq(fe, c, alb, a, b, xtol)
    )
    return vectorized_solver(fe_arr, c_arr)


def funti(wvl: float,
          ff2: np.ndarray,
          aae: np.ndarray,
          pal: np.ndarray
          ) -> np.ndarray:
    """TODO add a docstring there.

    :param wvl:   wavelength in microns
    :param ff2:
    :param aae:   impurity absorption angstrom exponent
    :param pal:   particle absorption length (micron)
    :return:

    .. note:: Equations are explained in:
          Kokhanovsky (2021): The Broadband Albedo of Snow. https://doi.org/10.3389/fenvs.2021.757575
    """
    # get akap, the imaginary part of ice refractive index
    absdiffs = np.abs(wvl - WMIC)
    # search through WMIC to find appropriate akap value and interpolate if the exact value is not found
    akap = ASTRAL[absdiffs.argmin()] if absdiffs[absdiffs.argmin()] < 1.e-4 else np.interp(wvl, WMIC, ASTRAL)

    # compute spectral snow albedo
    alpha = 4.0 * np.pi * akap / wvl  # bulk ice absorption coefficient
    x0 = 0.55
    q = alpha + ff2 * (wvl / x0) ** (-aae)
    psi1 = np.exp(-np.sqrt(q * pal))  # spectral albedo of clean plane-parallel snow surfaces

    # compute solar irradiance E_0 (λ) at the bottom of atmosphere
    f0 = 32.38  # W/m²/µm
    f1 = -160140.33  # W/m²/µm
    f2 = 7959.53  # W/m²/µm
    bet = 0.08534  # µm
    gam = 0.40179  # µm
    psi2 = f0 + f1 * np.exp(-wvl / bet) + f2 * np.exp(-wvl / gam)  # incident spectral solar flux at the snow surface

    return psi1 * psi2


def funtip(wvl: float,
           u1: float,
           ff2: np.ndarray,
           aae: np.ndarray,
           pal: np.ndarray
           ):
    """TODO add a docstring there.

    :param wvl:   wavelength in microns
    :param u1:    # TODO: what is this
    :param ff2:   # TODO: what is this
    :param aae:   impurity absorption angstrom exponent
    :param pal:   particle absorption length (micron)
    :return:
    """
    # get akap, the imaginary part of ice refractive index
    absdiffs = np.abs(wvl - WMIC)
    # search through WMIC to find appropriate akap value and interpolate if the exact value is not found
    akap = ASTRAL[absdiffs.argmin()] if absdiffs[absdiffs.argmin()] < 1.e-4 else np.interp(wvl, WMIC, ASTRAL)

    # Calculate alpha, Q, psi1, and psi2 based on the formulas
    alpha = 4.0 * np.pi * akap / wvl
    x0 = 0.55
    q = alpha + ff2 * (wvl / x0) ** (-aae)
    psi1 = np.exp(-u1 * np.sqrt(q * pal))

    # compute solar irradiance E_0 (λ) at the bottom of atmosphere
    f0 = 32.38  # W/m²/µm
    f1 = -160140.33  # W/m²/µm
    f2 = 7959.53  # W/m²/µm
    bet = 0.08534  # µm
    gam = 0.40179  # µm
    psi2 = f0 + f1 * np.exp(-wvl / bet) + f2 * np.exp(-wvl / gam)  # incident spectral solar flux at the snow surface

    return psi1 * psi2


def funtik(aa1, ab1):
    """TODO add a docstring there.

    :param aa1:
    :param ab1:
    :return:
    """
    f0 = 32.38  # W/m²/µm
    f1 = -160140.33  # W/m²/µm
    f2 = 7959.53  # W/m²/µm
    bet = 0.08534  # µm
    gam = 0.40179  # µm

    # Calculate the necessary terms
    # psi2 = f0 + f1 * exp(-x / bet) + f2 * exp(-x / gam)
    z1 = np.exp(-ab1 / bet) - np.exp(-aa1 / bet)
    z2 = np.exp(-ab1 / gam) - np.exp(-aa1 / gam)

    # Compute the FUNTIK value using the formula
    funtik_value = f0 * (ab1 - aa1) - z1 * f1 * bet - z2 * f2 * gam

    return funtik_value
