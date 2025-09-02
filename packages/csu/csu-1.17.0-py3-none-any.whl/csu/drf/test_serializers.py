import pytest
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .serializers import AddErrorMixin


class SampleAddErrorMixin(AddErrorMixin, serializers.Serializer):
    foo = serializers.CharField(required=False)

    def validate(self, attrs):
        if "foo" in attrs:
            self.add_error("foo", "Foo is bad.")
            self.add_error("foo", "As I said, Foo is bad..")
        raise ValidationError({"foo": "Other stuff.", "bar": "More stuff."})


def test_add_error():
    serializer = SampleAddErrorMixin(data={"foo": 123})

    with pytest.raises(ValidationError) as exc:
        serializer.is_valid(raise_exception=True)
    assert exc.value.detail == {
        "foo": [
            "Foo is bad.",
            "As I said, Foo is bad..",
            "Other stuff.",
        ],
        "bar": ["More stuff."],
    }
