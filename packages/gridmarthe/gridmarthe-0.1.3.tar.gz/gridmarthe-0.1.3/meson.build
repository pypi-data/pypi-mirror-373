# ---------------------------------------------------------------- #
# ---------------------- Gridmarthe build ------------------------ #
# ---------------------------------------------------------------- #
# https://numpy.org/doc/stable/f2py/buildtools/meson.html          #
# ---------------------------------------------------------------- #

project('gridmarthe', ['fortran', 'c'],
  version : run_command('meson_get_version.py').stdout().strip(),
  license: 'GNU/GPL-V3',
  meson_version: '>=1.1.0',
  default_options : [
    'warning_level=1',
    'buildtype=release'
  ],
)

# add_languages('fortran')
lecsem_sources = files([
    'src/gridmarthe/lecsem/lecsem.f90',
    'src/gridmarthe/lecsem/edsemigl.f90',
    'src/gridmarthe/lecsem/scan_grid.f90'
])
lecsem_install_dir = 'gridmarthe/lecsem/'  # in python_install_dir


# ------ Get compiler and build options ------ #
fc = meson.get_compiler('fortran')
cc = meson.get_compiler('c')
deps = []
inc_dir = []

# Options de compilation Fortran
fargs = []  # compile args
largs = []  # link args

if fc.get_id() == 'gcc'
  
  fargs += ['-fdefault-real-8']
  fargs += ['-O2', '-ffree-line-length-none']
  
  if cc.version().version_compare('>=13.0')
    fargs += ['-fallow-argument-mismatch', '-std=legacy']
  endif
  
  if host_machine.system() == 'windows'
    fargs += ['-fPIC', '-Wno-error']
    
    if not get_option('condabuild')
        largs += ['-static', '-static-libgfortran', '-static-libgcc', '-static-libquadmath']
    endif
    
    quadmath_dep = fc.find_library('quadmath', required: false) # from `f2py --build-dir` meson.build generation
    quadmath = declare_dependency(link_args : ['-lquadmath'])
    deps += [quadmath_dep,quadmath]
  else
      # fargs += ['-fPIC', '-shared'] # not really necessary here
  endif

elif fc.get_id() in ['llvm-flang', 'flang', 'flang-new']
  # TODO add options for llvm-flang for conda-forge
  fargs += ['-fdefault-real-8', '-ffree-form']
  
elif cc.get_id() in ['intel-llvm', 'intel', 'intel-llvm-cl', 'intel-cl']
  fargs += ['-real-size 64', '-stand f95']

else
  # 'msvc' ?
  error('Build is recommended with GCC/gfortran')

endif


fortran_args = fc.get_supported_arguments(fargs)
link_args = fc.get_supported_link_arguments(largs)
add_project_arguments(fortran_args, language: 'fortran')
add_project_link_arguments(link_args, language: 'fortran')

# ----- Get Python linked ------ #
py = import('python').find_installation(pure: false)
py_dep = py.dependency()
python_install_dir = py.get_install_dir()

deps += [py_dep]

incdir_numpy = run_command(py,
  # ['-c', 'import os; import numpy; print(os.path.relpath(numpy.get_include()))'],
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()

inc_np = include_directories(incdir_numpy)
np_dep = declare_dependency(include_directories: inc_np)

incdir_f2py = incdir_numpy / '..' / '..' / 'f2py' / 'src'
inc_f2py = include_directories(incdir_f2py)
fortranobject_c = incdir_f2py / 'fortranobject.c'

inc_dir += [inc_np,inc_f2py]

# ---- Building interface for LECSEM ---- #
# subdir('src/gridmarthe/lecsem') # not functionnal yet, keep it here for now
lecsem_interface = custom_target('lecsemmodule.c',
  input : lecsem_sources,
  output : ['lecsemmodule.c', 'lecsem-f2pywrappers.f', 'lecsem-f2pywrappers2.f90'],
  command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', 'lecsem', '--lower']
)

py.extension_module('lecsem',
  [
    lecsem_sources,
    lecsem_interface,
    fortranobject_c
  ],
  include_directories: inc_dir,
  dependencies: deps,
  install: true,
  install_dir: python_install_dir / lecsem_install_dir,
)

# --------- Install pypackage ----------- #
install_subdir('src/gridmarthe', install_dir : python_install_dir)
