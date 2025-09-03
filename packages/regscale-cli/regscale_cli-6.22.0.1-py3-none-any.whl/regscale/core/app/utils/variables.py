#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions and classes for handling application variables"""

import logging
import os
import re
import sys
from typing import Any, Callable, Dict, Optional, Tuple, Type

logger = logging.getLogger(__name__)


class RsVariableType:
    """
    Configuration variable type

    :param Type var_type: The data type of the configuration variable
    :param str example: An example value for the configuration variable
    :param Optional[bool] required: A flag indicating if the configuration variable is required, defaults to True
    :param Optional[bool] sensitive: A flag indicating if the configuration variable is sensitive, defaults to False
    :param Optional[Any] default: A default value for the configuration variable, defaults to None
    """

    def __init__(
        self,
        var_type: Type,
        example: str,
        required: Optional[bool] = True,
        sensitive: Optional[bool] = False,
        default: Optional[Any] = None,
    ) -> None:
        self.type = var_type
        self.example = example
        self.required = required
        self.sensitive = sensitive
        self.default = default


class RsVariableClassProperty:
    """
    Class property for retrieving configuration variables

    :param Callable getter: The getter function for the property
    """

    def __init__(self, getter: Callable):
        self.getter = getter
        self.name = None  # Will store the attribute name

    def __set_name__(self, owner: Any, name: str) -> None:
        """
        Sets the name of the property when it's assigned to a class

        :param Any owner: The class that owns this property
        :param str name: The name of the property
        """
        self.name = name

    def __get__(self, obj: Any, cls: Optional[type] = None) -> Any:
        """
        Retrieves the value using the getter when the property is accessed

        :param Any obj: The object instance
        :param Optional[type] cls: The class instance, defaults to None
        :return: The value of the property
        :rtype: Any
        """
        if obj is None:
            # Class-level access
            return self.getter(cls)

        # Instance-level access
        if not hasattr(obj, f"_{self.name}"):
            # Initialize the instance-specific value
            value = self.getter(cls)
            setattr(obj, f"_{self.name}", value)
        return getattr(obj, f"_{self.name}")

    def __set__(self, obj: Any, value: Any) -> None:
        """
        Sets the value for an instance

        :param Any obj: The object instance
        :param Any value: The value to set
        """
        setattr(obj, f"_{self.name}", value)


class RsVariablesMeta(type):
    """
    Metaclass for creating RsVariables classes with properties for each configuration variable.

    Example::

        .. code-block:: python

            >>>class GcpVariables(metaclass=RsVariablesMeta):
            >>>    # Define class-level attributes with type annotations and examples
            >>>    gcpProjectId: RsVariableType(str, "000000000000")
            >>>    gcpCredentials: RsVariableType(str, "path/to/credentials.json", sensitive=True)
    """

    def __new__(cls, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any]):
        """
        Creates new RsVariables class with properties for each configuration variable

        :param str name: The name of the class
        :param Tuple[type, ...] bases: The base classes of the class
        :param Dict[str, Any] attrs: The attributes of the class
        :return: The new RsVariables class
        """
        for attr, config_type in attrs.get("__annotations__", {}).items():
            if isinstance(config_type, RsVariableType):
                # Create a property for each configuration attribute
                getter = cls.create_getter(attr, config_type)
                attrs[attr] = RsVariableClassProperty(getter)

        # Add an __init__ method to initialize instance attributes
        def __init__(self):
            # Initialize all properties to trigger the getters
            for attr in self.__class__.__annotations__:
                if isinstance(self.__class__.__annotations__[attr], RsVariableType):
                    getattr(self, attr)

        attrs["__init__"] = __init__
        return super(RsVariablesMeta, cls).__new__(cls, name, bases, attrs)

    @staticmethod
    def create_getter(attr: str, config_type: RsVariableType) -> Callable:
        """
        Creates a getter function for each property

        :param str attr: The name of the attribute
        :param RsVariableType config_type: The type of the attribute
        :return: The getter function for the attribute
        :rtype: Callable
        """

        def getter(cls: type) -> Any:
            return RsVariablesMeta.fetch_config_value(attr, config_type)

        return getter

    @classmethod
    def fetch_config_value(cls, attr_name: str, config_type: RsVariableType) -> Any:
        """
        Fetches, processes, and returns the configuration value for a given attribute

        :param str attr_name: The name of the attribute
        :param RsVariableType config_type: The type of the attribute
        :raises ValueError: If a required configuration is missing and the script is not running interactively
        :return: The processed configuration value
        :rtype: Any
        """
        from regscale.core.app.application import Application

        app = Application()
        # Check Environment variable first (case-insensitive), then init.yaml
        config_value = next((os.environ[key] for key in os.environ if key.lower() == attr_name.lower()), None)
        if config_value is None:
            config_value = next((value for key, value in app.config.items() if key.lower() == attr_name.lower()), "")
        processed_value = cls.replace_text_inside_brackets(config_value)
        if config_type.sensitive:
            logger.debug(f"Configuration for '{attr_name}' set to: ******")
        else:
            logger.debug(f"Configuration for '{attr_name}' set to: {processed_value}")

        if processed_value == "":
            if config_type.required and config_type.default is None:
                if sys.stdin.isatty():
                    prompt_message = (
                        f"\033[91mREQUIRED: {attr_name} not set in init.yaml or environment variable.\033[0m \n"
                        f"Enter value for {attr_name} (e.g., {config_type.example}):"
                    )
                    processed_value = input(prompt_message)
                else:
                    error_message = (
                        f"Required configuration '{attr_name}' is missing and script is not running interactively."
                    )
                    logger.error(error_message)
                    raise ValueError(error_message)

                if config_type.sensitive:
                    logger.info(f"Configuration for '{attr_name}' saved to init.yaml: ******")
                else:
                    logger.info(f"Configuration for '{attr_name}' saved to init.yaml: {processed_value}")
                # Save the config value
                app.config[attr_name] = processed_value
                app.save_config(app.config)
            elif config_type.default is not None:
                processed_value = config_type.default
                logger.debug(f"Using default value for '{attr_name}': {processed_value}")
        try:
            if config_type.type == dict:
                if isinstance(processed_value, str):
                    import ast

                    typed_value = ast.literal_eval(processed_value) if processed_value else {}
                else:
                    typed_value = processed_value if processed_value else {}
            elif config_type.type == bool:
                if isinstance(processed_value, str):
                    typed_value = processed_value.lower() in ["true", "1", "yes"]
                elif isinstance(processed_value, bool):
                    typed_value = processed_value
            else:
                typed_value = config_type.type(processed_value)
        except (ValueError, SyntaxError):
            logger.error(f"Failed to cast '{attr_name}' to {config_type.type.__name__}. Using original value.")
            typed_value = processed_value
        return typed_value

    @staticmethod
    def replace_text_inside_brackets(text: str, replacement: str = "") -> str:
        """
        Removes text inside brackets from a given string

        :param str text: The string to remove text from
        :param str replacement: The replacement text
        :return: The string with text inside brackets removed
        :rtype: str
        """
        # if string
        if not isinstance(text, str):
            return text
        pattern = "<[^>]*>"
        return re.sub(pattern, replacement, text)
