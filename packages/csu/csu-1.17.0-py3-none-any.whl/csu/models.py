from decimal import Decimal
from functools import cached_property

from django.db import models
from django.db.models import Field

from .gettext_lazy import _
from .timezones import cleanup_dt
from .timezones import now
from .utils import DOT01
from .utils import ONE00


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        auto_now_add=True,
        editable=False,
        db_index=True,
    )
    modified_at = models.DateTimeField(
        verbose_name=_("modified at"),
        auto_now=True,
        editable=False,
        db_index=True,
    )

    def update_fields(self, **kwargs):
        opts = self._meta
        for name, value in kwargs.items():
            field: Field = opts.get_field(name)
            field.save_form_data(self, value)

    def update_fields_and_save(self, **kwargs):
        self.update_fields(**kwargs)
        self.save(update_fields=("modified_at", *kwargs.keys()) if self.pk else None)


class AbstractStatusEnum(models.Choices):
    pending = object()
    confirmed = object()
    expired = object()
    cancelled = object()


class BaseStatusModel(BaseModel):
    class Meta:
        abstract = True

    status_enum_class: type[AbstractStatusEnum]
    status_confirm_time_limit_seconds: int

    status: models.Field

    confirmed_at = models.DateTimeField(
        verbose_name=_("confirmed at"),
        null=True,
        default=None,
        db_index=True,
        editable=False,
    )
    cancelled_at = models.DateTimeField(
        verbose_name=_("cancelled at"),
        null=True,
        default=None,
        db_index=True,
        editable=False,
    )

    def get_status(self):
        return self.status_enum_class(self.status).name

    def get_status_label(self):
        return self.status_enum_class(self.status).label

    @property
    def is_pending(self):
        return self.status == self.status_enum_class.pending

    @property
    def is_confirmed(self):
        return self.status == self.status_enum_class.confirmed

    @property
    def is_cancelled(self):
        return self.status == self.status_enum_class.cancelled

    def can_cancel(self):
        return not self.is_confirmed

    def can_confirm(self):
        if self.status == self.status_enum_class.expired:
            return False
        elif self.is_pending:
            current_dt = now()
            created_at = cleanup_dt(self.created_at)
            if current_dt.day != created_at.day:
                return False
            diff = (current_dt - created_at).total_seconds()
            return diff <= type(self).status_confirm_time_limit_seconds
        else:
            return True


class BasePriceModel(models.Model):
    class Meta:
        abstract = True

    price: Decimal = models.DecimalField(
        verbose_name=_("price"),
        max_digits=10,
        decimal_places=2,
    )
    vat_percentage: int = models.PositiveSmallIntegerField(
        verbose_name=_("vat"),
        help_text=_("The percentage of VAT."),
    )

    @cached_property
    def unit_price(self):
        return (self.price / (1 + self.vat_percentage / ONE00)).quantize(DOT01)

    @cached_property
    def vat_price(self):
        return self.price - self.unit_price
