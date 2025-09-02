def _(message: str) -> str:
    raise NotImplementedError


from django.utils.translation import gettext_lazy as _  # noqa: E402

__all__ = [
    "_",
]
