<!-- gridmarthe changelog -->

v0.1.3
------

Released on 2025-09-02

* add geometry functions (get_mask_array, compute_geometry)
* add reprojection functions (still experimental)
* add `martshp` script to easily convert a marthe grid file into a shp/gpkg file in command line
* code refactoring (lecsem module and global organization)
* add automatic tests
* minor fixes in plot method
* change: rename function to write raster: `to_raster()` instead of `write_raster_from_da()` 
* change: zone index is reset when the `drop_nan` option is used in `load_grid_marthe()`. A new
  variable 'zone_all' store the old index for the `reset_geometry()` method


v0.1.2
------

Released on 2025-01-09

* Change build to meson
* fix scripts 'ncmart' and 'cleanmgrid' paths
* update write method


v0.1.1
------

Released on 2024-11-03.

* first release as a stand alone package


v0.0.1
------

Unreleased - 2021-2024

* Use fortran sources from Marthe with f2py to read grids, single layer, homogeneous grids (1st version from JP Vergnes)
* Extend to multilayer, nested grid (A Manlay)
* Python wrappers for easy read operations (AM)
* Add write method in Fortran sources, scan var and wrappers (AM)
* Add command line scripts, and some derived treatments (surface layer, rescale, etc.)
