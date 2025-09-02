"""Module providing constants for EnFROSP."""

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
# limitations under the License

import os

import numpy as _np

from . import path_data

# TODO what is this?
samka = _np.array([0.0, 0.2335, 0.5271])
bamka = _np.array([1.0, 0.66, 0.3612])
pamka = _np.array([7.86e-8, 3.27e-5, 2.35e-5])

# Ice density (g/cm^3)
densi = 0.917

# ice refractive index read from index.dat and refrindex.dat
_index = _np.loadtxt(os.path.join(path_data, 'index.dat'))  # (224, 3)
waves_um = _index[:, 0]  # wavelengths in micrometers  # TODO why not read from image metadata?
waves_nm = waves_um * 1000  # wavelengths in nanometers
an = _index[:, 1]  # TODO what is this?
ak = _index[:, 2]  # TODO what is this?

OE = _np.fromfile(os.path.join(path_data, 'ssi_opt_enmap.dat'), dtype='f8')
_refrindex = _np.loadtxt(os.path.join(path_data, 'refrindex.dat'))  # (164, 3)
WMIC = _refrindex[:, 0]  # wavelength in microns
REFRIT = _refrindex[:, 1]  # TODO what is this?
ASTRAL = _refrindex[:, 2]  # TODO what is this?
