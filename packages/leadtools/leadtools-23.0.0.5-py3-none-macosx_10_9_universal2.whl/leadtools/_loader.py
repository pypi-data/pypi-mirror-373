# *************************************************************
# Copyright (c) 1991-2025 Apryse Software Corp.
# All Rights Reserved.
# *************************************************************


class LibraryLoader:
    """
    Provides method for loading LEADTOOLS .NET Core libraries.

    This static class provides static methods for loading LEADTOOLS .NET Core libraries into the Python application scope
    """

    @staticmethod
    def add_reference(lib_name):
        """
        Adds the specified library into the application scope

        This is the equivalent in C# of adding a file reference to the specified .dll or using the System.Reflection.Assembly.Load() method

        Parameters:
        lib_name (str): The name of the LEADTOOLS library (without '.dll')

        Returns:
        None
        """
        import clr
        clr.AddReference(lib_name)