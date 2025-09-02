import zoneinfo
from abc import ABCMeta
from abc import abstractmethod
from datetime import date
from datetime import datetime
from decimal import Decimal

import pytest
from django.core.serializers.json import DjangoJSONEncoder

from .service import HTTPServiceResponse
from .utils import cached_classproperty
from .utils import convert_with_json_encoder
from .utils import lazy_import_classproperty
from .utils import singleton_memoize


def test_singleton_memoize():
    pytest.raises(TypeError, singleton_memoize, lambda a: 123)
    a = []

    @singleton_memoize
    def stuff1(x=2) -> str:
        a.append(1)
        return "abc"

    assert a == []
    assert stuff1() == "abc"
    assert stuff1() == "abc"
    assert a == [1]

    b = []

    @singleton_memoize
    def stuff2():
        b.append(1)
        return "bce"

    assert b == []
    assert stuff2() == "bce"
    assert stuff2() == "bce"
    assert b == [1]


def test_singleton_property():
    c = []

    class Stuff3:
        @singleton_memoize
        @staticmethod
        def stuff():
            c.append(1)
            return "asd"

    assert c == []
    assert Stuff3().stuff() == "asd"
    assert Stuff3().stuff() == "asd"
    assert c == [1]

    d = []

    class Stuff4:
        @singleton_memoize
        @staticmethod
        def stuff():
            d.append(1)
            return "qwe"

    assert d == []
    assert Stuff4().stuff() == "qwe"
    assert Stuff4().stuff() == "qwe"
    assert d == [1]


def test_lazy_import_classproperty():
    class Stuff:
        abs_foo = lazy_import_classproperty("csu.service.HTTPServiceResponse")
        rel_foo = lazy_import_classproperty(".service.HTTPServiceResponse", __name__)

    s = Stuff()
    assert s.abs_foo is HTTPServiceResponse
    assert s.rel_foo is HTTPServiceResponse

    assert s.abs_foo is HTTPServiceResponse
    assert s.rel_foo is HTTPServiceResponse

    assert Stuff.abs_foo is HTTPServiceResponse
    assert Stuff.rel_foo is HTTPServiceResponse


def test_lazy_import_classproperty_cls():
    class Stuff:
        foo = lazy_import_classproperty("csu.service.HTTPServiceResponse")

    assert Stuff.foo is HTTPServiceResponse
    assert Stuff.foo is HTTPServiceResponse


def test_lazy_import_classproperty_is_lazy():
    class Base(metaclass=ABCMeta):
        @property
        @abstractmethod
        def foo(self):
            pass

    class Stuff(Base):
        foo = lazy_import_classproperty("csu.service.borken_doesnt_exist", abc=True)

    Stuff()


def test_cached_classproperty_abc():
    counter = []

    class Base(metaclass=ABCMeta):
        @property
        @abstractmethod
        def foo(self): ...

    property_instance = cached_classproperty(abc=True)

    class Stuff(Base):
        @property_instance
        def foo(cls):
            counter.append(cls.__name__)
            return len(counter)

    class AnotherStuff(Stuff): ...

    assert Stuff().foo == 1
    assert Stuff().foo == 1
    assert Stuff.foo is property_instance
    assert AnotherStuff.foo is property_instance
    assert AnotherStuff().foo == 2
    assert AnotherStuff().foo == 2
    assert counter == [
        "Stuff",
        "AnotherStuff",
    ]
    assert AnotherStuff.__dict__.get("foo", "missing") == "missing"
    assert Stuff.__dict__.get("foo", "missing") is property_instance
    assert AnotherStuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert AnotherStuff.__dict__.get("__Stuff_foo", "missing") == 2
    assert Stuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert Stuff.__dict__.get("__Stuff_foo", "missing") == 1


def test_cached_classproperty_abc_static():
    counter = []

    class Base(metaclass=ABCMeta):
        @property
        @abstractmethod
        def foo(self): ...

    class Stuff(Base):
        @cached_classproperty(abc=True, static=True)
        def foo(cls):
            counter.append(cls.__name__)
            return len(counter)

    class AnotherStuff(Stuff): ...

    assert AnotherStuff().foo == 1
    assert AnotherStuff().foo == 1
    assert Stuff().foo == 1
    assert Stuff().foo == 1
    assert counter == [
        "Stuff",
    ]
    assert AnotherStuff.__dict__.get("foo", "missing") == "missing"
    assert Stuff.__dict__.get("foo", "missing") == 1
    assert AnotherStuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert Stuff.__dict__.get("__Stuff_foo", "missing") == "missing"


def test_cached_classproperty():
    counter = []

    class CustomType:
        def example(self): ...

    class Base:
        @property
        @abstractmethod
        def foo(self): ...

    @cached_classproperty
    def property_instance(cls):
        counter.append(cls.__name__)
        return len(counter)

    class Stuff(Base):
        foo: CustomType
        foo = property_instance

    class AnotherStuff(Stuff): ...

    assert Stuff.foo == 1
    assert Stuff().foo == 1
    assert AnotherStuff.foo == 2
    assert AnotherStuff().foo == 2
    assert counter == [
        "Stuff",
        "AnotherStuff",
    ]
    assert AnotherStuff.__dict__.get("foo", "missing") == "missing"
    assert Stuff.__dict__.get("foo", "missing") is property_instance
    assert AnotherStuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert AnotherStuff.__dict__.get("__Stuff_foo", "missing") == 2
    assert Stuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert Stuff.__dict__.get("__Stuff_foo", "missing") == 1


def test_cached_classproperty_reversed():
    counter = []

    class CustomType:
        def example(self): ...

    class Base:
        @property
        @abstractmethod
        def foo(self): ...

    @cached_classproperty
    def property_instance(cls):
        counter.append(cls.__name__)
        return len(counter)

    class Stuff(Base):
        foo: CustomType
        foo = property_instance

    class AnotherStuff(Stuff): ...

    assert AnotherStuff.foo == 1
    assert AnotherStuff().foo == 1
    assert Stuff.foo == 2
    assert Stuff().foo == 2
    assert counter == [
        "AnotherStuff",
        "Stuff",
    ]
    assert AnotherStuff.__dict__.get("foo", "missing") == "missing"
    assert Stuff.__dict__.get("foo", "missing") is property_instance
    assert AnotherStuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert AnotherStuff.__dict__.get("__Stuff_foo", "missing") == 1
    assert Stuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert Stuff.__dict__.get("__Stuff_foo", "missing") == 2


def test_cached_classproperty_override():
    counter = []

    class CustomType:
        def example(self): ...

    class Base:
        @property
        @abstractmethod
        def foo(self): ...

    @cached_classproperty
    def property_instance(cls):
        counter.append(cls.__name__)
        return len(counter)

    class Stuff(Base):
        foo: CustomType
        foo = property_instance

    class AnotherStuff(Stuff):
        @cached_classproperty
        def foo(cls):
            value = super().foo
            counter.append(f"subclass:{cls.__name__}:{value}")
            return len(counter)

        foo.flag = "override"

    assert AnotherStuff.foo == 2
    assert AnotherStuff().foo == 2
    assert Stuff.foo == 3
    assert Stuff().foo == 3
    assert AnotherStuff.foo == 2
    assert AnotherStuff().foo == 2
    assert Stuff.foo == 3
    assert Stuff().foo == 3
    assert counter == [
        "AnotherStuff",
        "subclass:AnotherStuff:1",
        "Stuff",
    ]
    assert AnotherStuff.__dict__.get("foo", "missing").flag == "override"
    assert Stuff.__dict__.get("foo", "missing") is property_instance
    assert AnotherStuff.__dict__.get("__AnotherStuff_foo", "missing") == 2
    assert AnotherStuff.__dict__.get("__Stuff_foo", "missing") == 1
    assert Stuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert Stuff.__dict__.get("__Stuff_foo", "missing") == 3


def test_cached_classproperty_static():
    counter = []

    class Base:
        @property
        def foo(self):
            raise NotImplementedError

    class Stuff(Base):
        @cached_classproperty(static=True)
        def foo(cls):
            counter.append(cls.__name__)
            return len(counter)

    class AnotherStuff(Stuff): ...

    assert AnotherStuff.foo == 1
    assert AnotherStuff().foo == 1
    assert Stuff.foo == 1
    assert Stuff().foo == 1
    assert counter == [
        "Stuff",
    ]
    assert AnotherStuff.__dict__.get("foo", "missing") == "missing"
    assert Stuff.__dict__.get("foo", "missing") == 1
    assert AnotherStuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert AnotherStuff.__dict__.get("__Stuff_foo", "missing") == "missing"
    assert Stuff.__dict__.get("__AnotherStuff_foo", "missing") == "missing"
    assert Stuff.__dict__.get("__Stuff_foo", "missing") == "missing"


def test_cached_classproperty_simple():
    counter = []

    class Stuff:
        @cached_classproperty
        def foo(cls):
            counter.append(f"foo:{cls.__name__}")
            return len(counter)

        @cached_classproperty(static=True)
        def bar(cls):
            counter.append(f"bar:{cls.__name__}")
            return len(counter)

    assert Stuff.foo == 1
    assert Stuff().foo == 1
    assert Stuff.bar == 2
    assert Stuff().bar == 2
    assert counter == [
        "foo:Stuff",
        "bar:Stuff",
    ]
    assert isinstance(Stuff.__dict__.get("foo", "missing"), cached_classproperty)
    assert Stuff.__dict__.get("bar", "missing") == 2
    assert Stuff.__dict__.get("__Stuff_foo", "missing") == 1
    assert Stuff.__dict__.get("__Stuff_bar", "missing") == "missing"


@pytest.mark.parametrize(
    ("input", "output"),
    [
        ({"foo": "bar"}, {"foo": "bar"}),
        (["foo", "bar"], ["foo", "bar"]),
        ({"foo"}, ["foo"]),
        (("foo", "bar"), ["foo", "bar"]),
        ("foo", "foo"),
        (1, 1),
        (1.2, 1.2),
        (Decimal(1), "1"),
        (date(2000, 1, 1), "2000-01-01"),
        (datetime(2000, 1, 1), "2000-01-01T00:00:00"),  # noqa:DTZ001
        (datetime(2000, 1, 1, tzinfo=zoneinfo.ZoneInfo("Europe/Bucharest")), "2000-01-01T00:00:00+02:00"),
        (
            {
                "dec": ["1"],
                "date": {date(2000, 1, 1)},
                "dt": (datetime(2000, 1, 1),),  # noqa:DTZ001
                "none": None,
            },
            {
                "dec": ["1"],
                "date": ["2000-01-01"],
                "dt": ["2000-01-01T00:00:00"],
                "none": None,
            },
        ),
    ],
)
def test_convert_with_json_encoder(input, output):
    assert convert_with_json_encoder(DjangoJSONEncoder(), input) == output
