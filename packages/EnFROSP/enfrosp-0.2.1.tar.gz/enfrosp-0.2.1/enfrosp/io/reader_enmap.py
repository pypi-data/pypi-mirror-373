"""Reader module for EnMAP L1C data."""

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


import fnmatch
import os
import shutil
from datetime import datetime
from tempfile import TemporaryDirectory
from typing import List
from xml.etree import ElementTree
from zipfile import is_zipfile, ZipFile
from warnings import warn

import numpy as np
from osgeo import gdal

from . import path_data
from ..retrieval.constants import OE


class EnMAPL1C(object):
    """Reader class for EnMAP L1C data."""

    def __init__(self,
                 path_zipfile: str,
                 band_list: list = None):
        """Get an instance of EnMAPL1C.

        :param path_zipfile:    file path of the EnMAP L1C ZIP-file as downloaded from the EnMAP ground segment.
        :param band_list:       band list of the bands to be considered in the reader (default: None, i.e., all)
        """
        fn = os.path.basename(path_zipfile)

        if not os.path.exists(path_zipfile):
            raise FileNotFoundError(path_zipfile)

        if not is_zipfile(path_zipfile):
            raise ValueError(f"The provided ZIP-file at {path_zipfile} is not a valid ZIP-file.")

        if not fn.startswith('ENMAP01-____L1C-'):
            raise ValueError(fn, "The name of the provided ZIP-file should start with 'ENMAP01-____L1C'.")

        # privates
        self._dn = None
        self._toa_radiance = None
        self._toa_reflectance = None

        self.path_zipfile = path_zipfile
        self.band_list = band_list

        with ZipFile(path_zipfile) as zF:
            self.filelist_within_zip = [i.filename for i in zF.infolist() if i.file_size != 0]
            self.filelist = [os.path.abspath(os.path.join(path_zipfile, i)) for i in self.filelist_within_zip]

        self.path_vswir = self._get_image_filename('*SPECTRAL_IMAGE')

        self.meta: EnMAPL1CMetadata = self._read_meta()

    def _get_image_filename(self, matching_exp: str):
        exp_exts = ['.TIF', '.GEOTIFF', '.BSQ', '.BIL', '.BIP', 'JPEG2000', '.JP2']
        exp_exts.extend([i.lower() for i in exp_exts])

        matches = []
        for ext in exp_exts:
            if matches:
                break
            matches.extend(fnmatch.filter(self.filelist, f'{matching_exp}{ext}'))

        if len(matches) > 1:
            raise RuntimeError(f"The given matching expression matches with multiple input files: {matches}")

        if matches:
            return f'{os.sep}vsizip{os.sep}{matches[0]}'
        else:
            raise RuntimeError(f"No file matching the expression '{matching_exp}' and one of the supported file "
                               f"extensions ({exp_exts}) found within the given ZIP-file.")

    def _read_meta(self) -> 'EnMAPL1CMetadata':
        p_internal_xml = fnmatch.filter(self.filelist_within_zip, '*METADATA.XML')[0]

        with TemporaryDirectory() as td, ZipFile(self.path_zipfile, 'r') as zF:
            p_extr = os.path.join(td, os.path.basename(p_internal_xml))

            with zF.open(p_internal_xml) as iF, open(p_extr, 'wb') as oF:
                shutil.copyfileobj(iF, oF)

            meta = EnMAPL1CMetadata(p_extr, self.path_vswir, self.band_list)

        return meta

    def create_vrt(self,
                   outdir: str,
                   fn_suffix: str = '',
                   srcNodata: int = 0,
                   band_list: List[int] = None
                   ) -> None:
        """Create a VRT file pointing to the given raster image path.

        :param outdir:              output directory path
        :param fn_suffix:           filename suffix to be inserted before the file extension. If set to 'RGB', the
                                    'bandlist' parameter must also be set and a VRT that only contains these bands is
                                    written.
        :param srcNodata:           nodata value of the input raster file (default: 0)
        :param band_list:            list of bands to be included in the VRT (if set to None, all bands are included)
        """
        if fn_suffix == 'RGB':
            if not band_list:
                raise ValueError("Provide a band list when setting fn_suffix to 'RGB'.")

            self.meta.bandnames = [self.meta.bandnames[i] for i in band_list]

        bN = os.path.basename(self.path_vswir)
        fn = f'{bN}_{fn_suffix}.vrt' if fn_suffix else f'{bN}.vrt'
        path_vrt = os.path.join(outdir, fn)

        with gdal.Open(self.path_vswir) as ds:
            # create a VRT from all surface reflectance bands
            vrt_options = gdal.BuildVRTOptions(bandList=band_list, srcNodata=srcNodata)
            vrt: gdal.Dataset
            with gdal.BuildVRT(path_vrt, ds, options=vrt_options) as vrt:
                vrt.SetMetadataItem('wavelength', '{' + ', '.join(self.meta.wavelength.astype(str)) + '}', 'ENVI')
                vrt.SetMetadataItem('wavelength_units', 'nanometers', 'ENVI')
                vrt.SetMetadataItem('fwhm', '{' + ', '.join(self.meta.fwhm.astype(str)) + '}', 'ENVI')
                if srcNodata is not None:
                    vrt.SetMetadataItem('data ignore value', str(0), 'ENVI')

                # set band names, gains, offsets, nodata value, and color interpretation
                for i, bandname in zip(range(vrt.RasterCount), self.meta.bandnames):
                    band: gdal.Band
                    band = vrt.GetRasterBand(i + 1)
                    band.SetDescription(bandname)
                    band.SetScale(float(self.meta.gains[i]))
                    band.SetOffset(float(self.meta.offsets[i]))

                    if fn_suffix == 'RGB':
                        if i == 0:
                            band.SetColorInterpretation(gdal.GCI_RedBand)
                        if i == 1:
                            band.SetColorInterpretation(gdal.GCI_GreenBand)
                        if i == 2:
                            band.SetColorInterpretation(gdal.GCI_BlueBand)

    @property
    def dn(self):
        """Get digital numbers as stored in the EnMAP L1C product."""
        if self._dn is None:
            ds: gdal.Dataset
            bl = [int(i) + 1 for i in self.band_list] if self.band_list else None
            with (gdal.Open(self.path_vswir) as ds):
                _dn = ds.ReadAsArray(band_list=bl).astype(float)
                if _dn.ndim == 3:
                    self._dn = np.moveaxis(_dn, 0, -1)
                else:
                    self._dn = _dn.reshape(*_dn.shape, 1)

            # # visualize intermediate results
            # gA_dn = GeoArray(self._dn)
            # gA_dn.meta.band_meta['wavelength'] = self.meta.wavelength
            # gA_dn.show_zprofile(500, 500, title='EnFROSP DNs')
            # GeoArray('/home/gfz-fe/scheffler/temp/EnFROSP/'
            #          'enmapbox_toarad.bsq').show_zprofile(500, 500, title='EnMAP-Box TOA radiance')

        return self._dn

    @property
    def toa_radiance(self) -> np.ndarray:
        """Get TOA radiance in W/m^2/sr/nm."""
        if self._toa_radiance is None:
            mask = np.any(self.dn, axis=2) if self.dn.ndim == 3 else self.dn != 0
            toa_rad = self.dn * self.meta.gains.reshape(1, 1, -1) + self.meta.offsets.reshape(1, 1, -1)
            toa_rad[~mask] = 0

            # avoid that offsets are applied to 0-DN pixel values -> they should also result in 0-radiance
            toa_rad[self.dn == 0] = 0

            self._toa_radiance = toa_rad

            # # visualize intermediate results
            # gA_toa_rad = GeoArray(self._toa_radiance, nodata=0)
            # gA_toa_rad.meta.band_meta['wavelength'] = self.meta.wavelength
            # gA_toa_rad.show_zprofile(500, 500, title='EnFROSP TOA radiance')

        return self._toa_radiance

    @property
    def toa_reflectance(self) -> np.ndarray:
        """Get TOA reflectance scaled between 0 and 10000."""
        if self._toa_reflectance is None:
            # EQUATION: toaRef = (scale_factor * np.pi * toaRad * earthSunDist**2) / (solIrr * np.cos(zenithAngleDeg))
            sun_zenith = 90 - self.meta.center_sun_elevation_angle
            band_factors = ((10000 * np.pi * self.meta.earth_sun_distance ** 2) /
                            (np.cos(np.radians(sun_zenith)) * self.meta.solar_irr.reshape(1, 1, -1)))
            toa_ref = (band_factors * self.toa_radiance).astype(np.int16)

            self._toa_reflectance = toa_ref

            # # check difference between Karls TOA reflectance and the one from EnFROSP
            # # -> Karls result contains pixels where one or both EnMAP detectors are 0
            # #    but apart from that only slight differences due to float precision errors
            # toa_ref_karl = GeoArray('/home/gfz-fe/scheffler/python/enfrosp/code_alex/REFLECTANCE.bsq')[:]
            #
            # px_toa_ref = toa_ref[500, 500, :]
            # px_toa_ref_karl = toa_ref_karl[500, 500, :]
            #
            # diff = toa_ref_karl - toa_ref
            # mask = np.any(np.abs(diff) > 3, axis=2)
            # GeoArray(mask).show()
            # xypositions = np.argwhere(mask)
            #
            # bands = []
            # for i in range(xypositions.shape[0]):
            #     pos = xypositions[i, :]
            #     bands.append(np.argwhere(toa_ref_karl[*pos, :] - toa_ref[*pos, :]))
            #
            # pos2 = xypositions[1, :]
            # toa_ref_karl[*pos2, :] - toa_ref[*pos2, :]  # somehow there are large diffs
            # GeoArray(toa_ref_karl).show_zprofile(*pos2)
            # GeoArray(toa_ref).show_zprofile(*pos2)

            # # visualize intermediate results
            # GeoArray('/home/gfz-fe/scheffler/temp/EnFROSP/'
            #          'REFLECTANCE.bsq').show_zprofile(500, 500, title='Karl TOA reflectance')
            # gA_toa_ref = GeoArray(toa_ref, nodata=0)
            # gA_toa_ref.meta.band_meta['wavelength'] = self.meta.wavelength
            # gA_toa_ref.show_zprofile(500, 500, title='EnFROSP TOA reflectance')
            # gA_toa_ref.show()
            #
            # GeoArray(irrad.reshape(1, -1)).show_xprofile(0, 0, title='solar irradiance')

        return self._toa_reflectance


class EnMAPL1CMetadata(object):
    def __init__(self, path_xml: str, path_vswir: str, band_list: list):
        self._xml = ElementTree.parse(path_xml).getroot()
        self.band_list = band_list

        ds: gdal.Dataset
        with gdal.Open(path_vswir) as ds:
            self.geotransform = ds.GetGeoTransform()
            self.projection = ds.GetProjection()

        def findall(key):
            return [item.text for item in
                    self._xml.findall(f'specific/bandCharacterisation/bandID/{key}OfBand')]

        wvl = np.array(findall('wavelengthCenter'), float)
        fwhm = np.array(findall('FWHM'), float)
        gains = np.array(findall('Gain'), float)
        offsets = np.array(findall('Offset'), float)

        self.wavelength = wvl if not band_list else wvl[band_list]
        self.fwhm = fwhm if not self.band_list else fwhm[self.band_list]
        self.gains = gains if not self.band_list else gains[self.band_list]
        self.offsets = offsets if not self.band_list else offsets[self.band_list]
        self.solar_irr = self._compute_solar_irradiance()
        self.procL = self._xml.find('base/level').text
        self.bandnames = [f'Band {b} ({w} nm)' for b, w in zip(range(1, len(wvl) + 1), wvl)]
        self.coords_xy = {p.find('frame').text: (float(p.find('longitude').text),
                                                 float(p.find('latitude').text))
                          for p in self._xml.findall("base/spatialCoverage/boundingPolygon/point")}
        self.acquisition_datetime = datetime.strptime(
            self._xml.find("base/temporalCoverage/startTime").text, '%Y-%m-%dT%H:%M:%S.%fZ')
        self.processing_datetime = datetime.strptime(
            self._xml.find("specific/processingDateTime").text, '%Y-%m-%dT%H:%M:%S.%fZ')
        self.earth_sun_distance = self._get_earth_sun_distance()  # Karl's ESD only has 6 digits after comma
        self.center_sun_elevation_angle = float(self._xml.find("specific/sunElevationAngle/center").text)
        self.center_sun_azimuth_angle = float(self._xml.find("specific/sunAzimuthAngle/center").text)
        self.center_across_off_nadir_angle = float(self._xml.find("specific/acrossOffNadirAngle/center").text)
        self.center_along_off_nadir_angle = float(self._xml.find("specific/alongOffNadirAngle/center").text)
        self.center_scene_azimuth_angle = float(self._xml.find("specific/sceneAzimuthAngle/center").text)
        self.mean_ground_elevation = float(self._xml.find("specific/meanGroundElevation").text)
        self.ozone = float(self._xml.find("processing/ozoneValue").text)
        self.aot = float(self._xml.find("specific/qualityFlag/sceneAOT").text)/1000  # scale factor 1000?
        self.water_vapour = float(self._xml.find("specific/qualityFlag/sceneWV").text)  # scale factor 1000?

        # TODO: So far, Alex uses a fixed AOT value of 0.05 and Angstrom exponent of 1.3
        #       -> Can we use the AOT value from the EnMAP metadata directly?
        #           - EnMAP metadata provides AOT=164, but Alex uses 0.05 via key.dat
        self.vza = self.center_across_off_nadir_angle
        self.vaa = self.center_scene_azimuth_angle
        self.sza = 90 - self.center_sun_elevation_angle
        self.saa = self.center_sun_azimuth_angle
        warn('Using HARDCODED AOT value that likely does not fit to the current scene!', RuntimeWarning)
        self.aot = 0.05  # FIXME overwrites value from scene metadata
        warn('Using HARDCODED Angström exponent that likely does not fit to the current scene!', RuntimeWarning)
        self.angst = 1.3  # Angström exponent  # FIXME: hardcoded
        self.tau550 = self.aot

        # angular variables
        self.raa = 180.0 - (self.saa - self.vaa)
        self.amu1 = np.cos(self.sza * np.pi / 180.0)
        self.amu2 = np.cos(self.vza * np.pi / 180.0)
        self.as1 = np.sin(self.sza * np.pi / 180.0)
        self.as2 = np.sin(self.vza * np.pi / 180.0)
        self.cofi = np.cos(self.raa * np.pi / 180.0)

        self.u1 = 0.6 * self.amu1 + (1.0 + np.sqrt(self.amu1)) / 3.0
        self.u2 = 0.6 * self.amu2 + (1.0 + np.sqrt(self.amu2)) / 3.0

        self.co = -self.amu1 * self.amu2 + self.as1 * self.as2 * self.cofi
        self.scat = np.acos(self.co) * 180.0 / np.pi  # Scattering angle in degrees

        # Wavelengths and absorption coefficients for dry and clean snow retrieval
        self.alam3 = 1.02566003  # Microns
        self.alam4 = 1.23496997  # Microns
        self.akap3 = 2.295e-6
        self.akap4 = 1.175e-5

        # Bulk ice absorption coefficient
        self.alpha3 = 4.0 * np.pi * self.akap3 / self.alam3
        self.alpha4 = 4.0 * np.pi * self.akap4 / self.alam4

        # Spectral parameter
        self.BE = np.sqrt(self.alpha3 / self.alpha4)
        self.eps = 1.0 / (1.0 - self.BE)

    def _compute_solar_irradiance(self):
        """Get solar irradiance for EnMAP in W/m^2/nm."""
        sol_irr = np.loadtxt(os.path.join(path_data, 'SSI_TSIS-1__350-2500nm.txt'), skiprows=6, usecols=[1]) * OE
        wvl_full = np.arange(350, 2500, .1)
        irrad = np.zeros_like(self.wavelength)

        def gaussian(x, cwl, fwhm):
            sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
            return np.exp(-((x - cwl) ** 2) / (2 * sigma ** 2))

        for i, (cwl, fwhm) in enumerate(zip(self.wavelength, self.fwhm)):
            srf = gaussian(wvl_full, cwl, fwhm)
            irrad[i] = np.sum(sol_irr * srf) / np.sum(srf)

        return irrad

    def _get_earth_sun_distance(self):
        """Get earth-sun distance (requires file of pre-calculated earth sun distance per day)."""
        distances = {str(date).strip(): float(esd) for date, esd in
                     np.loadtxt(os.path.join(path_data, "Earth_Sun_distances_per_day_edited__1980_2030.csv"),
                                delimiter=',', dtype=str)}
        return distances[self.acquisition_datetime.strftime('%Y-%m-%d')]
