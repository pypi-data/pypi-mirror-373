import pytest
from django import forms
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .forms import formfield_for_drf_field


class WeirdField(serializers.CharField):
    def to_internal_value(self, data):
        if data == "x":
            raise ValidationError("x", code="foo")
        elif data == "abc":
            raise ValidationError(["a", "b", "c"], code="bar")
        else:
            return data


class WeirdFormField(forms.CharField):
    def to_python(self, data):
        data = super().to_python(data)
        if data == "x":
            raise forms.ValidationError("x", code="foo")
        elif data == "abc":
            raise forms.ValidationError(["a", "b", "c"], code="bar")
        else:
            return data


def test_weird_form_field():
    field = WeirdFormField()
    with pytest.raises(forms.ValidationError) as exc_info:
        field.clean("abc")
    assert exc_info.value.args == (["a", "b", "c"], "bar", None)
    with pytest.raises(forms.ValidationError) as exc_info:
        field.clean("x")
    assert exc_info.value.args == ("x", "foo", None)


def test_weird_field():
    field = formfield_for_drf_field(WeirdField())()
    with pytest.raises(forms.ValidationError) as exc_info:
        field.clean("abc")
    assert exc_info.value.args == (["a", "b", "c"], "bar", None)
    with pytest.raises(forms.ValidationError) as exc_info:
        field.clean("x")
    assert exc_info.value.args == ("x", "foo", None)


@pytest.mark.parametrize(
    "field",
    [
        WeirdFormField(required=False),
        formfield_for_drf_field(WeirdField, allow_blank=True)(required=False),
    ],
    ids=[
        "formfield",
        "formfield_for_drf_field",
    ],
)
def test_not_required(field):
    assert field.clean("") == ""
