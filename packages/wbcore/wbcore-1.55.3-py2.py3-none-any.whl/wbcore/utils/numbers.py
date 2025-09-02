powers = [10**x for x in (3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 100)]

human_powers = (
    ("Thousand", "Thousand"),
    ("Million", "Million"),
    ("Billion", "Billion"),
    ("Trillion", "Trillion"),
    ("Quadrillion", "Quadrillion"),
    ("Quintillion", "Quintillion"),
    ("Sextillion", "Sextillion"),
    ("Septillion", "Septillion"),
    ("Octillion", "Octillion"),
    ("Nonillion", "Nonillion"),
    ("Decillion", "Decillion"),
    ("Googol", "Googol"),
)


def intword(value, format=".1f"):
    """Converts a large integer to a friendly text representation.
    Works best for numbers over 1 million. For example, 1_000_000 becomes "1.0 million",
    1200000 becomes "1.2 million" and "1_200_000_000" becomes "1.2 billion". Supports up
    to decillion (33 digits) and googol (100 digits).
    Examples:
        ```pycon
        >>> intword("100")
        '100'
        >>> intword("12400")
        '12.4 thousand'
        >>> intword("1000000")
        '1.0 million'
        >>> intword(1_200_000_000)
        '1.2 billion'
        >>> intword(8100000000000000000000000000000000)
        '8.1 decillion'
        >>> intword(None) is None
        True
        >>> intword("1234000", "%0.3f")
        '1.234 million'
        ```
    Args:
        value (int, float, str): Integer to convert.
        format (str): To change the number of decimal or general format of the number
            portion.
    Returns:
        str: Friendly text representation as a string, unless the value passed could not
        be coaxed into an `int`.
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    output_format = format
    format = "%" + format

    if value < powers[0]:
        return str(value)
    for ordinal, power in enumerate(powers[1:], 1):
        if value < power:
            chopped = value / float(powers[ordinal - 1])
            if float(format % chopped) == float(10**3):
                chopped = value / float(powers[ordinal])
                singular, plural = human_powers[ordinal]
                return f"{chopped:{output_format}} {singular}"
            else:
                singular, plural = human_powers[ordinal - 1]
                return f"{chopped:{output_format}} {singular}"
    return str(value)
