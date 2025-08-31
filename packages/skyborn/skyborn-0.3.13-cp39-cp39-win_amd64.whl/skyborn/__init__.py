# skyborn/__init__.py


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'skyborn.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-skyborn-0.3.13')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-skyborn-0.3.13')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

# Import calculation functions
# Import submodules
from . import ROF, calc, conversion, gridfill, interp, plot, spharm, windspharm

# Expose calc submodules at package top-level for convenience
from .calc import (  # Mann-Kendall functions; New emergent constraint function names; Legacy names for backward compatibility
    calc_GAUSSIAN_PDF,
    calc_PDF_EC,
    calc_PDF_EC_PRIOR,
    calculate_potential_temperature,
    convert_longitude_range,
    emergent_constraint_posterior,
    emergent_constraint_prior,
    find_std_from_PDF,
    gaussian_pdf,
    geostrophic,
    kendall_correlation,
    linear_regression,
    mann_kendall_multidim,
    mann_kendall_test,
    mann_kendall_xarray,
    mk_multidim,
    mk_test,
    pearson_correlation,
    spearman_correlation,
    trend_analysis,
    troposphere,
)
from .causality import granger_causality, liang_causality

# Import conversion functions for easy access
from .conversion import (
    GribToNetCDFError,
    batch_convert_grib_to_nc,
    convert_grib_to_nc,
    convert_grib_to_nc_simple,
    grib2nc,
    grib_to_netcdf,
)
from .gradients import (
    calculate_gradient,
    calculate_meridional_gradient,
    calculate_vertical_gradient,
    calculate_zonal_gradient,
)

# Import key gridfill functions for convenient access
from .gridfill import fill as gridfill_fill

# Expose gridfill functions at top level with clear names
fill = gridfill_fill


__version__ = "0.3.13"
