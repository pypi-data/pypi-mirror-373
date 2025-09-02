WHITELISTED_METHODS = {
    list: {
        "append",
        "clear",
        "copy",
        "count",
        "extend",
        "index",
        "insert",
        "pop",
        "remove",
        "reverse",
        "sort",
    },
    dict: {
        "clear",
        "copy",
        "get",
        "items",
        "keys",
        "pop",
        "setdefault",
        "update",
        "values",
    },
    set: {"add", "clear", "copy", "discard", "pop", "remove", "update"},
    str: {
        "upper",
        "lower",
        "strip",
        "split",
        "splitlines",
        "rsplit",
        "replace",
        "startswith",
        "endswith",
        "join",
        "encode",
        "count",
    },
    bytes: {"decode"},
    bytearray: {"decode"},
}

# Methods that return iterators/views and need to be materialized
MATERIALIZE_METHODS = {
    dict: {"keys": list, "values": list, "items": list},
}
