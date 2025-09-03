from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Param(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    name: Optional[str] = Field("", description="The name of the parameter")
    description: Optional[str] = Field("", description="The description of the parameter")
    expected_type: str = Field("STRING", description="The expected type of the parameter as a string", alias="type")
    optional: bool = Field(description="Whether the parameter is optional or not", alias="optional", default=False)
    data_type: Optional[Any] = Field(None, description="The allowed data type of the parameter")
    click_type: Optional[str] = Field(None, description="The click type of the parameter")
    default: Optional[Any] = Field(None, description="The default value of the parameter")

    @model_validator(mode="before")
    def set_data_types(cls, values: dict) -> dict:
        """
        Set the data type of the parameter based on the expected type

        :param values: The values of the model
        :return: Updated values
        :rtype: dict
        """
        if expected_type := values.get("type"):
            values["data_type"] = cls._map_types(expected_type)
            values["click_type"] = cls._map_click_types(expected_type)
        return values

    @classmethod
    def _map_click_types(cls, type_str: str) -> Optional[str]:
        """
        Map the string type to the equivalent click type

        :param str type_str: The data type as a string
        :return: The equivalent click type, if it exists
        :rtype: Optional[str]
        """
        click_types = {
            "string": "click.STRING",
            "number": "click.FLOAT",
            "integer": "click.INT",
            "bool": "click.BOOL",
            "choice": "click.Choice",
        }
        return click_types.get(type_str)

    @classmethod
    def _map_types(cls, type_str: str) -> Any:
        """
        Map the javascript string type to python type

        :param str type_str: The data type as a string
        :return: The actual data type in python
        :rtype: Any
        """
        data_types = {
            "string": "str",
            "object": "dict",
            "array": "list",
            "number": "float",
            "integer": "int",
            "boolean": "bool",
            "choice": "choice",
        }
        if type_str in data_types:
            return data_types[type_str]
        try:
            return eval(type_str)
        except NameError:
            raise ValueError(f"Invalid type: {type_str}")
