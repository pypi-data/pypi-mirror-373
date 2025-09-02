import pytest
from rest_framework.exceptions import ValidationError

phonenumber = pytest.importorskip(f"{__name__.rsplit('.', 1)[0]}.phonenumber")


@pytest.mark.parametrize(
    ("value", "error", "result"),
    [
        ("0723456789", None, "+40723456789"),
        ("0 7 2 3 4 5 6 7 8 9", None, "+40723456789"),
        ("0-7-2-3-4-5-6-7-8-9", None, "+40723456789"),
        ("0_7_2_3_4_5_6_7_8_9", "Invalid phone number.", None),
        ("0.7.2.3.4.5.6.7.8.9", None, "+40723456789"),
        ("(0.7.2.3).4.5.6.7.8.9", None, "+40723456789"),
        ("+40723456789", None, "+40723456789"),
        ("0040723456789", None, "+40723456789"),
        ("0264456789", "Invalid phone number: type is FIXED_LINE.", None),
        ("+40264456789", "Invalid phone number: type is FIXED_LINE.", None),
        ("+40364456789", "Invalid phone number: type is FIXED_LINE.", None),
        ("0040264456789", "Invalid phone number: type is FIXED_LINE.", None),
        ("0800 801 200", "Invalid phone number: type is TOLL_FREE.", None),
        ("0906760519", "Invalid phone number: type is PREMIUM_RATE.", None),
        ("0", "Invalid phone number.", None),
        ("1", "Invalid phone number.", None),
        ("11", "Invalid phone number.", None),
        ("111", "Invalid phone number.", None),
        ("111111111111111", "Invalid phone number.", None),
        ("11111111111111111111", "Invalid phone number: too long to be a phone number.", None),
        ("111111111111111111111111111111111", "Invalid phone number: too long to be a phone number.", None),
    ],
)
def test_phone_number_field(value, error, result):
    assert not (error and result)
    field = phonenumber.PhoneNumberField()
    if error:
        with pytest.raises(ValidationError) as exc_info:
            field.to_internal_value(value)

        (detail,) = exc_info.value.detail
        assert str(detail) == error
    else:
        assert field.to_internal_value(value) == result
