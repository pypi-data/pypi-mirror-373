def lt(value: int) -> str:
    return _stringify("<", value)


def lte(value: int) -> str:
    return _stringify("<=", value)


def gt(value: int) -> str:
    return _stringify(">", value)


def gte(value: int) -> str:
    return _stringify(">=", value)


def default() -> str:
    return "default"


def _stringify(operator: str, value: int) -> str:
    return f"{operator}{value}"
