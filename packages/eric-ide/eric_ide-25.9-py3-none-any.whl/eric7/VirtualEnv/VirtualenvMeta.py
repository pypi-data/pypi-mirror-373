# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a data class containing the metadata of a virtual environment.
"""

from dataclasses import asdict, dataclass


@dataclass
class VirtualenvMetaData:
    """
    Class implementing a container for the metadata of a virtual environment.
    """

    name: str  # name of the virtual environment
    path: str = ""  # directory of the virtual environment (empty for a global one)
    interpreter: str = ""  # path of the Python interpreter
    is_global: bool = False  # flag indicating a global environment
    environment_type: str = "standard"  # virtual environment type
    environment_data: str = ""  # string with json serialized data used by the type
    exec_path: str = ""  # string to be prefixed to the PATH environment setting
    description: str = ""  # description of the environment
    eric_server: str = ""  # server name the environment belongs to
    available: bool = True  # flag indicating an available virtual environment
    meta_version: int = 3  # version number of the meta data structure

    def as_dict(self):
        """
        Public method to convert the metadata into a dictionary.

        @return dictionary containing the metadata
        @rtype dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """
        Class method to create a metadata object from the given dictionary.

        @param data dictionary containing the metadata
        @type dict
        @return created metadata object
        @rtype VirtualenvMetaData
        """
        if data.get("meta_version", 1) < 2:
            # convert from meta version 1
            if data.get("is_conda", False):
                data["environment_type"] = "conda"
            elif data.get("is_remote", False):
                data["environment_type"] = "remote"
            elif data.get("is_eric_server", False):
                data["environment_type"] = "eric_server"
            else:
                data["environment_type"] = "standard"

        return cls(
            name=data["name"],
            path=data.get("path", ""),
            interpreter=data.get("interpreter", ""),
            is_global=data.get("is_global", False),
            environment_type=data.get("environment_type", "standard"),
            environment_data=data.get("environment_data", ""),
            exec_path=data.get("exec_path", ""),
            description=data.get("description", ""),
            eric_server=data.get("eric_server", ""),
            available=data.get("available", True),
        )
