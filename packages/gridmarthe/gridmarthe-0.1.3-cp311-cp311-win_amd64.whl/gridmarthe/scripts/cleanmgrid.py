#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#
#    This file is part of gridmarthe.
#
#    gridmarthe is a python library to manage grid files for 
#    MARTHE hydrogeological computer code from French Geological Survey (BRGM).
#    Copyright (C) 2024  BRGM
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# objectif, lire l'ensemble des fichiers maillés et les corriger.
# sinon, a minima le permh

import os, sys, re, shutil, textwrap
from pathlib import Path
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from gridmarthe.__version__ import _copyleft


# ext: VARIABLE_NAME in FRench
MARTGRID_FILES = {
    'permh' : 'PERMEAB',
    'debit' : 'DEBIT',
    'charg' : 'CHARGE',
    'emmca' : 'EMMAG_CAPT',
    'emmli' : 'EMMAG_LIBR',
    'zgeom' : 'ZONE_GEOM',
    'hsubs' : 'H_SUBSTRAT',
    'equip' : 'Z_EQUIPOT',
    'topog' : 'H_TOPOGR',
    'zonep' : 'ZONE_SOL',
    'zonei' : 'ZONE_IRRIG',
    'idebo' : 'IND_DEBORD',
    'sepon' : 'SUBS_EPONTE',
    'salini': 'SALINITE',
    'poros' : 'POROSITE',
    'satur' : 'SATURAT',
    'salext': 'SALIN_EXT',
    'conce' : 'CONCENTR',
    'conex' : 'CONCEN_EXT',
    'tempe' : 'TEMPERAT',
    'temex' : 'TEMPER_EXT',
    'mconc' : 'MASS_CONCEN',
    'porfx' : 'PORO_FIX',
    'aff_r' : 'AFFLU_RIVI',
    'trc_r' : 'TRONC_RIVI',
    'lon_r' : 'LONG_RIVI',
    'lar_r' : 'LARG_RIVI',
    'hau_r' : 'HAUTEU_RIVI',
    'epai_r': 'EPAI_LIT_RIV',
    'perm_r': 'PERM_LIT_RIVI',
    'qext_r': 'Q_EXTER_RIVI',
    'flo_r' : 'DEBIT_RIVI',
    'qamon' : 'Q_AMONT_RIVI',
    'rug_r' : 'RUGOS_RIVI',
    'pnt_r' : 'PENTE_RIVI',
    'fon_r' : 'FOND_RIVI',
    'conc_r': 'CONCEN_RIVI',
    'cext_r': 'CONC_EXT_RIVI',
    'qmas_r': 'QMASS_RIVI',
    'mass_r': 'MASSE_RIVI',
    'aff_d' : 'AFFLU_DRAIN',
    'trc_d' : 'TRONC_DRAIN',
    'lon_d' : 'LONG_DRAIN',
    'z_dra' : 'ALTIT_DRAIN',
    'meteo' : 'ZONE_METEO',
    'd_ava' : 'DIRECT_AVAL',
    'v_rui' : 'VITESS_RUISS',
    'ruiss' : 'RUISSEL',
    'recha' : 'RECHARGE',
    's_bvext' : 'SUPERF_BV_EXT',
    'z_bvext' : 'NZON_RIV_EXT',
}


def parse_args():
    """ CLI program """
    parser = ArgumentParser(
        prog='cleanmgrid',
        formatter_class=RawDescriptionHelpFormatter,
        description="Clean marthe grid file for miswritten attributes. Only works for marthe grid v9.0 (a check is performed and <v9 are skipped)",
        epilog=textwrap.dedent(_copyleft)
    )
    
    parser.add_argument('opt', metavar='PATH_TO_FILE', type=str, nargs=1, help='PATH_TO_FILE can be a relative path, if it ends with ".rma" all grid file in rma project will be processed.')
    parser.add_argument('--layer' , '-l', type=int, default=None, help='Number of layer. Only if PATH_TO_FILE is *NOT* a rma file. Otherwise, it will be parsed from Marthe\'s files.')
    parser.add_argument('--grid'  , '-g', type=int, default=None, help='Number of nested grid. Only if PATH_TO_FILE is *NOT* a rma file. Otherwise, it will be parsed from Marthe\'s files.')
    parser.add_argument('--output', '-o', type=str, default=None, help='Output file name (without subdir if any). Only if PATH_TO_FILE is a single grid file and *NOT* a rma file. Otherwise, all files will be bakup and clean')
    parser.add_argument(
        '--no_overwrite' , '-n',
        action="store_const", const=True, default=False,
        help='Do no overwrite file, add `.fix` extension. By default file is bakup and then overwrite.'
    )
    
    args = parser.parse_args()
    
    if not args.opt[0].endswith('rma') and (args.layer is None or args.grid is None):
        print('File {} is not a Marthe project ("*.rma"). Please provide `-l` and `-g` argument when using on a single grid file. See `cleanmgrid -h`')
        sys.exit(1)

    return args


def fread(file):
    with open(file, 'r', encoding='ISO-8859-1') as f:
        content = f.read()
    return content


def scan_vers_semi(str_semi):
    if re.search(r'Marthe_Grid.*Version=9\.0', str_semi):
        version = 9.0
    elif re.search(r'Semis.*8\.0', str_semi):
        version = 8.0
    else:
        print('Unknown Marthe Grid version.')
        version = 9999.
    return version


def parse_geom(layer_str:str):
    layers = re.findall(r'Cou=\s*(\d+);', layer_str)
    ngrid  = re.findall(r'(\d+)=Nombre.*[g|G]igognes', layer_str)[0]
    # nlay = max(map(int, layers))
    return layers, ngrid


def read_rma(frma):
    rma = fread(frma)
    files = re.finditer(r'(.*)  =\s+[A-z]', rma)
    files = [ x.group(1).strip().replace('=', '') for x in files]
    files = [ x for x in files if len(x) > 0]
    return files


def read_files_from_rma(frma):
    
    # root = os.path.dirname(frma)
    root = os.getcwd()
    files = read_rma(frma)
    
    # get all gridded files
    res = []
    for fgrid in files:
        # files[fgrid] = re.findall(r'(.*\.[A-z]*) *=.*Perméabilité', rma)[0],
        kind = os.path.splitext(fgrid)[-1].replace('.', '')
        if kind in MARTGRID_FILES.keys():
            res.append((kind, fgrid, MARTGRID_FILES.get(kind)))
    
    # get layers, ngrid infos
    layer =  [x for x in files if x.endswith('layer')][0]
    layer =  fread("{}/{}".format(root, layer))
    layers, ngrid = parse_geom(layer)
    return res, layers, ngrid


def insert_str(string, index, insert_str):
    return string[:index] + insert_str + string[index:]


def search_index(string, pattern):
    # get research start, match end, research pattern and result
    idx = [(m.start(0), m.end(1), m.group(0).replace(m.group(1), ''), m.group(1)) for m in re.finditer(pattern, string)]
    return idx


def clean_grid_str(string: str, pattern: str, fillvalue: str|list, test=lambda x: len(x) < 1):
    """ Search for a pattern and replace with a unique or varying value
    if match satisfy a custom test
    """
    matches = search_index(string, pattern)
    new_str = string
    
    if len(matches) == 0:
        # nothing to clean // or bug with regex :)
        return new_str

    if isinstance(fillvalue, list):
        if len(fillvalue) != len(matches):
            raise ValueError('Length for fillvalue and match differs. Cannot replace with fillvalues')

    if test(matches[0][-1]):
        if isinstance(fillvalue, list):
            # sub one by one
            for match, fill in zip(matches, fillvalue):
                before = new_str[:match[0]]
                after = new_str[match[0]:]
                after = re.sub(pattern, '{}{}'.format(match[2], str(fill)), after, count=1)
                new_str = before + after
        else:
            # unique value, sub all at once
            new_str = re.sub(pattern, '{}{}'.format(matches[0][2], fillvalue), new_str)
    return new_str


def write_res(string, fname):
    with open(f'{str(fname)}', 'w', encoding='ISO-8859-1') as f:
        f.write(string)
    return 0


def main():
    """ CLEANMGRID """
    
    args = parse_args()
    finputs = args.opt[0]
    
    root = os.path.dirname(finputs) # edit no, if not ./MONMODEL.rma but MONMODEL.rma, dirname is '' so /bakup => not allowed in linux non root
    if root == '' or root is None:
        root = os.getcwd()
    if args.output is None and not args.no_overwrite:
        os.makedirs('{}/bakup'.format(root), exist_ok=True)
    filename = os.path.split(finputs)[-1]
    
    # --- get geom
    if finputs.endswith('rma'):
        files, layers, ngrid = read_files_from_rma(finputs)
    else:
        ext = os.path.splitext(finputs)[-1].replace('.', '')
        key = MARTGRID_FILES.get(ext)
        if key is None:
            print('Unkwnown key field for grid kind {} (file: {})'.format(ext, finputs))
            sys.exit(1)
        files, layers, ngrid = [(ext, filename, key)], list(range(1, args.layer + 1)), str(args.grid)
    
    
    for ext, file, key in files:
        
        # --- treatment of each grid file --- #
        # --- read and scan var
        fpath = Path(root, file)
        grid  = fread(fpath)
        version = scan_vers_semi(grid)
        fileout = fpath
        
        if version != 9.0:
            continue
        
        # --- clean attributes:
        grid = clean_grid_str(grid, r'\nField=(.?)', key, test=lambda x: len(x) < 1 )
        grid = clean_grid_str(grid, pattern=r'\nLayer=([0-9]*)'  , fillvalue=layers * (int(ngrid)+1)   , test=lambda x: int(x) == 0)
        grid = clean_grid_str(grid, pattern=r'Max_Layer=([0-9]*)', fillvalue=str(max(map(int, layers))), test=lambda x: int(x) == 0)
        # grid = clean_grid_str(grid, pattern=r'Nest_grid=([0-9]*)', fillvalue=list(range(int(ngrid)+1)) , test=lambda x: int(x) == 0) # in multilayer not good, miss repetition of layers
        x = [item for item in list(range(int(ngrid)+1)) for _ in range(max(map(int,layers)))] # equiv of np.repeat
        grid = clean_grid_str(grid, pattern=r'Nest_grid=([0-9]*)', fillvalue=x, test=lambda x: int(x) == 0)
        grid = clean_grid_str(grid, pattern=r'Max_NestG=([0-9]*)', fillvalue=ngrid                     , test=lambda x: int(x) == 0)
        grid = clean_grid_str(grid, pattern=r'Time=([0-9]*\.[0-9]*E[|\-|\+][0-9]*)', fillvalue='0', test=lambda x: float(x) != 0)
        
        # --- save results
        if args.no_overwrite:
            fpath = '{}.fix'.format(str(fpath))
        elif args.output is not None:
            fileout = Path(root, args.output)
        else:
            shutil.copy(fpath, Path(root, 'bakup', file))
        
        write_res(grid, fileout)
    
    return 0


if __name__ == '__main__':
    
    status = main()
    sys.exit(status)
