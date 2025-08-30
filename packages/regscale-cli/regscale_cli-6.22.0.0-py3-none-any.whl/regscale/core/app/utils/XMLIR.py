# Author: Luke Bechtel (Regscale)
import typing
from functools import wraps
from typing import List

from lxml import etree
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypedDict

from regscale.integrations.public.fedramp.reporting import log_error, log_event


class LogEventArgs(TypedDict):
    """
    Args for the log_event function.
    """

    record_type: str
    event_msg: str
    model_layer: str
    level: str


class LogErrorArgs(TypedDict):
    """
    Args for the log_error function.
    """

    record_type: str
    missing_element: str
    model_layer: str
    level: str
    event_msg: str


class XMLIRTraversal(BaseModel):
    """
    A traversal through an XML tree to produce an XMLIR object.
    :param xpathToThis: The XPath to the current element
    :param el: The current element
    :param root: The root element
    :param add_error: A function to add an error
    :param add_log: A function to add a log
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    namespaces: dict
    xpathToThis: str
    el: etree._Element
    root: etree._Element

    events: List[LogEventArgs] = []
    errors: List[LogErrorArgs] = []

    def el_xpath(self, xpath: str):
        """
        Helper function to get an element by xpath from the current element, using the correct namespaces.
        """
        return self.el.xpath(xpath, namespaces=self.namespaces)

    def root_xpath(self, xpath: str) -> etree._Element:
        """
        Helper function to get an element by xpath from the root element, using the correct namespaces.

        :param str xpath: The xpath to the element
        :return: The element at the provided xpath
        :rtype: etree._Element
        """
        return self.root.xpath(xpath, namespaces=self.namespaces)

    def add_event(self, args: LogEventArgs):
        """
        Add an event to this traversal.

        :param LogEventArgs args: The event arguments
        """
        self.events.append(
            log_event(
                record_type=args["record_type"],
                event_msg=args["event_msg"],
                model_layer=args["model_layer"],
                level=args["level"],
            )
        )

    def add_error(self, args: LogErrorArgs):
        """
        Add an error to this traversal.

        :param LogErrorArgs args: The event arguments
        """
        self.errors.append(
            log_error(
                record_type=args["record_type"],
                missing_element=args["missing_element"],
                model_layer=args["model_layer"],
                level=args["level"],
                event_msg=args["event_msg"],
            )
        )


class XMLIR:
    """
    A class that makes creating intermediate representations of XML objects easier.
    Calling parse() on an XMLIR-inheriting object will run through all its decorated functions
    and return a dictionary of the results.
    """

    __decorated_functions: {} = {}

    @classmethod
    def from_el(cls, xpath):
        """
        A decorator used to decorate functions that will be run on an XML element.
        The return value of the decorated function will be added to the object returned by 'XMLIR.parse()'
        """

        def wrapper(func):
            qualname = func.__qualname__
            clsname = qualname.rsplit(".", 1)[0] if "." in qualname else None

            @wraps(func)
            def inner(self, *args, **kwargs):
                return func(self, *args, **kwargs)

            if clsname not in cls.__decorated_functions:
                cls.__decorated_functions[clsname] = {}

            if func.__name__ not in cls.__decorated_functions[clsname]:
                cls.__decorated_functions[clsname][func.__name__] = {}

            cls.__decorated_functions[clsname][func.__name__]["func"] = func
            cls.__decorated_functions[clsname][func.__name__]["xpath"] = xpath
            return inner

        return wrapper

    def decorated_functions_for_class(self):
        """
        Returns the decorated functions for this class.
        """
        return self.__decorated_functions[self.__class__.__name__]

    def parse(self, traversal: XMLIRTraversal):
        """
        Will traverse an XML element,
        and run any functions decorated with @XMLIR.from_el
        """
        ret = {}

        # Run through all decorated functions and run them.
        for func_name, f_desc in self.decorated_functions_for_class().items():
            xpath = f_desc["xpath"]
            func = f_desc["func"]

            # Get the relevant element from the xpath
            xml_els = traversal.el.xpath(xpath, namespaces=traversal.namespaces)

            # Pass the xml_els to the function
            # And get the result
            processed_xml_els = func(self, xml_els, traversal)

            # Add the result to the return object
            ret[func_name] = processed_xml_els

        return ret


class XMLIR2:
    def __init__(self, traversal: XMLIRTraversal) -> None:
        # Validate that all custom attributes have a getter
        self.check_get_methods()

        # Get all custom attributes.
        attributes_to_parse = self.get_custom_attrs()

        # Run through all getters and add the result to the object
        for attr_name in attributes_to_parse:
            getter = self.getter_for_attr(attr_name)
            setattr(self, attr_name, getter(traversal))

    def __repr__(self) -> str:
        """
        Print out all normal attributes of the object.
        """
        attrs = self.custom_attr_dict()

        return f"{self.__class__.__name__} ({str(attrs)})"

    def custom_attr_dict(self) -> dict:
        """
        Return a list of all custom attributes and their values.
        """
        custom_attrs = self.get_custom_attrs()
        return {attr_name: getattr(self, attr_name) for attr_name in custom_attrs}

    def items(self):
        return self.custom_attr_dict().items()

    def __iter__(self):
        return iter(self.items())

    def getter_for_attr(self, attr_name: str):
        return getattr(self, f"get_{attr_name}")

    def check_get_methods(self) -> None:
        attributes = self.get_custom_attrs()

        for attr in attributes:
            getter_name = f"get_{attr}"
            if not hasattr(self, getter_name):
                raise AttributeError(
                    f"No 'get_{attr}' method found. "
                    "All non-callable, non-'__'-prefixed custom attributes must have a getter."
                )

            # Get the getter method
            getter_method = getattr(self.__class__, getter_name)

            # Check if the getter has a return type hint
            getter_hints = typing.get_type_hints(getter_method)
            if "return" not in getter_hints:
                raise TypeError(f"Getter '{getter_name}' does not have a return type hint.")

            # Check if the attribute has a type hint
            attr_hints = typing.get_type_hints(self.__class__)
            if attr not in attr_hints:
                raise TypeError(f"Attribute '{attr}' does not have a type hint.")

            # Compare the type hint of the getter and the attribute
            if getter_hints["return"] != attr_hints[attr]:
                raise TypeError(
                    f"Type hint of the attribute '{attr}' does not match the return type hint of its getter method."
                )

        getters = self.get_custom_attr_getters()
        for getter in getters:
            attr_name = getter.replace("get_", "")
            if not hasattr(self, attr_name):
                raise AttributeError(f"Getter '{getter}' found, but no attribute '{attr_name}' found.")

    def get_custom_attr_getters(self) -> List[str]:
        attributes: List[str] = [
            attr_name
            for attr_name, attr_value in self.__class__.__dict__.items()
            if callable(attr_value) and attr_name.startswith("get_")
        ]
        return attributes

    def get_custom_attrs(self) -> List[str]:
        attributes: List[str] = [
            attr_name
            for attr_name, attr_value in self.__class__.__dict__.items()
            if not callable(attr_value) and not attr_name.startswith("__")
        ]
        return attributes
