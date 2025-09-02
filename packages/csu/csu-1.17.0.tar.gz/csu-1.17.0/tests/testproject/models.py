import pytest

pytest.importorskip("django")
from django.db import models

from csu.models import BaseModel


class MyBaseModel(BaseModel):
    foo = models.PositiveIntegerField()
