# SPDX-FileCopyrightText: 2025 PairInteraction Developers
# SPDX-License-Identifier: LGPL-3.0-or-later


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pairinteraction.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-pairinteraction-2.2.2')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-pairinteraction-2.2.2')) as file:
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

import multiprocessing
import sys

from pairinteraction_gui.app import Application
from pairinteraction_gui.main_window import MainWindow

__all__ = ["main"]


def main() -> int:
    """Run the PairInteraction GUI application.

    Returns:
        int: Application exit code

    """
    # Multithreading together with "fork" is not supported
    # (up to python 3.14 "fork" was the default on linux
    # see also https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
    # and https://docs.python.org/3.14/whatsnew/3.14.html#whatsnew314-multiprocessing-start-method)
    # We set the start method to "spawn" for all platforms (anyway default on mac and windows)
    # TODO instead of multiprocessing it would probably be better to release the GIL during some C++ calls
    # see here: https://nanobind.readthedocs.io/en/latest/api_core.html#_CPPv4N8nanobind18gil_scoped_releaseE
    multiprocessing.set_start_method("spawn")

    app = Application(sys.argv)
    app.setApplicationName("PairInteraction")

    app.allow_ctrl_c()

    window = MainWindow()
    window.show()

    return app.exec()
