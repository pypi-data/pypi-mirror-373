from datetime import date
from datetime import datetime

from django.contrib.admin import DateFieldListFilter
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Choices
from django.db.models import Lookup
from django.db.models.expressions import Col
from django.db.models.lookups import Exact
from django.db.models.sql import AND
from django.utils.encoding import force_str
from django.utils.tree import Node
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import Widget
from rest_framework import serializers

from .timezones import today


class PastDateListFilter(DateFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.links = [
            (label, {self.lookup_kwarg_until: filters[self.lookup_kwarg_since]} if self.lookup_kwarg_until in filters else filters)
            for label, filters in self.links
        ]


def repr_expr(obj):
    if isinstance(obj, Exact):
        return f"{repr_expr(obj.lhs)}={repr_expr(obj.rhs)}"
    elif isinstance(obj, Lookup):
        return f"{repr_expr(obj.lhs)}__{obj.lookup_name}={repr_expr(obj.rhs)}"
    elif isinstance(obj, Col):
        return obj.target.column
    elif isinstance(obj, Node):
        if obj.connector == AND:
            return "-".join(map(repr_expr, obj.children))
        else:
            return "-OR-".join(map(repr_expr, obj.children))
    elif isinstance(obj, datetime | date):
        return obj.isoformat()
    else:
        return str(obj)


class FullFilenameExportAdminMixin:
    model: models.Model

    def get_export_filename(self, request, queryset: models.QuerySet, file_format):
        filters = repr_expr(queryset.query.where)
        filename = "{}-{}-{}-{}.{}".format(
            self.model._meta.app_label,
            self.model._meta.verbose_name_plural.replace(" ", "-").replace("/", "-"),
            today().isoformat(),
            filters or "all",
            file_format.get_extension(),
        )
        return filename


class ChoiceWidget(Widget):
    def __init__(self, choice_class: type[Choices], **kwargs):
        super().__init__(**kwargs)
        self.choice_class = choice_class

    def render(self, value, obj=None, **kwargs):
        if value in self.choice_class:
            return self.choice_class(value).name
        else:
            return value

    def clean(self, value, row=None, **kwargs):
        if value in self.choice_class:
            return self.choice_class[value]


class SmartField(Field):
    def clean(self, data, **kwargs):
        """
        Perform exception wrapping early here (instead of letting import_obj do it).
        Apparently that behavior is completely missing from (for import_id_fields).
        """
        try:
            return super().clean(data, **kwargs)
        except ValueError as e:
            raise ValidationError({self.attribute: force_str(e)}, code="invalid") from e


def widget_passthrough(widget_instance):
    def widget_trampoline(key_is_id=None, **kwargs):
        assert not kwargs, f"no widget kwargs are allowed but we got: {kwargs!r}"
        return widget_instance

    return widget_trampoline


def widget_for_drf_field(drf_field: serializers.Field):
    class WidgetWrapper(Widget):
        def clean(self, value, row=None, **kwargs):
            try:
                return drf_field.run_validation(value)
            except serializers.ValidationError as exc:
                raise ValueError(*map(str, exc.detail)) from None

    return WidgetWrapper()


class SmartModelResource(ModelResource):
    DEFAULT_RESOURCE_FIELD = SmartField

    @classmethod
    def widget_kwargs_for_field(cls, *args):
        return {}

    @classmethod
    def widget_from_django_field(cls, f: models.Field, *args, **kwargs):
        name = f.name
        widgets = cls._meta.widgets or ()
        if name in widgets:
            return widget_passthrough(widgets[name])
        else:
            return widget_passthrough(super().widget_from_django_field(f, *args, **kwargs)())
