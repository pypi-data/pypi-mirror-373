from datetime import date
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.validators import RegexValidator
from django.db.models import Choices
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.fields import ChoiceField
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import HyperlinkedRelatedField

from ..consts import CYRILLIC_CONVERSION_TABLE
from ..consts import NON_DIGIT_RE
from ..consts import NON_WORD_RE
from ..consts import REGISTRATION_NUMBER_RE
from ..consts import REGISTRATION_NUMBER_ROMANIAN_LEASE_RE
from ..consts import REGISTRATION_NUMBER_STRICT_RE
from ..consts import SPACES_RE
from ..gettext_lazy import _
from ..timezones import adjust_dt
from ..timezones import today


class AsciiCharField(CharField):
    default_error_messages = {
        **CharField.default_error_messages,
        "non_ascii": _("Ensure this field has only latin characters."),
    }
    # Allowed cyrillic characters
    cyrillic_conversion_table = CYRILLIC_CONVERSION_TABLE
    non_word_re = NON_WORD_RE
    spaces_re = SPACES_RE

    def __init__(self, *, uppercase=False, only_alphanumerics=False, normalize_spaces=True, translate_cyrillics=True, **kwargs):
        super().__init__(**kwargs)
        self.uppercase = uppercase
        self.translate_cyrillics = translate_cyrillics
        self.only_alphanumerics = only_alphanumerics
        self.normalize_spaces = normalize_spaces

    def to_internal_value(self, value):
        value: str = super().to_internal_value(value)
        if self.translate_cyrillics:
            value = value.translate(self.cyrillic_conversion_table)
        try:
            value.encode("ascii")
        except UnicodeEncodeError:
            self.fail("non_ascii")
        if self.only_alphanumerics:
            value = self.non_word_re.sub("", value)
        elif self.normalize_spaces:
            value = self.spaces_re.sub(" ", value)
        if self.uppercase:
            value = value.upper()
        return value


class DigitsCharField(AsciiCharField):
    default_error_messages = {
        **CharField.default_error_messages,
        "non_digit": _("Ensure this field has only digits."),
    }
    non_word_re = NON_DIGIT_RE

    def __init__(self, *, strip=True, **kwargs):
        super().__init__(**kwargs, only_alphanumerics=strip)

    def to_internal_value(self, value):
        value: str = super().to_internal_value(value)
        if not value.isdigit():
            self.fail("non_digit")
        return value


class RegistrationNumberField(AsciiCharField):
    def __init__(self, **kwargs):
        max_length = kwargs.pop("max_length", 12)
        super().__init__(
            **kwargs,
            max_length=max_length,
            only_alphanumerics=True,
            uppercase=True,
        )


class RomanianRegistrationNumberField(RegistrationNumberField):
    default_error_messages = {
        **RegistrationNumberField.default_error_messages,
        "expired": _("Leasing registration number is expired: {year}/{month} is less than {current_year}/{current_month}."),
        "year": _("Leasing registration number has invalid year: {year}."),
        "month": _("Leasing registration number has invalid month: {month}."),
        "expiry": _("Leasing registration number must  include expiry date (YY/MM)."),
        "no_q_letter": _("Cannot contain the letter Q."),
        "no_i_start_letter": _("Letters sequence cannot start with I."),
        "no_o_start_letter": _("Letters sequence cannot start with O."),
    }

    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            validators=[
                RegexValidator(
                    regex=REGISTRATION_NUMBER_RE["RO"],
                    message=_("Invalid registration number."),
                ),
                *(
                    RegexValidator(regex=regex, inverse_match=True, code=code, message=self.default_error_messages[code])
                    for code, regex in REGISTRATION_NUMBER_STRICT_RE.items()
                ),
            ],
        )

    def to_internal_value(self, value):
        value = super().to_internal_value(value)

        lease = REGISTRATION_NUMBER_ROMANIAN_LEASE_RE.match(value)
        if lease:
            if len(value) < 7:
                self.fail("expiry")

            current = today().replace(day=1)
            _, year, month = lease.groups()
            parsed_year = int(f"{current.year // 100}{year}")
            parsed_month = int(month)

            if parsed_year > current.year + 10 or parsed_year < current.year - 10:
                self.fail("year", year=year)

            if parsed_month > 12 or parsed_month < 1:
                self.fail("month", month=month)

            expiry_date = date(parsed_year, parsed_month, 1)
            if expiry_date < current:
                self.fail(
                    "expired",
                    year=parsed_year,
                    month=month,
                    current_year=current.year,
                    current_month=f"{current.month:02}",
                )

        return value


class ChassisNumberField(AsciiCharField):
    default_error_messages = {
        **AsciiCharField.default_error_messages,
        "length": _("Chassis number must have {required_length} characters ({length} given)."),
        "letter": _("Chassis number cannot contain the letter '{letter}'."),
    }
    default_invalid_conversion = {"O": "0", "Q": "0", "I": "1"}

    def __init__(self, required_length=17, invalid_conversion=None, normalize_invalid=True, reject_invalid=False, **kwargs):
        super().__init__(
            **kwargs,
            only_alphanumerics=True,
            uppercase=True,
        )
        self.invalid_conversion = invalid_conversion or self.default_invalid_conversion
        self.invalid_conversion_table = str.maketrans(self.invalid_conversion)
        self.required_length = required_length
        self.normalize_invalid = normalize_invalid
        self.reject_invalid = reject_invalid

    def to_internal_value(self, value):
        value = super().to_internal_value(value)
        if self.normalize_invalid:
            value = value.translate(self.invalid_conversion_table)
        length = len(value)
        if self.required_length and length != self.required_length:
            self.fail("length", length=length, required_length=self.required_length)
        if self.reject_invalid:
            for char in self.invalid_conversion:
                if char in value:
                    self.fail("letter", letter=char.lower())

        return value


class EnumField(ChoiceField):
    default_error_messages = {
        "invalid_choice": _("'{input}' is not a valid choice. Must be one of: {opts}."),
        "invalid_choice_multiple": _("'{input}' is not a valid choice. Must be one of: {opts} or {last_opt}."),
    }

    def __init__(self, *, enum: type[Choices], **kwargs):
        super().__init__(
            choices=[("", "-") if name == "__empty__" else (name, enum[name].label) for name in enum.names],
            **kwargs,
        )
        self.enum = enum

    def to_representation(self, value):
        return self.enum(value).name

    def to_internal_value(self, data):
        if data in self.enum.names:
            return self.enum[data]
        else:
            *opts, last_opt = self.enum
            opts = ", ".join(f"'{i.name}'" for i in opts)
            last_opt = f"'{last_opt.name}'"
            if opts:
                self.fail("invalid_choice_multiple", input=data, opts=opts, last_opt=last_opt)
            else:
                self.fail("invalid_choice", input=data, opts=last_opt)


class FormattedField(ReadOnlyField):
    format: str

    def __init__(self, *, format=None, **kwargs):
        self.format = format
        super().__init__(**kwargs, read_only=True)

    def to_representation(self, value):
        # noinspection StrFormat
        return self.format.format(value)


class DispatchingHyperlinkedRelatedField(HyperlinkedRelatedField):
    def __init__(self, *, dispatch_field, dispatch_mapping, **kwargs):
        kwargs["read_only"] = True
        kwargs["source"] = "*"
        super().__init__(lookup_field=dispatch_field, view_name=dispatch_mapping, **kwargs)

    def use_pk_only_optimization(self):
        return False

    def get_url(self, obj, view_name, request, format):
        dispatch_value = getattr(obj, self.lookup_field)
        view_options = view_name[dispatch_value]
        lookup_value = getattr(obj, view_options["lookup_field"])
        kwargs = {view_options["lookup_url_kwarg"]: lookup_value}
        return self.reverse(view_options["view_name"], kwargs=kwargs, request=request, format=format)


class LocalizedTimeField(serializers.DateTimeField):
    def __init__(self, *args, timezone: str | ZoneInfo = settings.TIME_ZONE, **kwargs):
        self.timezone = ZoneInfo(timezone) if isinstance(timezone, str) else timezone
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if value is None:
            return None

        localized_value = adjust_dt(value, tz=self.timezone)
        return localized_value.isoformat("T")


class PermissiveHyperlinkedRelatedField(serializers.HyperlinkedRelatedField):
    def to_internal_value(self, data):
        model = self.get_queryset().model
        if isinstance(data, model):
            return data
        else:
            return super().to_internal_value(data)
