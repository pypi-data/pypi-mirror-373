class DictOps:
    """
    Dictionary helpers with nested access.
    """

    @staticmethod
    def deep_get(d: dict, path: str, default=None):
        keys = path.split(".")
        for key in keys:
            if isinstance(d, dict):
                d = d.get(key, default)
            else:
                return default
        return d

    @staticmethod
    def deep_set(d: dict, path: str, value):
        keys = path.split(".")
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
