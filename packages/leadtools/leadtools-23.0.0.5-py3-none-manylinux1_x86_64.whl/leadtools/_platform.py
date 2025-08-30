# *************************************************************
# Copyright (c) 1991-2025 Apryse Software Corp.
# All Rights Reserved.
# *************************************************************

import os


class PlatformHelper:
    """
    Provides helper functionality for the LEADTOOLS Python library

    This static class provides static methods for configuring the LEADTOOLS Python library
    """

    _initialized = False

    # Get the platform specific native lib path
    @staticmethod
    def get_default_lib_path():
        """
        Gets the default lib path for the LEADTOOLS native libraries

        Returns a fully qualified path to the default location of the LEADTOOLS native libraries based on the current platform
        """
        from ._info import LeadtoolsInfo
        bin_path = LeadtoolsInfo.get_bin()
        from Leadtools import Platform

        if not os.path.exists(bin_path):
            raise FileNotFoundError("LEADTOOLS bin path not found: {}".format(bin_path))

        lib_path = bin_path.replace("\\", "/")
        kernel_name = ""

        if Platform.IsWindows:
            if Platform.Is64Bit:
                kernel_name = "Ltkrnx.dll"
                lib_path = os.path.join(bin_path, "CDLL", "x64").replace("\\", "/")
            else:
                kernel_name = "Ltkrnu.dll"
                lib_path = os.path.join(bin_path, "CDLL", "Win32").replace("\\", "/")
        elif Platform.IsLinux:
            kernel_name = "libltkrn.so"
            if Platform.Is64Bit:
                lib_path = os.path.join(bin_path, "Linux", "x64").replace("\\", "/")
                if not os.path.exists(lib_path):
                    lib_path = os.path.join(bin_path, "Lib", "x64").replace("\\", "/")
            else:
                lib_path = os.path.join(bin_path, "Linux", "x86").replace("\\", "/")
                if not os.path.exists(lib_path):
                    lib_path = os.path.join(bin_path, "Lib", "x86").replace("\\", "/")
        elif Platform.IsMacOS:
            kernel_name = "Leadtools.framework"
            lib_path = os.path.join(bin_path, "Xcode", "Frameworks/macOS").replace(
                "\\", "/"
            )
        else:
            raise RuntimeError("Unsupported operating system detected!")

        kernel_path = os.path.join(lib_path, kernel_name).replace("\\", "/")
        if not os.path.exists(kernel_path):
            raise FileNotFoundError(
                "LEADTOOLS native kernel library not found: {}".format(kernel_path)
            )

        return lib_path

    @staticmethod
    def init_leadtools():
        """
        Initializes the LEADTOOLS Python library

        Configures the LEADTOOLS Python library to use the default location for the native libraries for the current platform
        """
        from ._info import LeadtoolsInfo
        if not PlatformHelper._initialized:
            from Leadtools import Platform
            Platform.LibraryPath = PlatformHelper.get_default_lib_path()
            PlatformHelper._initialized = True
