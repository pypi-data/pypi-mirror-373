import json


class JSONX:
    """
    Extended JSON utilities.
    """

    @staticmethod
    def dumps(obj, indent=2):
        return json.dumps(obj, indent=indent, ensure_ascii=False)

    @staticmethod
    def loads(s: str):
        return json.loads(s)

    @staticmethod
    def safe_load(s: str, default=None):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return default
