"""""" # start delvewheel patch
def _delvewheel_patch_1_10_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pyvalhalla_weekly.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-pyvalhalla_weekly-3.5.1.post1.dev207')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-pyvalhalla_weekly-3.5.1.post1.dev207')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from pathlib import Path

try:
    from ._valhalla import VALHALLA_PRINT_VERSION, VALHALLA_PYTHON_PACKAGE
except ModuleNotFoundError:
    from _valhalla import VALHALLA_PRINT_VERSION, VALHALLA_PYTHON_PACKAGE
from .actor import Actor
from .config import get_config, get_help

# if run from CMake, Docker or test
try:
    from .__version__ import __version__

    # extend with version modifier (so far the git hash)
    if (idx := VALHALLA_PRINT_VERSION.find("-")) != -1:
        __version__ = __version__ + VALHALLA_PRINT_VERSION[idx:]
except ModuleNotFoundError:
    __version__ = "undefined"

PYVALHALLA_DIR = Path(__file__).parent.resolve()

__all__ = ["Actor", "get_config", "get_help", "__version__"]
