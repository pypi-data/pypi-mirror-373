LOOKUP_EXPRESSION_MAPPING = {
    "exact": ("Equals", "="),
    "iexact": ("Equals (case-insensitive)", "≈"),
    "contains": ("Contains", "[=]"),
    "icontains": ("Contains (case-insensitive)", "[≈]"),
    "startswith": ("Starts with", "=]"),
    "istartswith": ("Starts with (case-insensitive)", "≈]"),
    "endswith": ("Ends with", "[="),
    "iendswith": ("Ends with (case-insensitive)", "[≈"),
    "regex": ("Regex", "r="),
    "iregex": ("Regex (case-insensitive)", "r≈"),
    "in": ("In", "∈"),
    "gte": ("Greater than or Equal", ">="),
    "lte": ("Less than or Equal", "<="),
    "gt": ("Greater than", ">"),
    "lt": ("Less than", "<"),
    "overlap": ("Overlaps", "="),
    "isnull": ("Is Null", "Is Null"),
}


ALL_TEXT_LOOKUPS = [
    "exact",
    "iexact",
    "contains",
    "icontains",
    "startswith",
    "istartswith",
    "endswith",
    "iendswith",
    "regex",
    "iregex",
]


def get_lookup_label(lookup_expr: str) -> str:
    return LOOKUP_EXPRESSION_MAPPING.get(lookup_expr, (lookup_expr, lookup_expr))[0]


def get_lookup_icon(lookup_expr: str) -> str:
    return LOOKUP_EXPRESSION_MAPPING.get(lookup_expr, (lookup_expr, lookup_expr))[1]
