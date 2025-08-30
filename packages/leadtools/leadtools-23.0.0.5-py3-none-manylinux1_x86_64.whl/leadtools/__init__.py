# *************************************************************
# Copyright (c) 1991-2025 Apryse Software Corp.
# All Rights Reserved.
# *************************************************************

# This module is for allowing LEADTOOLS .NET Core to be used in Python 3.7+
# This module requires Python.NET
# This module requires the .NET Core runtime

import os
import sys

_dotnet_config = "DotNetConfig.json"
_leadtools_config = "LeadtoolsConfig.json"

# Import PythonNet
from pythonnet import set_runtime


def _init_dotnet():
    """
    Initializes the .NET Core runtime

    This function initializes the .NET Core runtime using the runtime configuration file found in the libraries config folder.

    Returns:
    None
    """

    # Load .NET Core Runtime
    from clr_loader import get_coreclr

    root_folder = os.path.dirname(__file__)
    config_file = os.path.join(root_folder, "config", _dotnet_config)
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Missing .NET Core runtime config file {config_file}!")
    set_runtime(get_coreclr(runtime_config=config_file))
    return config_file


def _load_leadtools_kernel_modules():
    """
    Loads the LEADTOOLS Kernel libraries.

    This function loads the LEADTOOLS Kernel libraries into the application scope.
    """
    import clr

    #from ._info import LeadtoolsInfo

    sys.path.append(
        os.path.join(LeadtoolsInfo.get_bin(), "net")
    )

    _kernel_modules = {"Leadtools", "Leadtools.Core"}
    for kernel_module in _kernel_modules:
        clr.AddReference(kernel_module)


def _init():
    """
    Initializes the LEADTOOLS Python library

    This function initializes the LEADTOOLS Python library by configuring and starting the .NET Core runtime and then loading the LEADTOOLS Kernel libraries into the application scope.
    """
    # Add the LEADTOOLS net bin folder to the python search path
    _init_dotnet()
    _load_leadtools_kernel_modules()
    #from ._platform import PlatformHelper
    PlatformHelper.init_leadtools()


# useful variables
from .__pkginfo__ import __version__
from .__pkginfo__ import __product__
from .__pkginfo__ import __copyright__
from .__pkginfo__ import __license__


from ._info import LeadtoolsInfo
from ._loader import LibraryLoader
from ._platform import PlatformHelper

__all__ = [
    "LeadtoolsInfo",
    "LibraryLoader",
    "PlatformHelper",
]

# run the LEADTOOLS initialization
_init()
