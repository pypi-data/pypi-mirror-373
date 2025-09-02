def prefix_key(key: str, prefix: str | None = None) -> str:
    if prefix:
        return prefix + "_" + key
    return key
