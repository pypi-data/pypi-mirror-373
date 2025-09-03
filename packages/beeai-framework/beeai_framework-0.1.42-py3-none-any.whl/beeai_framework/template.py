# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar

import chevron
from pydantic import BaseModel, Field

from beeai_framework.errors import FrameworkError
from beeai_framework.utils.models import ModelLike, to_model_optional

T = TypeVar("T", bound=BaseModel)


class PromptTemplateInput(BaseModel, Generic[T]):
    input_schema: type[T] = Field(..., alias="schema")
    template: str
    functions: dict[str, Callable[[dict[str, Any]], str]] = {}
    defaults: dict[str, Any] = {}


class PromptTemplate(Generic[T]):
    def __init__(self, config: PromptTemplateInput[T]) -> None:
        self._config = config

    def render(self, template_input: ModelLike[T] | None = None, /, **kwargs: Any) -> str:
        input_model = to_model_optional(self._config.input_schema, template_input)
        data = input_model.model_dump() if input_model else kwargs

        if self._config.defaults:
            for key, value in self._config.defaults.items():
                if data.get(key) is None:
                    data.update({key: value})

        # Apply function derived data
        for key in self._config.functions:
            if key in data:
                raise PromptTemplateError(f"Function named '{key}' clashes with input data field!")
            data[key] = self._config.functions[key](data)

        return chevron.render(template=self._config.template, data=data)

    def fork(
        self, customizer: Callable[[PromptTemplateInput[Any]], PromptTemplateInput[Any]] | None
    ) -> "PromptTemplate[Any]":
        new_config = customizer(self._config) if customizer else self._config
        if not isinstance(new_config, PromptTemplateInput):
            raise ValueError("Return type from customizer must be a PromptTemplateInput or nothing.")
        return PromptTemplate(new_config)

    def update(
        self,
        *,
        functions: dict[str, Callable[[dict[str, Any]], str]] | None = None,
        defaults: dict[str, Any] | None = None,
    ) -> Self:
        self._config.functions.update(functions or {})
        self._config.defaults.update(defaults or {})
        return self


class PromptTemplateError(FrameworkError):
    """Raised for errors caused by PromptTemplate."""

    def __init__(
        self,
        message: str = "PromptTemplate error",
        *,
        cause: Exception | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, is_fatal=True, is_retryable=False, cause=cause, context=context)


__all__ = ["PromptTemplate", "PromptTemplateError", "PromptTemplateInput"]
