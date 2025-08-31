from http import HTTPStatus
from typing import Any, Type

from pydantic import BaseModel

from .error import ErrorModel

ResponseDoc = dict[int | str, dict[str, Any]]

def _create_http_status_code(status_code: int) -> HTTPStatus:
    return HTTPStatus(status_code)


def make_standard_response(
    status_code: int,
    *,
    model: Type[BaseModel],
    example: dict[str, Any],
    content_type: str = "application/json",
    override_description: str | None = None,
) -> ResponseDoc:
    status = _create_http_status_code(status_code=status_code)

    result = {
        "model": model,
        "description": override_description or status.description,
        "content": {
            content_type: {
                "example": example
            }
        },
    }

    if status_code == 204:
        result.pop("model")
        result.pop("content")

    return {
        status_code: result
    }


def make_standard_error_response(
    status_code: int,
    *,
    model: Type[BaseModel] | None = None,
    content_type: str = "application/json",
    example: dict[str, Any] | None = None,
    override_description: str | None = None,
    override_example: str | None = None
) -> ResponseDoc:
    """
    Gera uma resposta OpenAPI com modelo e exemplo opcional.
    """
    model = model or ErrorModel
    desc_error = override_example or "Error"
    example = example or ErrorModel(detail=desc_error).model_dump()
    return make_standard_response(
        status_code=status_code,
        model=model or ErrorModel,
        override_description=override_description,
        example=example,
        content_type=content_type
    )


def make_standard_success_response(
    status_code: int,
    model: Type[BaseModel],
    *,
    description: str | None = None,
    example: dict[str, Any] | None = None,
    content_type: str = "application/json"
) -> ResponseDoc:
    """
    Gera uma resposta OpenAPI com modelo e exemplo opcional.
    """
    example = example or {"foo": "bar"}
    return make_standard_response(
        status_code=status_code,
        model=model,
        override_description=description,
        example=example,
        content_type=content_type
    )
