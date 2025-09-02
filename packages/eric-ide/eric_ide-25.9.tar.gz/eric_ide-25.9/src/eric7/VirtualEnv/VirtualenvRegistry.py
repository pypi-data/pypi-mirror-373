# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the virtual environment types registry and associated data
structures.
"""

import contextlib
import types

from dataclasses import dataclass


@dataclass
class VirtualenvType:
    """
    Class implementing a container for the metadata of a virtual environment type.
    """

    name: str  # name of the type (used as a key in the registry)
    visual_name: str  # type name as shown to the user
    createFunc: types.FunctionType = None
    # function to create a virtual environment
    # This function must have the signature createFunc(baseDir: str) where 'basedir'
    # is the root path of the created environments (may be an empty string)
    deleteFunc: types.FunctionType = None
    # function to delete a virtual environment
    # This function must have the signature deleteFunc(venvMetaData: VirtualenvMetaData)
    # where 'venvMetaData' contains the data of the virtual environment. It must return
    # a flag indicating a successful deletion.
    upgradeFunc: types.FunctionType = None
    # function to upgrade a virtual environment
    # This function must have the signature
    # upgradeFunc(venvMetaData: VirtualenvMetaData) where 'venvMetaData' contains the
    # data of the virtual environment.
    defaultExecPathFunc: types.FunctionType = None
    # function returning the default PATH prefix string
    # This function must have the signature defaultExecPathFunc(venvDirectory: str)
    # where 'venvDirectory' is the directory of the environment. It must return a
    # string containing the default PATH prefix.


class VirtualenvTypeRegistry:
    """
    Class implementing the virtual environment type registry.
    """

    def __init__(self, venvManager):
        """
        Constructor

        @param venvManager reference to the virtual environment manager object
        @type VirtualenvManager
        """
        self.__manager = venvManager

        self.__registry = {}
        # dictionary containing the types entries with the type name as key

    def registerType(self, venvType):
        """
        Public method to register a new virtual environment type.

        @param venvType virtual environment data
        @type VirtualenvType
        @exception KeyError raised to indicate an already registered environment name
        """
        if venvType.name in self.__registry:
            raise KeyError(
                f"Virtual environment name '{venvType.name}' was already registered."
            )

        self.__registry[venvType.name] = venvType

    def unregisterType(self, name):
        """
        Public method to unregister the virtual environment type of the given name.

        @param name name of the virtual environment type
        @type str
        """
        with contextlib.suppress(KeyError):
            del self.__registry[name]

    def getEnvironmentType(self, name):
        """
        Public method to get a reference to the named virtual environment type.

        @param name name of the virtual environment type
        @type str
        @return reference to the environment type data
        @rtype VirtualenvType
        """
        try:
            return self.__registry[name]
        except KeyError:
            return None

    def getEnvironmentTypeNames(self):
        """
        Public method to get a list of names of registered virtual environment types.

        @return list of tuples of virtual environment type names and their visual name
        @rtype list of tuple of (str, str)
        """
        return [(v.name, v.visual_name) for v in self.__registry.values()]

    def getCreatableEnvironmentTypes(self):
        """
        Public method to get a list of all virtual environment types that posses a
        creation method/function.

        @return list of virtual environment types that posses a creation method/function
        @rtype functionType
        """
        return [e for e in self.__registry.values() if e.createFunc is not None]

    def getDeletableEnvironmentTypes(self):
        """
        Public method to get a list of all virtual environment types that posses a
        deletion method/function.

        @return list of virtual environment types that posses a deletion method/function
        @rtype functionType
        """
        return [e for e in self.__registry.values() if e.deleteFunc is not None]
