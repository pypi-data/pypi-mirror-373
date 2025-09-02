from collections import defaultdict
from functools import cached_property

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.fields import BooleanField
from rest_framework.fields import Field
from rest_framework.serializers import Serializer
from rest_framework.serializers import as_serializer_error
from rest_framework.utils.serializer_helpers import ReturnDict

from ..gettext_lazy import _
from ..models import BasePriceModel
from ..models import BaseStatusModel
from ..service import HTTPService


class ServiceSerializerMixin:
    context: dict

    @cached_property
    def service_instance(self) -> HTTPService:
        return self.context["service_instance"]


class AddErrorMixin:
    errors: ReturnDict
    _stored_errors: dict

    def add_error(self, field_name: str, message: str):
        self.merge_errors({field_name: str(message)})

    def merge_errors(self, errors: dict[str, list[str] | str]):
        for field, messages in errors.items():
            if isinstance(messages, list | tuple):
                self._stored_errors[field].extend(messages)
            else:
                self._stored_errors[field].append(messages)

    def run_validation(self, data):
        self._stored_errors = defaultdict(list)
        try:
            return super().run_validation(data)
        except (ValidationError, DjangoValidationError) as exc:
            self.merge_errors(as_serializer_error(exc))
            raise ValidationError(self._stored_errors) from exc
        finally:
            if self._stored_errors:
                raise ValidationError(self._stored_errors)


class RejectUnexpectedWritableMixin:
    _declared_fields: dict[str, Field]

    def __init_subclass__(cls, **kwargs):
        if not hasattr(getattr(cls, "Meta", None), "expected_writable_fields"):
            raise TypeError("Must define 'expected_writable_fields' in serializer Meta.")

        expected = cls.Meta.expected_writable_fields = set(cls.Meta.expected_writable_fields)
        actual = {name for name, field in cls._declared_fields.items() if not field.read_only}
        unexpected = actual - expected
        if unexpected:
            raise TypeError(f"Misconfigured serializer fields. Unexpected writable fields: {', '.join(unexpected)}")

    def reject_unknown(self, attrs: dict | None):
        if attrs:
            unknown_fields = set(attrs) - self.Meta.expected_writable_fields
            if unknown_fields:
                raise ValidationError({field: [_("This field is unexpected.")] for field in unknown_fields})


class ConfirmSerializer(Serializer):
    instance: BaseStatusModel | BasePriceModel

    confirm = BooleanField(required=True, initial=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        if kwargs.get("partial"):
            raise TypeError("Cannot accept a true value for 'partial'")
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        raise TypeError("This serializer can only confirm!")

    @staticmethod
    def validate_confirm(value):
        if not value:
            raise ValidationError(_("Must have a true value."))
        return value

    def validate(self, data):
        if not self.instance.can_confirm():
            raise ValidationError(_("Confirm time limit expired."))
        return super().validate(data)


class CancelSerializer(Serializer):
    instance: BaseStatusModel | BasePriceModel

    cancel_error = _("Cannot cancel.")
    cancel = BooleanField(required=True, initial=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        if kwargs.get("partial"):
            raise TypeError("Cannot accept a true value for 'partial'")
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        raise TypeError("This serializer can only cancel!")

    @staticmethod
    def validate_cancel(value):
        if not value:
            raise ValidationError(_("Must have a true value."))
        return value

    def validate(self, data):
        if not self.instance.can_cancel():
            raise ValidationError(self.cancel_error)

        return super().validate(data)
