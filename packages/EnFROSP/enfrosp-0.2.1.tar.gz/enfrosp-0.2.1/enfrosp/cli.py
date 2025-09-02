#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Console script for enfrosp."""

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

import argparse
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
import sys
import os

from enfrosp import __version__
from enfrosp import Retrieval


def get_enfrosp_argparser():
    """Get a console argument parser for EnFROSP."""
    parser = ArgumentParser(
        prog='enfrosp',
        description='EnFROSP command line argument parser',
        epilog="use '>>> enfrosp -h' for detailed documentation and usage hints."
    )
    parser.add_argument('--version', action='version', version=__version__)

    #####################
    # GENERAL ARGUMENTS #
    #####################

    general_opts_parser = ArgumentParser(add_help=False)
    gop_p = general_opts_parser.add_argument

    gop_p('-i', '--path_enmap_zipfile', type=str, default=None,
          help='input path of the EnMAP L1C image to be processed (zip-archive)')
    gop_p('-o', '--path_outdir', nargs='?', type=str, default=os.path.abspath(os.path.curdir),
          help='output directory where the processed data is saved')

    retr_subparser = _add_retrieve_subparser(parser)
    retr_allsubparsers = retr_subparser.add_subparsers()

    _add_clean_snow_grain_size_subparser(retr_allsubparsers, general_opts_parser)
    _add_polluted_snow_albedo_impurities_subparser(retr_allsubparsers, general_opts_parser)
    _add_polluted_snow_broadband_albedo_subparser(retr_allsubparsers, general_opts_parser)

    return parser


def _add_retrieve_subparser(parent_parser):
    subparsers = parent_parser.add_subparsers()

    retr_subparser = subparsers.add_parser(
        'retrieve',
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Retrieve several snow properties from EnMAP L1C data.',
        help="retrieve snow properties from EnMAP L1C data (sub argument parser) - "
             "use 'enfrosp retrieve -h' for documentation and usage hints")

    return retr_subparser


def _add_clean_snow_grain_size_subparser(parent_parser, general_opts_parser):
    parser = parent_parser.add_parser(
        'clean_snow_grain_size',
        parents=[general_opts_parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Retrieve clean snow grain size.',
        help="retrieve clean snow grain size (sub argument parser) - "
             "use 'enfrosp retrieve clean_snow_grain_size -h' for documentation and usage hints"
    )
    parser.set_defaults(func=retrieve_clean_snow_grain_size)


def _add_polluted_snow_albedo_impurities_subparser(parent_parser, general_opts_parser):
    parser = parent_parser.add_parser(
        'polluted_snow_albedo_impurities',
        parents=[general_opts_parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Retrieve polluted snow albedo and impurities.',
        help="retrieve polluted snow albedo and impurities (sub argument parser) - "
             "use 'enfrosp retrieve clean_snow_grain_size -h' for documentation and usage hints"
    )
    parser.set_defaults(func=retrieve_polluted_snow_albedo_impurities)


def _add_polluted_snow_broadband_albedo_subparser(parent_parser, general_opts_parser):
    parser = parent_parser.add_parser(
        'polluted_snow_broadband_albedo',
        parents=[general_opts_parser],
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Retrieve polluted snow broadband albedo.',
        help="retrieve polluted snow broadband albedo (sub argument parser) - "
             "use 'enfrosp retrieve polluted_snow_broadband_albedo -h' for documentation and usage hints"
    )
    parser.set_defaults(func=retrieve_polluted_snow_broadband_albedo)


def retrieve_clean_snow_grain_size(cli_args: Namespace):
    Retrieval(
        path_enmap_zipfile=cli_args.path_enmap_zipfile,
        path_outdir=cli_args.path_outdir
    ).run_clean_snow_grain_size_retrieval(
        output_level=2  # FIXME hardcoded
    )


def retrieve_polluted_snow_albedo_impurities(cli_args: Namespace):
    Retrieval(
        path_enmap_zipfile=cli_args.path_enmap_zipfile,
        path_outdir=cli_args.path_outdir
    ).run_polluted_snow_albedo_impurities_retrieval(
        write_rs=True,  # FIXME hardcoded
        write_rp=True,  # FIXME hardcoded
        write_bba_plane=True  # FIXME hardcoded
    )


def retrieve_polluted_snow_broadband_albedo(cli_args: Namespace):
    rt = Retrieval(
        path_enmap_zipfile=cli_args.path_enmap_zipfile,
        path_outdir=cli_args.path_outdir
    )
    rt.run_clean_snow_grain_size_retrieval(output_level=0)
    rt.run_polluted_snow_albedo_impurities_retrieval()
    rt.run_polluted_snow_broadband_albedo_retrieval()


def _find_deepest_parser(parser: argparse.ArgumentParser, argv: list):
    current = parser
    remaining = list(argv)

    while remaining:
        sp_actions = [a for a in current._actions if isinstance(a, argparse._SubParsersAction)]
        if sp_actions:
            next_parser = sp_actions[0].choices.get(remaining[0])
            if next_parser:
                current = next_parser
                remaining = remaining[1:]
            else:
                break
        else:
            break

    return current, remaining


def main(parsed_args: Namespace = None) -> int:
    if parsed_args is None:
        parser = get_enfrosp_argparser()
        target_parser, argv = _find_deepest_parser(parser, sys.argv[1:])

        if argv:
            parsed_args = parser.parse_args()
        else:
            target_parser.print_help()
            return 0

    parsed_args.func(parsed_args)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
