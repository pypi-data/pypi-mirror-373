[![PyPI - Version](https://img.shields.io/pypi/v/gridmarthe)](https://pypi.org/project/gridmarthe/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/gridmarthe.svg)](https://anaconda.org/conda-forge/gridmarthe)
[![GitLab License](https://img.shields.io/gitlab/license/brgm%2Fhydrogeological-modelling%2Fmarthe-tools%2Fgridmarthe?color=blue)](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/blob/dev/LICENSE?ref_type=heads)

# Gridmarthe

`gridmarthe` is a Python project for (fast) Marthe grid operations.

MARTHE is a hydrogeological modelling code developped at BRGM, French Geological
Survey [(Thiery, 2020)](#references), and is available at
https://www.brgm.fr/en/software/marthe-modelling-software-groundwater-flows


## gridmarthe in a nutshell

`gridmarthe` allow users to read/write efficiently Marthe Grids (v9, v8, constant_data, etc.)
with python, for any MARTHE variable.

With the `gridmarthe` API, data are stored in a `xarray` dataset, and can be manage with
`xarray` functions (or `numpy`). Specific treatments/functions are also provided by `gridmarthe`.

The package also install different command line tools: `ncmart` to convert Marthe Grid to netCDF format,
`martshp` to convert in shapefile/geopackage, `cleanmgrid` to fix marthe grid format.

Full documentation and tutorials can be founded at https://gridmarthe.readthedocs.io


## Installation

### From pip


On pip, `gridmarthe` is available for GNU/Linux, macOS and Windows for python >=3.10.
Users can install it with:

```bash
pip install gridmarthe
```

For GNU/Linux and MacOS, the package needs gfotran/gcc to run.

Linux, example with debian/ubuntu:

```bash
sudo apt install gcc gfortran
```


MacOS:

```bash
brew install gcc gfortran
```

### From conda-forge

`gridmarthe` is also available in the `conda-forge` channel. Conda users can install it with:

```bash
conda install gridmarthe
# or, with mamba
mamba install gridmarthe
```


### From sources

`gridmarthe` use some Fortran modules which need
to be compiled before local installation.

#### Compilation and installation

Get the sources :

```bash
git clone https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe
cd gridmarthe
```

##### With pip (Unix-like OS)

On a Unix-like machine, with gfortran, ninja-build, python3, the project `Makefile` will compile Fortran sources and install
**in development mode** the package.

```bash
make
```

or, without the development mode :

```bash
pip install .
```

On a windows machine, it is possible to compile with gfortran
(mingw project https://mingw-w64.org/ or https://winlibs.com/#download-release ; or `choco install mingw`).
Neverless, the simpliest way is to use a conda environment (miniforge with mambalib is recommended) to install gcc/gfortran,
and install the project.

##### With conda (recommended on Windows)

It is also possible to install gridmarthe in a conda environment. An environment file is provided (example with mamba):

```bash
mamba env create -n gm -f environment.yml
mamba activate gm
pip install --no-deps .
```

Here, the development mode is *not* available (yet, with the meson build).
One can add the `-e` flag in pip command, or use `conda-build`:

```bash
mamba env create -n gm -f environment.yml
mamba activate gm
mamba install conda-build
make lib
conda develop src/
```


## Usage

Simple examples can be found in the 
[documentation](https://gridmarthe.readthedocs.io/en/stable/user_guide/index.html).


## License

This program is free software and released under the terms of the
[GNU General Public License (version 3 or later)](LICENSE).


## Authors and acknowledgment

A. Manlay and J.P. Vergnes, (c) BRGM


## References

Thiery, D. (2020). Guidelines for MARTHE v7.8 computer code for
hydro-systems modelling (English version) (Report BRGM/RP-69660-FR; p. 246 p.)
 <http://ficheinfoterre.brgm.fr/document/RP-69660-FR>
