import re


class StringTools:
    """
    String manipulation helpers.
    """

    @staticmethod
    def camel_to_snake(s: str):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

    @staticmethod
    def snake_to_camel(s: str):
        return "".join(word.title() for word in s.split("_"))
