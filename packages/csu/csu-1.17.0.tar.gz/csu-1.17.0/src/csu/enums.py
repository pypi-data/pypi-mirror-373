try:
    from django.db.models.enums import ChoicesType
except ImportError:
    from django.db.models.enums import ChoicesMeta as ChoicesType


def get_enum_name(value, enum_class: ChoicesType):
    if value is None or value not in enum_class.values:
        return repr(value)
    else:
        return enum_class(value).name
