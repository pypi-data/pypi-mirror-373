"""EnFROSP snow parameter retrieval."""

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


import os
import numpy as np
from geoarray import GeoArray
from scipy.integrate import quad_vec

from .constants import samka, bamka, pamka, densi, ak, waves_nm, waves_um
from .functions import atmos, vectorized_brentq, funti, funtip, funtik
from ..io.reader_enmap import EnMAPL1C


class Retrieval(object):
    def __init__(self,
                 path_enmap_zipfile: str,
                 path_outdir: str
                 ):
        """Initialize the retrieval.

        :param path_enmap_zipfile:  input path of the EnMAP L1C image to be processed (zip-archive)
        :param path_outdir:         output directory where the processed data is saved
        """
        self.path_enmap_zipfile = os.path.abspath(path_enmap_zipfile)
        self.path_outdir = os.path.abspath(path_outdir)

        self.im = EnMAPL1C(self.path_enmap_zipfile)

        if not os.path.isdir(path_outdir):
            print(f"The output directory {path_outdir} does not exist. Creating it now.")
            os.makedirs(path_outdir)

        # read reflectances
        self.refle = self.im.toa_reflectance / 10000.  # TOA reflectance between 0 and 1

        # THVs: choice of pixels for the retrievals
        self.mask_baddata = \
            np.any(
                np.dstack([self.refle[:, :, 0] < 0.5,
                           self.refle[:, :, 192] > 0.3,
                           self.refle[:, :, 192] < 1e-5,
                           self.refle[:, :, 103] < 0.1,
                           self.refle[:, :, 121] < 0.1]),
                axis=2
            )
        # anum = np.sum(~self.mask_baddata)  # count of good pixels used for retrieval  # FIXME not used

        self.refle[self.mask_baddata] = None

        # TODO: Alex writes the input to output_selected_spectrum.dat in case num == jline
        #       Since the Python code will run vectorized and not pixel-by pixel, this makes no sense here

        # Wet Snow Index (WSI) calculation
        self.WSI = (self.refle[:, :, 106] / self.refle[:, :, 101] - 1.0) * 100.0

        # # Cloud Index (CInka) calculation (commented out, as in FORTRAN)
        # CInka = self.refle[:, :, 121] / self.refle[:, :, 101]
        # GeoArray(CInka, self.im.meta.geotransform, self.im.meta.projection) \
        #     .save(os.path.join(path_outdir, 'cloud.bsq'))  # TODO compare with the one from Alex
        #
        # # add pixels with cloud index > 0.65 to bad data
        # mask_baddata[CInka > 0.65] = True
        # self.refle[mask_baddata] = None

        # Store reflectances in `ref007` array
        # TODO: This is only used the optional determination of the average reflectance for the scene
        #       (only for snow pixels) -> not yet implemented:
        # for ilka in range(224):
        #     ref007[num, ilka] = self.refle[ilka]

        # # Summing reflectances for averaging
        # sum_vals = np.zeros(224)
        # for L7 in range(224):
        #     sum_vals[L7] += self.refle[L7]

        # Measured reflectances at specific channels
        self.rmeas1 = self.refle[:, :, 0]
        self.rmeas2 = self.refle[:, :, 15]
        self.rmeas3 = self.refle[:, :, 103]
        self.rmeas4 = self.refle[:, :, 121]

        # Semi-infinite non-absorbing snow albedo retrieved:
        self.R0 = (self.rmeas3 ** self.im.meta.eps) * (self.rmeas4 ** (1.0 - self.im.meta.eps))
        self.fe = self.im.meta.u1 * self.im.meta.u2 / self.R0
        self.fe4 = self.fe

        # Spectral albedo at 1026 nm
        self.rs3 = (self.rmeas3 / self.R0) ** (1.0 / self.fe)

        # particle absorption length (micron)
        self.PAL = (np.log(self.rs3) ** 2) / self.im.meta.alpha3

    def run_clean_snow_grain_size_retrieval(self, output_level: int = 0):
        """Run the grain size retrieval for clean snow.

        :param output_level:
            Integer between 0 and 2 to set the level of additional outputs to be produced:
            0:  no additional outputs (default)
            1:  spectral spherical albedo and BOAR is produced
            2:  BBA (spherical/plane) and spectral plane albedo are produced

        :return:
        """
        if not 0 <= output_level <= 2:
            raise ValueError(f"The output level should be an integer between 0 and 3. Received: {output_level}.")

        # Diameter of grains (micron)
        D = self.PAL / 16.0

        # Snow specific surface area (SIGMA)
        SIGMA = 96.0 / (self.PAL * densi)  # FORTRAN: SIGMA=96./PAL/densi

        # Spectral snow parameters (derived for all 224 bands) #
        ########################################################

        # Spectral snow absorption coefficient (ALFA)
        # TODO ALFA = Spectral snow absorption coefficient?
        # FIXME this seems to use wavelength in microns in FORTRAN (ALFA=4.*pi*ak(k)/wave(k))
        ALFA = 4.0 * np.pi * ak / waves_nm  # (224,)

        # Snow grain size parameter (DM)
        DM = np.sqrt(self.PAL[:, :, None] * ALFA.reshape(1, 1, -1))  # (R, C, 224)

        # Spherical albedo (rs)
        rs = np.exp(-DM)  # (R, C, 224)

        # Plane albedo (rp)
        rp = rs * self.im.meta.amu1  # (R, C, 224)

        # BOA (Bottom of Atmosphere) reflectance (rboa)
        rboa = self.R0[:, :, None] * rs ** self.fe[:, :, None]  # (R, C, 224)

        # Broadband albedo calculation for different wavelengths
        # - band 0: VIS
        # - band 1: NIR
        # - band 2: SWIR
        rb = (
            samka.reshape(1, 1, -1) +
            bamka.reshape(1, 1, -1) *
            np.exp(-np.sqrt(pamka.reshape(1, 1, -1) * self.PAL[:, :, None]))
        )  # (R, C, 3)
        rbp = (
            samka.reshape(1, 1, -1)
            + bamka.reshape(1, 1, -1)
            * np.exp(-self.im.meta.u1 * np.sqrt(pamka.reshape(1, 1, -1) * self.PAL[:, :, None]))
        )

        # END OF RETRIEVAL FOR DRY and CLEAN snow

        # Conversion for printing: D in mm, SIGMA in m²/kg
        #     The retrieved grain size D and specific surface area SIGMA are converted into mm and m²/kg,
        #     respectively, before being written to the main output file (output_clean.dat).
        D_mm = D * 1e-3
        SIGM_m2kg = SIGMA * 1e3

        # TODO: improve this (variables first defines here and needed in BBA retrieval)
        self.D_mm = D_mm
        self.SIGM_m2kg = SIGM_m2kg

        #                     MAIN OUTPUT
        #                     ***********

        # Output to main file 'output_clean.dat'
        GeoArray(
            np.dstack([
                D_mm,
                SIGM_m2kg,
                self.WSI,
                self.R0,
                rb[:, :, 0],
                rb[:, :, 1],
                rb[:, :, 2],
                self.rmeas3,
                self.rmeas4,
                self.refle[:, :, 192]
            ]),
            self.im.meta.geotransform,
            self.im.meta.projection,
            bandnames=[
                'Diameter of grains in mm',
                'Snow specific surface area (SIGMA) in m²/kg',
                'Wet Snow Index(WSI)',
                'Semi-infinite non-absorbing snow albedo (R0)',
                'Broadband albedo VIS',
                'Broadband albedo NIR',
                'Broadband albedo SWIR',
                'TOA reflectance band 104',
                'TOA reflectance band 122',
                'TOA reflectance band 193',
            ]
        ).save(
            os.path.join(self.path_outdir, 'output_clean.bsq')
        )

        # TODO: make these outputs optional
        # Optional print to other files (for example, writing reflectance data for all 224 channels)
        # r, c = 500, 500  # FIXME harcoded row/column position
        r, c = 0, 0  # FIXME harcoded row/column position
        pixel_number = np.ravel_multi_index((r, c), self.refle.shape[:2])
        spectra = np.vstack([
            waves_nm,
            self.refle[r, c, :],
            rboa[r, c, :],
            rs[r, c, :],
            np.full(224, np.array(pixel_number))
            ]
        ).T
        np.savetxt(os.path.join(self.path_outdir, 'output_2_spectra.dat'), spectra, fmt='%1.9f', delimiter='\t')

        # print(spectra)

        # Optional further outputs based on the value of `IP`
        #     Depending on the value of IP, additional reflectance data (rs, rboa, rp, and broadband albedo rb and rbp)
        #     are written to different output files (output_3_albedo.dat, output_4_BOAR.dat, etc.).
        if output_level == 0:
            pass  # Skip additional output
        else:
            GeoArray(rs, self.im.meta.geotransform, self.im.meta.projection) \
                .save(os.path.join(self.path_outdir, 'output_3_albedo.bsq'))
            GeoArray(rboa, self.im.meta.geotransform, self.im.meta.projection) \
                .save(os.path.join(self.path_outdir, 'output_4_BOAR.bsq'))

            if output_level == 2:
                GeoArray(rp, self.im.meta.geotransform, self.im.meta.projection) \
                    .save(os.path.join(self.path_outdir, 'output_5_PA.bsq'))
                GeoArray(np.dstack([rb, rbp]), self.im.meta.geotransform, self.im.meta.projection) \
                    .save(os.path.join(self.path_outdir, 'output_6_BBA.bsq'))

    def run_polluted_snow_albedo_impurities_retrieval(self,
                                                      write_rs: bool = False,
                                                      write_rp: bool = False,
                                                      write_bba_plane: bool = False
                                                      ):
        """Run the estimation of snow albedo in the visible for polluted snow + properties of impurities in snow.

        :param write_rs:          enable to write output_impurity_rs.bsq (default: False)
        :param write_rp:          enable to write output_impurity_rp.bsq (default: False)
        :param write_bba_plane:   enable to write output_imp_bba_plane.bsq (default: False)
        :return:
        """
        # Constants
        alka1 = 418.42
        alka2 = 491.78

        def estimate_spherical_albedo(wavelength: float, r_meas: np.ndarray):
            re, alb, trans = atmos(wavelength, self.im.meta)
            c = (r_meas - re) / (self.R0 * trans)
            rs = np.full_like(c, np.nan)
            rs[~self.mask_baddata] = vectorized_brentq(self.fe[~self.mask_baddata], c[~self.mask_baddata], alb)

            # No retrieval conditions
            rs[np.any(np.dstack([
                np.isnan(rs),
                rs == 0.1,
                rs > 0.99
            ]), axis=2)] = np.nan
            # ars = c / (1.0 + c * alb)  # FIXME ars is never used
            rs[rs < 0] = 1.0

            return rs

        rs418 = estimate_spherical_albedo(alka1, self.rmeas1)
        rs492 = estimate_spherical_albedo(alka2, self.rmeas2)
        rs492[np.isnan(rs418)] = np.nan  # in FORTRAN, the computation of rs492 is skipped if rs418 is NaN

        # Estimate impurity load and AAE
        QU = np.log(rs418) / np.log(rs492)
        ratka = np.log(alka2 / alka1)
        Q = np.log(QU)

        # output: Impurity Absorption Angstrom Exponent (AAE)
        AAE = 2.0 * Q / ratka
        IT = np.where(AAE < 1.1, 1, 2).astype(float)
        IT[self.mask_baddata] = np.nan  # FIXME not sure if that is correct

        # output: Absorption strength
        PSIK = alka1 / 550.0
        finka = PSIK ** AAE
        # inverse microns
        ff3 = finka * (np.log(rs418)) ** 2
        ff2 = ff3 / self.PAL

        # inverse meters
        par = ff2 * 1e6  # TODO what is par?

        # Effective concentration of dust and soot (ppm)
        conc = np.full_like(par, np.nan)
        conc[IT == 1] = par[IT == 1] * 0.37429  # Soot concentration
        conc[IT == 2] = par[IT == 2] * 46.786  # Dust concentration
        IT[conc < 10.] = 0

        # TODO: improve this (variables first defined here and needed in BBA retrieval)
        self.AAE = AAE
        self.ff2 = ff2
        self.rs418 = rs418
        self.rs492 = rs492
        self.conc = conc  # FIXME FORTRAN computes [NaN, 5.65227747, 5.83288813] -> slight deviation
        self.IT = IT
        self.par = par

        # rub = self.R0 * rs418 ** self.fe
        # FIXME writing out.dat is commented out in the FORTRAN version, not needed according to Alex
        GeoArray(np.dstack([self.rmeas1, self.rmeas2, conc, par, AAE]),
                 self.im.meta.geotransform,
                 self.im.meta.projection,
                 bandnames=['TOA reflectance band 1',
                            'TOA reflectance band 16',
                            'Effective concentration of dust and soot (ppm)',
                            'PAR',  # TODO: What is this?
                            'Absorption Angstrom Exponent'
                            ]) \
            .save(os.path.join(self.path_outdir, 'out.bsq'))  # out.dat in FORTRAN

        # Spectral albedo estimation for polluted snow
        if any([write_rs, write_rp, write_bba_plane]):
            ALFA = 4.0 * np.pi * ak / waves_um  # (224,)
            BETKA = (waves_um.reshape(1, 1, -1) / 0.55) ** (-AAE[:, :, None])  # (R, C, 224)
            POLKA = np.sqrt(self.PAL[:, :, None] * ALFA.reshape(1, 1, -1) + ff3[:, :, None] * BETKA)  # (R, C, 224)
            albes = np.exp(-POLKA)
            albep = albes ** self.im.meta.u1
            polboa = albes ** self.fe[:, :, None]

            # TODO: is float 16 sufficient here? -> reduces IO time and file size
            if write_rs:
                (GeoArray(albes.astype(np.float32), self.im.meta.geotransform, self.im.meta.projection)
                 .save(os.path.join(self.path_outdir, 'output_impurity_rs.bsq')))
            if write_rp:
                (GeoArray(albep.astype(np.float32), self.im.meta.geotransform, self.im.meta.projection)
                 .save(os.path.join(self.path_outdir, 'output_impurity_rp.bsq')))
            if write_bba_plane:
                (GeoArray(polboa.astype(np.float32), self.im.meta.geotransform, self.im.meta.projection)
                 .save(os.path.join(self.path_outdir, 'output_imp_bba_plane.bsq')))

    def _estimate_broadband_albedo(self, wvl_start: float, wvl_end: float):
        # alternative numpy approach, but much slower than quad_vec
        # wvls = np.linspace(wvl_start, wvl_end, 100)
        # funti_vals = np.dstack([funti(wvl, self.ff2, self.AAE, self.PAL) for wvl in wvls])
        # aiv = np.trapezoid(funti_vals, wvls, axis=2)

        # compute aiv and aivp by integrating funti/funtip between wvl_start and wvl_end
        aiv = quad_vec(funti, wvl_start, wvl_end, args=(self.ff2, self.AAE, self.PAL))[0]  # (R, C)
        aivp = quad_vec(funtip, wvl_start, wvl_end, args=(self.im.meta.u1, self.ff2, self.AAE, self.PAL))[0]  # (R, C)
        aiw: float = funtik(wvl_start, wvl_end)

        # broadband albedo for clean snow
        bba = aiv / aiw  # (R, C)

        # broadband albedo for polluted snow
        bbap = aivp / aiw  # (R, C)

        return bba, bbap

    def run_polluted_snow_broadband_albedo_retrieval(self):
        """Estimate broadband albedo over polluted snow."""
        # Part 1: Estimation of broadband albedo in the range 0.3 - 2.45 microns
        bba3, bba3p = self._estimate_broadband_albedo(wvl_start=0.3, wvl_end=2.45)

        # Part 2: Estimation of broadband albedo in the range 0.3 - 0.7 microns
        bba1, bba1p = self._estimate_broadband_albedo(wvl_start=0.3, wvl_end=0.7)

        # Part 3: Estimation of broadband albedo in the range 0.7 - 2.45 microns
        bba2, bba2p = self._estimate_broadband_albedo(wvl_start=0.7, wvl_end=2.45)

        # mask_invalid = (
        #     np.any(
        #         np.dstack([
        #             self.rs418 > 0.99,
        #             self.rs492 >= 0.99,
        #             self.R0 < 0.5,
        #             self.conc < 20.
        #         ]),
        #         axis=2
        #     ))

        # TODO: set results at mask_invalid to nodata

        # output_impurity.dat
        # write(1961,*) alat,alon,D,SIGM,WSI,R0, bba1,bba2,bba3,IT,AAE,conc,par,rmeas1,rmeas2,rs418,rs492

        _data = (np.dstack([self.D_mm,
                            self.SIGM_m2kg,
                            self.WSI,
                            self.R0,
                            bba1,
                            bba2,
                            bba3,
                            self.IT,
                            self.AAE,
                            self.conc,
                            self.par,
                            self.rmeas1,
                            self.rmeas2,
                            self.rs418,
                            self.rs492,
                            ])
                 .astype(np.float32))
        # _data[mask_invalid] = np.nan
        GeoArray(_data,
                 self.im.meta.geotransform,
                 self.im.meta.projection,
                 bandnames=['Diameter of grains in mm',
                            'Snow specific surface area (SIGMA) in m²/kg',
                            'Wet Snow Index(WSI)',
                            'Semi-infinite non-absorbing snow albedo (R0)',
                            'Broadband albedo over clean snow in the range 0.3 - 0.7 microns',
                            'Broadband albedo over clean snow in the range 0.7 - 2.45 microns',
                            'Broadband albedo over clean snow in the range 0.3 - 2.45 microns',
                            'Impurity Absorption Angstrom Exponent (AAE) regions (1 for AAE<1.1 else 2)',  # TODO (?)
                            'Impurity Absorption Angstrom Exponent (AAE)',
                            'Effective concentration of dust and soot (ppm)',
                            'PAR (FF2 * 1e6)',  # TODO: What is this?
                            'TOA reflectance band 1',
                            'TOA reflectance band 16',
                            'Spherical albedo at 418.42 nm',
                            'Spherical albedo at 491.78 nm'
                            ]) \
            .save(os.path.join(self.path_outdir, 'output_impurity.bsq'))  # output_impurity.dat in FORTRAN

        # # output_reflectances.dat
        # # write(1964,*)alat,alon, rmeas1,rmeas2,rmeas3,rmeas4, refle (133),refle (150),refle(193)
        # GeoArray(np.dstack([self.rmeas1,
        #                     self.rmeas2,
        #                     self.rmeas3,
        #                     self.rmeas4,
        #                     self.refle[:, :, 132],
        #                     self.refle[:, :, 149],
        #                     self.refle[:, :, 192]
        #                     ])
        #          .astype(np.float32),
        #          self.im.meta.geotransform,
        #          self.im.meta.projection,
        #          bandnames=['TOA reflectance band 1',
        #                     'TOA reflectance band 16',
        #                     'TOA reflectance band 104',
        #                     'TOA reflectance band 122',
        #                     'TOA reflectance band 133',
        #                     'TOA reflectance band 150',
        #                     'TOA reflectance band 193',
        #                     ]) \
        #     .save(os.path.join(self.path_outdir, 'output_reflectances.bsq'))  # output_reflectances.dat in FORTRAN

        # output_BBA.dat
        # if ( isnan(bba3)) go to 1
        # if (bba3.gt.1.) go to 1
        # c write(1928,*) alat,alon,bba3,bba2,bba1,bba3p,bba2p,bba1p
        GeoArray(np.dstack([bba3,
                            bba2,
                            bba1,
                            bba3p,
                            bba2p,
                            bba1p
                            ])
                 .astype(np.float32),
                 self.im.meta.geotransform,
                 self.im.meta.projection,
                 bandnames=['Broadband albedo over clean snow in the range 0.3 - 2.45 microns',
                            'Broadband albedo over clean snow in the range 0.7 - 2.45 microns',
                            'Broadband albedo over clean snow in the range 0.3 - 0.7 microns',
                            'Broadband albedo over polluted snow in the range 0.3 - 2.45 microns',
                            'Broadband albedo over polluted snow in the range 0.7 - 2.45 microns',
                            'Broadband albedo over polluted snow in the range 0.3 - 0.7 microns',
                            ]) \
            .save(os.path.join(self.path_outdir, 'output_BBA.bsq'))  # output_BBA.dat in FORTRAN
