from django.conf import settings
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import NumberParseException
from phonenumbers import PhoneNumberType
from phonenumbers import number_type
from rest_framework import serializers

from ..gettext_lazy import _

ACCEPTABLE_PHONE_PREFIXES = {
    40,  # Romania
}
NUMBER_TYPE_VALUES = PhoneNumberType.values()
NUMBER_TYPE_NAMES = {value: name for name, value in vars(PhoneNumberType).items() if value in NUMBER_TYPE_VALUES}


class PhoneNumberField(serializers.CharField):
    default_error_messages = {
        "invalid": _("Invalid phone number."),
        "failed_parse": _("Invalid phone number: {error}."),
        "wrong_type": _("Invalid phone number: type is {type}."),
        "invalid_choice": _("'{country_code}' is not an accepted code."),
    }

    def to_internal_value(self, data):
        phone_number: PhoneNumber | None = None
        try:
            phone_number = PhoneNumber.from_string(phone_number=data, region=settings.PHONENUMBER_DEFAULT_REGION)
        except NumberParseException as exc:
            if exc.error_type == NumberParseException.TOO_SHORT_NSN:
                self.fail("failed_parse", error=_("too short to be a phone number"))
            elif exc.error_type == NumberParseException.TOO_LONG:
                self.fail("failed_parse", error=_("too long to be a phone number"))
            else:
                self.fail("invalid")

        if phone_number and not phone_number.is_valid():
            self.fail("invalid")

        phone_number_type = number_type(phone_number)
        if phone_number_type not in (
            PhoneNumberType.MOBILE,
            PhoneNumberType.FIXED_LINE_OR_MOBILE,
            PhoneNumberType.PERSONAL_NUMBER,
            PhoneNumberType.UNKNOWN,
        ):
            self.fail("wrong_type", type=NUMBER_TYPE_NAMES[phone_number_type])

        if phone_number.country_code not in ACCEPTABLE_PHONE_PREFIXES:
            self.fail("invalid_choice", country_code=phone_number.country_code)
        return phone_number.as_e164
