# *************************************************************
# Copyright (c) 1991-2025 Apryse Software Corp.
# All Rights Reserved.
# *************************************************************

import os
import json

from .__pkginfo__ import __version__
from .__pkginfo__ import __product__
from .__pkginfo__ import __copyright__
from .__pkginfo__ import __license__
from .__pkginfo__ import __leadtools_config__


class LeadtoolsInfo:
    """
    Provides useful information about the LEADTOOLS Python library

    This static class provides static methods for getting useful information about the LEADTOOLS Python library
    """

    @staticmethod
    def print_product_info():
        """
        Prints the LEADTOOLS Python library product name and version
        """
        print(f"{__product__} version {__version__}")

    @staticmethod
    def print_version():
        """
        Prints the LEADTOOLS Python library product version
        """
        print(f"{__version__}")

    @staticmethod
    def print_license():
        """
        Prints the LEADTOOLS Python library product copyright and license
        """
        print(f"{__copyright__}\n{__license__}")

    @staticmethod
    def get_bin():
        """
        Gets the LEADTOOLS Python library bin folder

        Returns the fully qualified path of the LEADTOOLS Python library bin folder
        The bin folder is where the LEADTOOLS .NET Core (managed) and native libraries reside
        """
        # return os.path.join(os.path.join(os.path.dirname(__file__), "bin"))

        # Read the config file and get the binPath, which should be relative to the root_folder
        root_folder = os.path.dirname(__file__)
        f = open(os.path.join(root_folder, "config", __leadtools_config__))
        data = json.load(f)
        bin_path = os.path.abspath(os.path.join(root_folder, data["binPath"]))
        f.close()
        return os.path.abspath(os.path.join(root_folder, bin_path))

    @staticmethod
    def get_ocr_runtime():
        """
        Gets the LEADTOOLS Python library OCR Runtime folder

        Returns the fully qualified path of the LEADTOOLS Python library OCR Runtime folder
        For more information see: https://www.leadtools.com/help/sdk/dh/to/leadtools-ocr-module-lead-engine-runtime-files.html
        """
        ocr_path = os.path.join(os.path.join(LeadtoolsInfo.get_bin(), "Common", "OcrLEADRuntime"))
        if not os.path.exists(ocr_path):
            ocr_path = os.path.join(os.path.join(LeadtoolsInfo.get_bin(), "../../leadtools_common_runtime/bin/Common", "OcrLEADRuntime"))
        if not os.path.exists(ocr_path):
            raise FileNotFoundError("LEADTOOLS OCR Runtime path not found!")
        return ocr_path

    @staticmethod
    def get_shadow_fonts():
        """
        Gets the LEADTOOLS Python library OCR Runtime folder

        Returns the fully qualified path of the LEADTOOLS Python library Shadow Fonts folder
        For more information see: https://www.leadtools.com/help/sdk/dh/to/leadtools-drawing-engine-and-multi-platform-consideration.html#ShadowFonts
        """
        shadow_fonts_path = os.path.join(os.path.join(LeadtoolsInfo.get_bin(), "Common", "ShadowFonts"))
        if not os.path.exists(shadow_fonts_path):
            shadow_fonts_path = os.path.join(os.path.join(LeadtoolsInfo.get_bin(), "../../leadtools_common_runtime/bin/Common", "ShadowFonts"))
        if not os.path.exists(shadow_fonts_path):
            raise FileNotFoundError("LEADTOOLS Shadow Fonts path not found!")
        return shadow_fonts_path


    @staticmethod
    def get_batch():
        """
        Gets the LEADTOOLS Python library batch folder

        Returns the fully qualified path of the LEADTOOLS Python library batch folder
        """
        return os.path.join(os.path.join(LeadtoolsInfo.get_bin(), "Common", "Batch"))
