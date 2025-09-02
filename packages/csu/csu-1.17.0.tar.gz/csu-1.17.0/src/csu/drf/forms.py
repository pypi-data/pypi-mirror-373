from collections.abc import Callable
from typing import NotRequired
from typing import Protocol
from typing import TypedDict
from typing import Unpack

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.forms import CharField
from django.forms import Widget
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.fields import Field


class _USUAL_DRF_FIELD_KWARGS(TypedDict):
    read_only: NotRequired[bool]
    write_only: NotRequired[bool]
    required: NotRequired[bool | None]
    default: NotRequired[object]
    initial: NotRequired[object]
    source: NotRequired[str]
    label: NotRequired[str]
    help_text: NotRequired[str]
    style: NotRequired[str]
    error_messages: NotRequired[dict[str, str]]
    validators: NotRequired[list[Callable]]
    allow_null: NotRequired[bool]


class _USUAL_DJ_FIELD_KWARGS(TypedDict):
    disabled: NotRequired[bool]
    empty_value: NotRequired[object]
    error_messages: NotRequired[dict[str, str]]
    help_text: NotRequired[str]
    initial: NotRequired[str]
    label: NotRequired[str]
    label_suffix: NotRequired[str]
    localize: NotRequired[bool]
    max_length: NotRequired[int]
    min_length: NotRequired[int]
    required: NotRequired[bool]
    show_hidden_initial: NotRequired[bool]
    strip: NotRequired[bool]
    template_name: NotRequired[str]
    validators: NotRequired[list[BaseValidator]]
    widget: NotRequired[Widget]


class _USUAL_DJ_FIELD_PROTO(Protocol):
    def __call__(self, **kwargs: Unpack[_USUAL_DJ_FIELD_KWARGS]):
        pass


def formfield_for_drf_field(
    drf_field: type[Field] | Field,
    /,
    *,
    formfield_class: type[forms.Field] = CharField,
    **drf_field_kwargs: Unpack[_USUAL_DRF_FIELD_KWARGS],
) -> _USUAL_DJ_FIELD_PROTO:
    if isinstance(drf_field, type) and issubclass(drf_field, Field):
        drf_field = drf_field(**drf_field_kwargs)

    class FormFieldWrapper(formfield_class):
        def to_python(self, value):
            value = super().to_python(value)
            try:
                return drf_field.run_validation(value)
            except DRFValidationError as exc:
                detail = exc.detail
                if isinstance(detail, list):
                    if len(detail) == 1:
                        (detail,) = detail
                        raise ValidationError(str(detail), detail.code) from exc
                    else:
                        code = {err.code for err in detail}
                        if len(code) == 1:
                            (code,) = code
                        else:
                            code = None
                        raise ValidationError([str(err) for err in detail], code) from exc
                else:
                    raise ValidationError(exc.detail) from exc

    return FormFieldWrapper
