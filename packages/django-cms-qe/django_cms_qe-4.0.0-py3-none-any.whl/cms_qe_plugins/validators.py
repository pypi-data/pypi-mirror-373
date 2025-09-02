from django.core.validators import RegexValidator, URLValidator, _lazy_re_compile
from django.utils.translation import gettext_lazy as _

path_validator = RegexValidator(
    _lazy_re_compile(r"^/\w+"),
    message=_("Enter a valid URL or path."),
    code="invalid",
)


def validate_url_or_path(value: str) -> None:
    """Validate URL or path."""
    if value[:1] == '/':
        return path_validator(value)
    return URLValidator()(value)
