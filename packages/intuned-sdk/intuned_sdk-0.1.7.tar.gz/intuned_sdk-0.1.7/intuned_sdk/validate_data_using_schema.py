from typing import Any
from typing import Dict
from typing import List

from jsonschema import validate
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError


class ValidationError(Exception):
    """Custom validation error with readable message."""

    def __init__(self, message: str, data: Any) -> None:
        self.data = data
        super().__init__(message)


def clean_data(
    data: Dict[str, Any] | List[Dict[str, Any]],
) -> Dict[str, Any] | List[Dict[str, Any]]:
    if isinstance(data, list):
        return [clean_data(item) for item in data]  # type: ignore
    elif isinstance(data, dict):  # type: ignore
        return {k: clean_data(v) for k, v in data.items() if v != "" and v is not None}
    return data


async def validate_data_using_schema(
    data: Dict[str, Any] | List[Dict[str, Any]], schema: Dict[str, Any]
):
    cleaned_data = clean_data(data)
    try:
        validate(instance=cleaned_data, schema=schema)
    except JsonSchemaValidationError as e:
        raise ValidationError(f"Data validation failed: {e.message}", data)
