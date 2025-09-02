from . import SORT_CONFIG


def get_sort_key(key: str, sort_config: dict = SORT_CONFIG):
    """
    Parameters
    ----------
    key: string
        Dot separated key like `cycle.inputs.0.term.@id`.

    Returns
    -------
    list[string]
        Sorted key for use by Python's native sort functions.
    """
    top_node, *rest = key.split(".")
    keys = []
    node_type = top_node[0].upper() + top_node[1:]
    config = sort_config[node_type]
    keys.append(sort_config[node_type]["index"]["order"])
    for part in rest:
        if part in config:
            keys.append(config[part]["order"])
            config = sort_config.get(config[part]["type"], sort_config)
        else:
            # handle array indices up to 999999999999999
            # ensure term IDs are sorted after schema items
            keys.append(part.zfill(15) if part.isnumeric() else "a" + part)
    return keys
