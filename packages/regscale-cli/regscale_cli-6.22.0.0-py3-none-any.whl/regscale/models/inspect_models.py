#!/usr/bin/env python3

"""Click BaseModels."""
from collections import OrderedDict
from inspect import Parameter, Signature, signature
from types import MappingProxyType
from typing import Any, Dict, List, Optional, Union, Callable

import click
import click.core
from pydantic import BaseModel, validator, ConfigDict, field_validator


# A Pydantic model to represent a parameter in a function signature
class ParameterModel(BaseModel):
    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)
    name: str
    kind: str
    default: Optional[Any] = None
    annotation: Union[str, None]

    # Validators to convert Parameter.kind and Parameter.annotation to string
    @field_validator("kind", mode="before")
    def _get_kind_str(cls, v):
        return str(v)

    @field_validator("annotation", mode="before")
    def _get_annotation_str(cls, v):
        if v is Parameter.empty:
            return None
        return str(v)


class SignatureModel(BaseModel):
    """Signature Model"""

    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    name: Optional[str] = None
    signature: Optional[Union[Signature, dict, str]] = None
    # parameters: Optional[OrderedDict] = None
    parameters: Dict[str, ParameterModel]

    @field_validator("signature", mode="before")
    def _check_signature(cls, var):
        """Validate a click.Command"""
        if not isinstance(var, (Signature, str, dict)):
            print(f"signature must be a (Signature, str, dict) not {type(var)}")
        return var

    @classmethod
    def from_callable(cls, command: str, fn: Callable):
        sig = signature(fn)
        params = {
            name: ParameterModel(
                name=command,
                kind=param.kind,
                default=param.default if param.default is not Parameter.empty else None,
                annotation=param.annotation,
            )
            for name, param in sig.parameters.items()
        }
        return cls(name=command, parameters=params, signature=sig)

    def to_dict(self):
        return {name: param.dict() for name, param in self.parameters.items()}

    def to_string(self):
        return ", ".join(
            [f"{param.name}: {param.annotation}={repr(param.default)}" for param in self.parameters.values()]
        )


if __name__ == "__main__":
    from regscale.models.hierarchy import REGSCALE_CLI

    call = REGSCALE_CLI["login"].callback
    b = SignatureModel.from_callable(command="login", fn=call)
    b
