import pytest

pytest.importorskip("django")

from django.db import connection
from django.test.utils import CaptureQueriesContext

from testproject.models import MyBaseModel


@pytest.mark.django_db
def test_basemodel_bad():
    t = MyBaseModel()
    t.update_fields(foo="bar")
    with pytest.raises(ValueError, match="Field 'foo' expected a number but got 'bar'."):
        t.update_fields_and_save(foo="bar")


@pytest.mark.django_db
def test_basemodel_insert():
    with CaptureQueriesContext(connection) as ctx:
        t = MyBaseModel()
        t.update_fields(foo="bar")
        t.update_fields_and_save(foo="123")
    assert len(ctx.captured_queries) == 1
    sql = ctx.captured_queries[0]["sql"]
    assert sql.startswith('INSERT INTO "testproject_mybasemodel" ("created_at", "modified_at", "foo") ')


@pytest.mark.django_db
def test_basemodel_update():
    t = MyBaseModel(foo="1")
    t.save()

    with CaptureQueriesContext(connection) as ctx:
        t.update_fields(foo="bar")
        t.update_fields_and_save(foo="123")
    assert len(ctx.captured_queries) == 1
    sql = ctx.captured_queries[0]["sql"]
    assert sql.startswith('UPDATE "testproject_mybasemodel" SET ')
    assert ' "modified_at" = \'' in sql
    assert ' "foo" = 123 ' in sql
