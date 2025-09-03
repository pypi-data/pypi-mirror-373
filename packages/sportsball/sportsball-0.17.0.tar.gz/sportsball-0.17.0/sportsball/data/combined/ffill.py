"""A function for forward filling."""

from typing import Any

from pydantic import BaseModel

from ..field_type import FFILL_KEY


def ffill(ffill_dict: dict[str, Any], identifier: str, model: BaseModel) -> None:
    """Forward fill a dictionary."""
    instance_ffil = ffill_dict.get(identifier, {})
    for field_name, field in model.model_fields.items():
        extra = field.json_schema_extra or {}
        if extra.get(FFILL_KEY, False):  # type: ignore
            current_value = getattr(model, field_name)
            if current_value is None or (
                isinstance(current_value, list) and not current_value
            ):
                setattr(model, field_name, instance_ffil.get(field_name))
            else:
                instance_ffil[field_name] = current_value
    ffill_dict[identifier] = instance_ffil
