from crispy_forms.layout import HTML
from crispy_forms.layout import Field
from crispy_forms.layout import Fieldset


class SimpleFieldset(Fieldset):
    @staticmethod
    def get_css_id(fields):
        parts = []
        for field in fields:
            if isinstance(field, Field):
                parts.extend(field.fields)
            elif isinstance(field, str):
                parts.append(field)
        return "_".join(parts)

    def __init__(self, title, *fields, extra=""):
        super().__init__(
            f"""<h4>{title}</h4>""",
            *fields,
            HTML(extra),
            css_id=f"{self.get_css_id(fields)}_fieldset",
        )


class CollapsibleFieldset(SimpleFieldset):
    def __init__(self, title, *fields):
        super().__init__(
            title,
            *fields,
            extra='<a class="form-control form-group collapsible"><span class="flex">'
            '<span class="value"></span>'
            '<span class="pen">🖊️</span>'
            "</span></a>",
        )
