def make_choices(items: tuple[str, ...]) -> list[tuple[str, str]]:
    """Make field required choices."""
    return [(item, item) for item in items]


def make_opt_choices(items: tuple[str, ...]) -> list[tuple[str, str]]:
    """Make field optional choices."""
    return [('', '')] + make_choices(items)
